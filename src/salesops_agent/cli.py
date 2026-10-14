import argparse


def main():
    parser = argparse.ArgumentParser(description="UdaCenture SalesOps Agent")
    parser.add_argument("--version", action="version", version="salesops-agent 0.1.0")
    parser.parse_args()
    parser.print_help()
