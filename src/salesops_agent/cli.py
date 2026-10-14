import argparse
import getpass
import json
import os
from pathlib import Path

from .agent import run_agent
from .config import load_settings
from .state import StateStore


def main():
    parser = argparse.ArgumentParser(description="UdaCenture SalesOps Agent")
    parser.add_argument("--version", action="version", version="salesops-agent 0.1.0")
    sub = parser.add_subparsers(dest="command", required=True)
    ask = sub.add_parser("ask")
    ask.add_argument("question")
    ask.add_argument("--config")
    ask.add_argument("--approval", choices=["approve", "reject"])
    ask.add_argument("--session")
    create = sub.add_parser("create-user")
    create.add_argument("--user", required=True)
    sub.add_parser("create-session")
    sub.add_parser("sessions")
    replay = sub.add_parser("replay")
    replay.add_argument("run_id")
    for command in [ask, create, sub.choices["create-session"], sub.choices["sessions"], replay]:
        command.add_argument("--output")
        if command is not create:
            command.add_argument("--user")
    args = parser.parse_args()
    cfg, root = load_settings(getattr(args, "config", None))
    output = Path(args.output or root / cfg.output_dir)
    principal = None
    if args.command != "ask" or args.user:
        store = StateStore(output / "state/history.db")
        password = os.getenv("SALESOPS_PASSWORD") or getpass.getpass("Local password: ")
        if args.command == "create-user":
            store.create_user(args.user, password)
            print("Local user created.")
            return
        if not args.user:
            parser.error("--user is required for authenticated session commands")
        principal = store.authenticate(args.user, password)
    if args.command == "ask":
        if args.session and principal is None:
            parser.error("--session requires authenticated --user")
        result = run_agent(
            args.question,
            args.config,
            output,
            approval=args.approval,
            principal=principal,
            session_id=args.session,
        )
        print(json.dumps({k: result[k] for k in ["run_id", "status", "answer"]}, indent=2))
        raise SystemExit(1 if result["status"] == "failed" else 0)
    if args.command == "create-session":
        result = store.create_session(principal)
    elif args.command == "sessions":
        result = store.sessions(principal)
    else:
        result = store.replay(principal, args.run_id)
    print(json.dumps(result, indent=2))
