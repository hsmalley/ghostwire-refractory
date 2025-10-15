"""
Unit tests for GhostWire Refractory - Sample Data Seeder

Tests the sample data seeder functionality with various configurations.
"""

import os
import sqlite3
import tempfile
from pathlib import Path

import pytest

from scripts.seed_sample_data import create_sample_embeddings, seed_sample_data


class TestSampleDataSeeder:
    """Test suite for the sample data seeder functionality."""

    def test_create_sample_embeddings(self):
        """Test that sample embeddings are created correctly."""
        embed_dim = 768
        num_samples = 5
        
        embeddings = create_sample_embeddings(embed_dim, num_samples)
        
        # Should return correct number of embeddings
        assert len(embeddings) == num_samples
        
        # Each embedding should be bytes of correct size
        for embedding in embeddings:
            assert isinstance(embedding, bytes)
            # Each float32 vector of embed_dim should be 4 * embed_dim bytes
            assert len(embedding) == embed_dim * 4
        
        # Verify embeddings are normalized (unit length)
        import numpy as np
        for embedding_bytes in embeddings:
            vector = np.frombuffer(embedding_bytes, dtype=np.float32)
            norm = np.linalg.norm(vector)
            # Should be approximately 1.0 (unit vector)
            assert abs(norm - 1.0) < 1e-6

    def test_create_sample_embeddings_different_dims(self):
        """Test sample embeddings with different dimensions."""
        import numpy as np
        for dim in [128, 256, 768, 1024]:
            embeddings = create_sample_embeddings(dim, 2)
            assert len(embeddings) == 2
            for embedding in embeddings:
                assert len(embedding) == dim * 4
                # Verify normalization
                vector = np.frombuffer(embedding, dtype=np.float32)
                norm = np.linalg.norm(vector)
                assert abs(norm - 1.0) < 1e-6

    def test_seed_sample_data_to_temp_db(self):
        """Test that sample data can be seeded to a temporary database."""
        # Create a temporary database file
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            tmp_db_path = tmp_db.name
        
        try:
            # Seed sample data to the temporary database
            seed_sample_data(db_path=tmp_db_path, embed_dim=768, force=True)
            
            # Connect to the database and verify data was inserted
            conn = sqlite3.connect(tmp_db_path)
            cursor = conn.cursor()
            
            # Check that memory_text table exists and has data
            cursor.execute("SELECT COUNT(*) FROM memory_text")
            count = cursor.fetchone()[0]
            assert count > 0, f"Expected some records, but found {count}"
            
            # Check that there are at least 15 entries (5 sessions * 3 messages each)
            assert count >= 15, f"Expected at least 15 records, but found {count}"
            
            # Check that the data has the expected structure
            cursor.execute("SELECT session_id, prompt_text, answer_text, embedding FROM memory_text LIMIT 1")
            row = cursor.fetchone()
            
            assert row is not None
            session_id, prompt_text, answer_text, embedding = row
            
            assert isinstance(session_id, str)
            assert "session_" in session_id  # Should be one of our sample session IDs
            assert isinstance(prompt_text, str)
            assert len(prompt_text) > 0
            assert isinstance(answer_text, str)
            assert len(answer_text) > 0
            assert isinstance(embedding, bytes)
            assert len(embedding) == 768 * 4  # 768-dim float32 embedding
            
            # Check that there are multiple unique session IDs
            cursor.execute("SELECT DISTINCT session_id FROM memory_text")
            session_ids = [row[0] for row in cursor.fetchall()]
            assert len(session_ids) >= 5  # Should have multiple different sessions
            
            conn.close()
            
        finally:
            # Clean up the temporary database
            os.unlink(tmp_db_path)

    def test_idempotency_without_force(self):
        """Test that seeding without force doesn't duplicate data."""
        # Create a temporary database file
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            tmp_db_path = tmp_db.name
        
        try:
            # Seed data for the first time
            seed_sample_data(db_path=tmp_db_path, embed_dim=768, force=True)
            
            # Connect and check initial count
            conn = sqlite3.connect(tmp_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM memory_text")
            initial_count = cursor.fetchone()[0]
            conn.close()
            
            # Try to seed again without force (should not add more data)
            seed_sample_data(db_path=tmp_db_path, embed_dim=768, force=False)
            
            # Check final count
            conn = sqlite3.connect(tmp_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM memory_text")
            final_count = cursor.fetchone()[0]
            conn.close()
            
            # Counts should be the same (no new data added)
            assert initial_count == final_count
            
        finally:
            # Clean up the temporary database
            os.unlink(tmp_db_path)

    def test_force_seeding_adds_data(self):
        """Test that using force parameter allows multiple seeding runs."""
        # Create a temporary database file
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            tmp_db_path = tmp_db.name
        
        try:
            # Seed data for the first time
            seed_sample_data(db_path=tmp_db_path, embed_dim=768, force=True)
            
            # Connect and check initial count
            conn = sqlite3.connect(tmp_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM memory_text")
            initial_count = cursor.fetchone()[0]
            conn.close()
            
            # Seed again with force (should add more data)
            seed_sample_data(db_path=tmp_db_path, embed_dim=768, force=True)
            
            # Check final count
            conn = sqlite3.connect(tmp_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM memory_text")
            final_count = cursor.fetchone()[0]
            conn.close()
            
            # Final count should be higher (more data added)
            assert final_count > initial_count
            
        finally:
            # Clean up the temporary database
            os.unlink(tmp_db_path)

    def test_respects_environment_settings(self):
        """Test that the seeder respects environment settings."""
        # Test with a custom embed_dim
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            tmp_db_path = tmp_db.name
        
        try:
            # Seed data with custom embedding dimension
            custom_dim = 512
            seed_sample_data(db_path=tmp_db_path, embed_dim=custom_dim, force=True)
            
            # Connect and check an embedding
            conn = sqlite3.connect(tmp_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT embedding FROM memory_text LIMIT 1")
            embedding = cursor.fetchone()[0]
            conn.close()
            
            # Verify the embedding has the correct size for the custom dimension
            assert len(embedding) == custom_dim * 4  # custom_dim * 4 bytes per float32
            
        finally:
            # Clean up the temporary database
            os.unlink(tmp_db_path)