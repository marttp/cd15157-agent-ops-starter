"""Bounded CRM expression interpreter. No Python evaluation or execution."""
import ast
import json
import multiprocessing
import time

from .data_access import FIELDS

OPERATIONS = {"count", "sum", "average", "group_sum", "filter_eq"}


def validate_code(source):
    if len(source) > 4096:
        raise ValueError("source_size_limit")
    tree = ast.parse(source, mode="eval")
    nodes = list(ast.walk(tree))
    if len(nodes) > 256:
        raise ValueError("ast_size_limit")
    for node in nodes:
        if not isinstance(node, (ast.Expression, ast.Call, ast.Name, ast.Load, ast.Constant)):
            raise ValueError("unsafe_syntax")
        if isinstance(node, ast.Call) and (not isinstance(node.func, ast.Name) or node.func.id not in OPERATIONS or node.keywords):
            raise ValueError("unsafe_capability")
        if isinstance(node, ast.Name) and node.id not in OPERATIONS | set(FIELDS):
            raise ValueError("restricted_dataset_or_name")
    return tree.body


def interpret(node, tables, budget):
    if isinstance(node, ast.Name) and node.id in tables:
        return tables[node.id]
    if isinstance(node, ast.Constant) and isinstance(node.value, (str, int, float, bool, type(None))):
        return node.value
    if not isinstance(node, ast.Call):
        raise ValueError("invalid_expression")
    name = node.func.id
    args = [interpret(child, tables, budget) for child in node.args]
    arity = {"count": 1, "sum": 2, "average": 2, "group_sum": 3, "filter_eq": 3}
    if len(args) != arity[name] or not isinstance(args[0], list):
        raise ValueError("invalid_analysis_arguments")
    rows = args[0]
    budget[0] -= len(rows) + 1
    if budget[0] < 0:
        raise ValueError("operation_limit")
    if name == "count":
        return len(rows)
    fields = args[1:3] if name == "group_sum" else args[1:2]
    if any(not isinstance(field, str) or field not in set().union(*(set(r) for r in rows)) for field in fields):
        raise ValueError("restricted_field")
    if name == "filter_eq":
        return [r for r in rows if r.get(args[1]) == args[2]]
    if name == "group_sum":
        result = {}
        for row in rows:
            value = row.get(args[2])
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError("numeric_field_required")
            key = str(row.get(args[1]))
            result[key] = result.get(key, 0) + value
        return result
    values = [r.get(args[1]) for r in rows]
    if any(not isinstance(v, (int, float)) or isinstance(v, bool) for v in values):
        raise ValueError("numeric_field_required")
    return sum(values) if name == "sum" else sum(values)/len(values) if values else None


def worker(source, serialized, connection):
    try:
        tables = json.loads(serialized)
        result = interpret(validate_code(source), tables, [100000])
        encoded = json.dumps(result, allow_nan=False)
        if len(encoded) > 65536:
            raise ValueError("output_size_limit")
        connection.send({"status": "success", "data": result})
    except (ValueError, SyntaxError, TypeError, KeyError) as error:
        connection.send({"status": "blocked", "reason": str(error) if isinstance(error, ValueError) else "invalid_expression"})
    finally:
        connection.close()


def run_sandboxed(source, tables, timeout=2):
    try:
        validate_code(source)
        if set(tables) - set(FIELDS):
            raise ValueError("restricted_dataset")
        projected = {name: [{k: v for k, v in row.items() if k in FIELDS[name].split()} for row in rows] for name, rows in tables.items()}
        if sum(len(rows) for rows in projected.values()) > 10000:
            raise ValueError("row_limit")
        serialized = json.dumps(projected, allow_nan=False)
        if len(serialized) > 2000000:
            raise ValueError("input_size_limit")
    except (ValueError, SyntaxError, TypeError):
        return {"status": "blocked", "reason": "unsafe_analysis_request"}
    context = multiprocessing.get_context("spawn")
    parent, child = context.Pipe(duplex=False)
    process = context.Process(target=worker, args=(source, serialized, child))
    started = time.monotonic()
    process.start()
    child.close()
    try:
        remaining = timeout - (time.monotonic() - started)
        if remaining <= 0 or not parent.poll(remaining):
            return {"status": "blocked", "reason": "execution_timeout"}
        return parent.recv()
    except EOFError:
        return {"status": "failed", "reason": "analysis_worker_failed"}
    finally:
        parent.close()
        if process.is_alive():
            process.terminate()
        process.join(timeout=1)
        if process.is_alive():
            process.kill()
            process.join()
