"""
Command-line interface for GhostWire Refractory Token Usage Benchmarks
"""

import argparse
import asyncio
import logging
import sys

from ..utils.token_benchmark import TokenBenchmarkSuite

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """Main entry point for benchmark CLI"""
    parser = argparse.ArgumentParser(
        description="GhostWire Refractory Token Usage Benchmark Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                        # Run all benchmarks with default settings
  %(prog)s --verbose             # Run with verbose output
  %(prog)s --report             # Generate and display report only
  %(prog)s --save-report file.json  # Save report to specific file
        """
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging output"
    )
    
    parser.add_argument(
        "--report", "-r",
        action="store_true",
        help="Generate and display benchmark report (without running benchmarks)"
    )
    
    parser.add_argument(
        "--save-report", "-s",
        metavar="FILE",
        help="Save benchmark report to specified JSON file"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json"],
        default="text",
        help="Report format (default: text)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Handle report-only mode
    if args.report:
        try:
            suite = TokenBenchmarkSuite()
            if args.format == "text":
                print(suite.generate_report())
            else:
                print(suite.generate_report())  # For now, same as text
            return 0
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return 1
    
    # Run benchmarks
    logger.info("Starting GhostWire Refractory Token Usage Benchmarks...")
    
    try:
        # Run the benchmark suite
        suite = TokenBenchmarkSuite()
        asyncio.run(suite.run_all_benchmarks())
        
        # Generate and display report
        report = suite.generate_report()
        print(report)
        
        # Save report if requested
        if args.save_report:
            suite.save_report(args.save_report)
            logger.info(f"Report saved to {args.save_report}")
        
        logger.info("Token usage benchmarks completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Benchmark interrupted by user")
        return 130  # Standard SIGINT exit code
    except Exception as e:
        logger.error(f"Benchmark failed: {e}", exc_info=args.verbose)
        return 1


if __name__ == "__main__":
    sys.exit(main())