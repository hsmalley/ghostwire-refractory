#!/usr/bin/env python3
"""
CLI tool for seeding sample data in GhostWire Refractory

Provides a simple command-line interface to populate the local database
with sample data for development and testing purposes.
"""

import argparse
import os
import sys
from pathlib import Path

# Add the python directory to the path to access ghostwire modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ghostwire.config.settings import settings


def main():
    """Main entry point for the sample data seeder CLI."""
    parser = argparse.ArgumentParser(
        prog="seed_sample_data",
        description="Seed the GhostWire Refractory database with sample data",
        epilog="""
Examples:
  %(prog)s                     # Seed with default settings
  %(prog)s --verbose          # Seed with verbose output
  %(prog)s --force            # Force re-seeding even if data exists
  %(prog)s --db-path custom.db # Seed to a custom database path
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--db-path",
        type=str,
        default=None,
        help="Path to SQLite database (defaults to DB_PATH from settings)"
    )
    
    parser.add_argument(
        "--embed-dim",
        type=int,
        default=None,
        help="Embedding dimension (defaults to EMBED_DIM from settings)"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force insertion even if sample data already exists"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Import the seeder function here to avoid issues with path
    try:
        from scripts.seed_sample_data import seed_sample_data
    except ImportError as e:
        print(f"❌ Error importing seeder: {e}")
        print("💡 Make sure you're running from the project root directory")
        sys.exit(1)
    
    # Run the seeder with the provided arguments
    try:
        seed_sample_data(
            db_path=args.db_path,
            embed_dim=args.embed_dim,
            force=args.force,
            verbose=args.verbose
        )
        
        if args.verbose:
            print("\n🎉 Sample data seeding complete!")
            print("You can now explore the application with sample data.")
            
    except Exception as e:
        print(f"💥 Failed to seed sample data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()