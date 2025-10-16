"""
Unit tests for GhostWire Refractory - Llama Deployment Script

Tests the llama deployment functionality with various configurations.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.llama_deploy import LlamaDeployer, main


class TestLlamaDeployer:
    """Test suite for the LlamaDeployer class."""

    def test_init_with_hosts(self):
        """Test that LlamaDeployer initializes correctly with hosts."""
        hosts = ["server1", "server2"]
        deployer = LlamaDeployer(hosts=hosts)
        
        assert deployer.hosts == hosts
        assert deployer.user is not None  # Should default to current user
        assert deployer.port == 22

    def test_init_with_custom_user_and_port(self):
        """Test that LlamaDeployer initializes correctly with custom user and port."""
        hosts = ["server1"]
        user = "testuser"
        port = 2222
        deployer = LlamaDeployer(hosts=hosts, user=user, port=port)
        
        assert deployer.hosts == hosts
        assert deployer.user == user
        assert deployer.port == port

    def test_generate_systemd_unit(self):
        """Test that systemd unit content is generated correctly."""
        hosts = ["server1"]
        deployer = LlamaDeployer(hosts=hosts)
        
        service_name = "test-llama"
        llamafile_path = "/opt/llamafiles/test.llamafile"
        unit_content = deployer._generate_systemd_unit(service_name, llamafile_path)
        
        # Check that the unit content contains expected elements
        assert f"Description=Llamafile Service - {service_name}" in unit_content
        assert f"ExecStart={llamafile_path} --server --port 8080" in unit_content
        assert "[Unit]" in unit_content
        assert "[Service]" in unit_content
        assert "[Install]" in unit_content
        assert "WantedBy=multi-user.target" in unit_content

    def test_create_sample_embeddings(self):
        """Test that sample embeddings are created correctly."""
        from scripts.seed_sample_data import create_sample_embeddings
        
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
        from scripts.seed_sample_data import create_sample_embeddings
        
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

    @patch("scripts.llama_deploy.Connection")
    def test_deploy_to_host_success(self, mock_connection):
        """Test successful deployment to a host."""
        # Mock the connection and its methods
        mock_conn = MagicMock()
        mock_connection.return_value = mock_conn
        
        # Mock the sudo and run methods to return success
        mock_conn.sudo.return_value = MagicMock(return_code=0)
        mock_conn.run.return_value = MagicMock(return_code=0, stdout="active")
        
        # Mock the put method (file transfer)
        mock_conn.put.return_value = None
        
        # Create deployer and test deployment
        hosts = ["server1"]
        deployer = LlamaDeployer(hosts=hosts)
        
        # Create a temporary file to use as llamafile
        with tempfile.NamedTemporaryFile(suffix='.llamafile', delete=False) as tmp_file:
            tmp_file_path = tmp_file.name
            tmp_file.write(b"fake llamafile content")
        
        try:
            result = deployer._deploy_to_host(
                host="server1",
                llamafile_path=tmp_file_path,
                service_name="test-llama",
                destination_path="/opt/llamafiles",
                force=True
            )
            
            # Should return True for success
            assert result is True
            
            # Verify that connection methods were called
            mock_connection.assert_called_once_with(
                host="server1",
                user=deployer.user,
                port=22,
                connect_kwargs={}
            )
            
            # Verify that sudo commands were called
            mock_conn.sudo.assert_any_call("systemctl daemon-reload")
            mock_conn.sudo.assert_any_call("systemctl enable test-llama")
            mock_conn.sudo.assert_any_call("systemctl restart test-llama")
            
            # Verify that put was called to upload the file
            mock_conn.put.assert_called_once()
            
        finally:
            # Clean up the temporary file
            os.unlink(tmp_file_path)

    @patch("scripts.llama_deploy.Connection")
    def test_deploy_to_host_failure(self, mock_connection_class):
        """Test failed deployment to a host."""
        # Mock the connection instance to raise an exception
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=None)
        mock_connection_class.return_value = mock_conn
        
        # Mock the sudo method to raise an exception
        mock_conn.sudo.side_effect = Exception("Connection failed")
        
        # Create deployer and test deployment
        hosts = ["server1"]
        deployer = LlamaDeployer(hosts=hosts)
        
        # Create a temporary file to use as llamafile
        with tempfile.NamedTemporaryFile(suffix='.llamafile', delete=False) as tmp_file:
            tmp_file_path = tmp_file.name
            tmp_file.write(b"fake llamafile content")
        
        try:
            result = deployer._deploy_to_host(
                host="server1",
                llamafile_path=tmp_file_path,
                service_name="test-llama",
                destination_path="/opt/llamafiles",
                force=True
            )
            
            # Should return False for failure
            assert result is False
            
        finally:
            # Clean up the temporary file
            os.unlink(tmp_file_path)

    def test_deploy_sample_data_to_temp_db(self):
        """Test that sample data can be seeded to a temporary database."""
        # Create a temporary database file
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            tmp_db_path = tmp_db.name
        
        try:
            # Seed sample data to the temporary database
            from scripts.seed_sample_data import seed_sample_data
            seed_sample_data(db_path=tmp_db_path, embed_dim=768, force=True)
            
            # Connect to the database and verify data was inserted
            import sqlite3
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
            from scripts.seed_sample_data import seed_sample_data
            seed_sample_data(db_path=tmp_db_path, embed_dim=768, force=True)
            
            # Connect and check initial count
            import sqlite3
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
            from scripts.seed_sample_data import seed_sample_data
            seed_sample_data(db_path=tmp_db_path, embed_dim=768, force=True)
            
            # Connect and check initial count
            import sqlite3
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
            # Seed with custom embedding dimension
            from scripts.seed_sample_data import seed_sample_data
            seed_sample_data(db_path=tmp_db_path, embed_dim=512, force=True)
            
            # Connect and check an embedding
            import sqlite3
            conn = sqlite3.connect(tmp_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT embedding FROM memory_text LIMIT 1")
            embedding = cursor.fetchone()[0]
            conn.close()
            
            # Verify the embedding has the correct size for the custom dimension
            assert len(embedding) == 512 * 4  # 512-dim float32 embedding
            
        finally:
            # Clean up the temporary database
            os.unlink(tmp_db_path)