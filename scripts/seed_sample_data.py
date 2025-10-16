#!/usr/bin/env python3
"""
Sample Data Seeder for GhostWire Refractory

Populates the local SQLite database with sample sessions, messages, and synthetic embeddings
to accelerate local development and testing.
"""

import argparse
import os
import random
import sqlite3
import struct
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

# Add the python directory to the path to access ghostwire modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ghostwire.config.settings import settings
from ghostwire.models.memory import DATABASE_SCHEMA


def create_sample_embeddings(embed_dim: int, num_samples: int) -> list[bytes]:
    """
    Create sample embeddings as random vectors of specified dimension.
    
    Args:
        embed_dim: Dimension of embedding vectors
        num_samples: Number of embeddings to generate
        
    Returns:
        List of embedding vectors serialized as bytes
    """
    embeddings = []
    for _ in range(num_samples):
        # Generate random vector and normalize to unit length
        vector = np.random.randn(embed_dim).astype(np.float32)
        vector = vector / (np.linalg.norm(vector) + 1e-8)  # Normalize with small epsilon
        embeddings.append(vector.tobytes())
    return embeddings


def seed_sample_data(db_path: str = None, embed_dim: int = None, force: bool = False):
    """
    Populate the database with sample data.
    
    Args:
        db_path: Path to database (uses default if None)
        embed_dim: Embedding dimension (uses default if None)
        force: If True, will insert even if sample data already exists
    """
    # Use configured values if not provided
    db_path = db_path or settings.DB_PATH
    embed_dim = embed_dim or settings.EMBED_DIM
    
    print(f"🌱 Seeding sample data to database: {db_path}")
    print(f"📊 Using embedding dimension: {embed_dim}")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Apply the schema if tables don't exist
        cursor.executescript(DATABASE_SCHEMA)
        
        # Check if sample data already exists (avoid duplicates unless forced)
        if not force:
            cursor.execute("SELECT COUNT(*) FROM memory_text WHERE prompt_text LIKE '%Sample%' OR answer_text LIKE '%Sample%' OR summary_text LIKE '%Sample%'")
            existing_count = cursor.fetchone()[0]
            if existing_count > 0:
                print(f"⚠️  Sample data already exists ({existing_count} entries). Use --force to add more.")
                return
        
        # Generate sample sessions with associated messages
        sample_sessions = [
            ("session_neon_chat", "Neon Oracle", "Welcome to GhostWire Refractory!"),
            ("session_vector_db", "Vector Wizard", "HNSW index initialized successfully."),
            ("session_embedding", "Embedding Specialist", "Vector similarity search is now optimized."),
            ("session_api_v1", "API Orchestrator", "New endpoints registered and ready."),
            ("session_debug", "Debug Oracle", "All services are running smoothly.")
        ]
        
        # Generate sample conversations for each session
        sample_prompts = [
            "What is the purpose of GhostWire Refractory?",
            "How do I configure the embedding service?",
            "Can you explain the HNSW indexing?",
            "What are the API rate limits?",
            "How do I run the benchmark suite?",
            "What's the token optimization feature?",
            "How do I set up local development?",
            "Can you explain the vector normalization?"
        ]
        
        sample_responses = [
            "GhostWire Refractory is a neural network-based chat system with memory that stores message embeddings in SQLite and uses HNSW for efficient vector similarity search.",
            "The embedding service can be configured through environment variables. Use EMBED_DIM to set the embedding dimension.",
            "HNSW (Hierarchical Navigable Small World) indexing provides efficient approximate nearest neighbor search with logarithmic complexity.",
            "Rate limits are configured with RATE_LIMIT_REQUESTS and RATE_LIMIT_WINDOW environment variables. Default is 100 requests per 60 seconds.",
            "Run the benchmark suite with `python -m python.ghostwire.cli benchmark`. It will test various model performance metrics.",
            "Token optimization features include context window optimization and efficient embedding caching to reduce token usage.",
            "Set up local development by installing dependencies with uv and running `python -m python.ghostwire.main`.",
            "Vector normalization ensures all embedding vectors have unit length for consistent similarity calculations."
        ]
        
        # Generate sample embeddings for the data
        total_samples = len(sample_sessions) * 3  # 3 conversations per session
        embeddings = create_sample_embeddings(embed_dim, total_samples)
        
        # Insert sample data
        embedding_idx = 0
        inserted_count = 0
        
        for session_id, prompt_prefix, response in sample_sessions:
            # Create a few conversations per session
            base_time = datetime.utcnow() - timedelta(days=random.randint(0, 7))
            
            # First conversation in session
            prompt = f"{prompt_prefix}: {random.choice(sample_prompts)}"
            answer = response
            timestamp = (base_time - timedelta(hours=2)).timestamp()
            
            cursor.execute(
                "INSERT INTO memory_text (session_id, prompt_text, answer_text, timestamp, embedding, summary_text) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    session_id,
                    prompt,
                    answer,
                    timestamp,
                    embeddings[embedding_idx],
                    f"Sample conversation in {session_id}"
                )
            )
            embedding_idx += 1
            inserted_count += 1
            
            # Second conversation in session
            prompt2 = f"{prompt_prefix}: {random.choice(sample_prompts)}"
            answer2 = random.choice(sample_responses)
            timestamp2 = (base_time - timedelta(hours=1)).timestamp()
            
            cursor.execute(
                "INSERT INTO memory_text (session_id, prompt_text, answer_text, timestamp, embedding, summary_text) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    session_id,
                    prompt2,
                    answer2,
                    timestamp2,
                    embeddings[embedding_idx],
                    f"Follow-up in {session_id}"
                )
            )
            embedding_idx += 1
            inserted_count += 1
            
            # Third conversation in session
            prompt3 = f"{prompt_prefix}: {random.choice(sample_prompts)}"
            answer3 = random.choice(sample_responses)
            timestamp3 = base_time.timestamp()
            
            cursor.execute(
                "INSERT INTO memory_text (session_id, prompt_text, answer_text, timestamp, embedding, summary_text) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    session_id,
                    prompt3,
                    answer3,
                    timestamp3,
                    embeddings[embedding_idx],
                    f"Recent activity in {session_id}"
                )
            )
            embedding_idx += 1
            inserted_count += 1
        
        # Commit the changes
        conn.commit()
        print(f"✅ Successfully inserted {inserted_count} sample memory entries across {len(sample_sessions)} sessions")
        print(f"💡 Sample session IDs: {', '.join([s[0] for s in sample_sessions])}")
        
    except Exception as e:
        print(f"❌ Error seeding sample data: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def main():
    """Main entry point for the sample data seeder."""
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
    
    if args.verbose:
        print("⚡️ GhostWire Refractory - Sample Data Seeder")
        print("=" * 50)
    
    try:
        seed_sample_data(
            db_path=args.db_path,
            embed_dim=args.embed_dim,
            force=args.force
        )
        
        if args.verbose:
            print("\n🎉 Sample data seeding complete!")
            print("You can now explore the application with sample data.")
            
    except Exception as e:
        print(f"💥 Failed to seed sample data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()