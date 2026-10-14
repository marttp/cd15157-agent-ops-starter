import argparse
import json
from .agent import run_agent


def main():
    parser = argparse.ArgumentParser(description="UdaCenture SalesOps Agent")
    parser.add_argument("--version", action="version", version="salesops-agent 0.1.0")
    sub = parser.add_subparsers(dest="command", required=True)
    ask = sub.add_parser("ask")
    ask.add_argument("question")
    ask.add_argument("--config")
    ask.add_argument("--output")
    ask.add_argument("--approval", choices=["approve", "reject"])
    args = parser.parse_args()
    result = run_agent(args.question, args.config, args.output, approval=args.approval)
    print(json.dumps({k: result[k] for k in ["run_id", "status", "answer"]}, indent=2))
    raise SystemExit(1 if result["status"] == "failed" else 0)
