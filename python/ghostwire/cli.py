"""
CLI module for GhostWire Refractory
"""

import argparse
import sys

from .config.settings import settings


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="ghostwire",
        description="GhostWire Refractory - Neural network-based chat system with memory",
    )

    parser.add_argument(
        "command",
        nargs="?",
        default="serve",
        choices=["serve", "benchmark", "orchestrate"],
        help="Command to execute (default: serve)",
    )

    # Serve command arguments
    parser.add_argument(
        "--host", default=settings.HOST, help="Host to bind the server to"
    )

    parser.add_argument(
        "--port", type=int, default=settings.PORT, help="Port to bind the server to"
    )

    parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload on code changes"
    )

    # Orchestrator command arguments
    parser.add_argument(
        "--request", type=str, help="User request to process through orchestrator"
    )

    args = parser.parse_args()

    if args.command == "serve":
        from .main import create_app, start_server

        app = create_app()
        start_server(app, host=args.host, port=args.port, reload=args.reload)
    elif args.command == "benchmark":
        from .cli.benchmark_cli import main as benchmark_main

        sys.exit(benchmark_main())
    elif args.command == "orchestrate":
        if not args.request:
            print("Error: --request is required for orchestrate command")
            sys.exit(1)

        # Import and run orchestrator
        import asyncio

        from .orchestrator.integration import create_ghostwire_orchestrator

        async def run_orchestration():
            orchestrator = create_ghostwire_orchestrator(
                llm_endpoints=[settings.LOCAL_OLLAMA_URL],
                default_model=settings.DEFAULT_OLLAMA_MODEL,
            )

            result = await orchestrator.process_request(args.request)
            print(f"Orchestration Result: {result['response']}")

            await orchestrator.close()

        asyncio.run(run_orchestration())
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
