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
        description="GhostWire Refractory - Neural network-based chat system with memory"
    )
    
    parser.add_argument(
        "command",
        nargs="?",
        default="serve",
        choices=["serve", "benchmark"],
        help="Command to execute (default: serve)"
    )
    
    # Serve command arguments
    parser.add_argument(
        "--host",
        default=settings.HOST,
        help="Host to bind the server to"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=settings.PORT,
        help="Port to bind the server to"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on code changes"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command == "benchmark":
        # Run token usage benchmarks
        try:
            import asyncio
            from .utils.token_benchmark import TokenBenchmarkSuite
            
            print("Running GhostWire Refractory Token Usage Benchmarks...")
            print("=" * 60)
            
            suite = TokenBenchmarkSuite()
            asyncio.run(suite.run_all_benchmarks())
            report = suite.generate_report()
            print(report)
            suite.save_report("token_benchmark_report.json")
            print("\nReport saved to token_benchmark_report.json")
            
            return 0
        except KeyboardInterrupt:
            print("\nBenchmark interrupted by user")
            return 130
        except Exception as e:
            print(f"Error running benchmarks: {e}")
            return 1
    
    else:  # serve command
        # Start the FastAPI server
        try:
            import uvicorn
            from .main import app
            
            print(f"Starting GhostWire Refractory server on {args.host}:{args.port}...")
            
            uvicorn.run(
                app,
                host=args.host,
                port=args.port,
                reload=args.reload,
            )
            
            return 0
        except KeyboardInterrupt:
            print("\nServer stopped by user")
            return 0
        except Exception as e:
            print(f"Error starting server: {e}")
            return 1


if __name__ == "__main__":
    sys.exit(main())
