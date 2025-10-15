"""
Unit tests for GhostWire Refractory - Vector Utilities

Tests the vector normalization functionality with various edge cases.
"""

import numpy as np
from ghostwire.utils.vector_utils import normalize_vector


class TestVectorNormalization:
    """Test suite for the normalize_vector function."""

    def test_normalize_unit_vector_unchanged(self):
        """Test that a unit vector remains unchanged after normalization."""
        unit_vector = np.array([1.0, 0.0, 0.0])
        result = normalize_vector(unit_vector)

        # The unit vector should remain the same
        np.testing.assert_array_equal(result, unit_vector)
        # Norm should be 1
        assert np.isclose(np.linalg.norm(result), 1.0)

    def test_normalize_simple_vector(self):
        """Test normalization of a simple vector."""
        input_vector = np.array([3.0, 4.0, 0.0])  # This has magnitude 5
        result = normalize_vector(input_vector)

        # Check that the result is a unit vector (magnitude = 1)
        assert np.isclose(np.linalg.norm(result), 1.0, atol=1e-7)

        # Check that the direction is preserved
        expected = np.array([0.6, 0.8, 0.0])  # [3/5, 4/5, 0/5]
        np.testing.assert_allclose(result, expected, atol=1e-7)

    def test_normalize_random_vector(self):
        """Test normalization of a random vector."""
        np.random.seed(42)  # For reproducible results
        input_vector = np.random.rand(10)
        result = normalize_vector(input_vector)

        # The result should be a unit vector
        assert np.isclose(np.linalg.norm(result), 1.0, atol=1e-7)

    def test_normalize_zero_vector(self):
        """Test that zero vector is handled correctly."""
        zero_vector = np.array([0.0, 0.0, 0.0])
        result = normalize_vector(zero_vector)

        # Zero vector should be returned unchanged
        np.testing.assert_array_equal(result, zero_vector)

        # Norm should still be 0
        assert np.linalg.norm(result) == 0.0

    def test_normalize_single_element_vector(self):
        """Test normalization of a single-element vector."""
        input_vector = np.array([5.0])
        result = normalize_vector(input_vector)

        # Should be normalized to [1.0] or [-1.0] depending on sign
        expected = np.array([1.0])
        np.testing.assert_allclose(result, expected, atol=1e-7)
        assert np.isclose(np.linalg.norm(result), 1.0, atol=1e-7)

    def test_normalize_negative_vector(self):
        """Test normalization of a vector with negative components."""
        input_vector = np.array([-3.0, -4.0, 0.0])  # This has magnitude 5
        result = normalize_vector(input_vector)

        # Check that the result is a unit vector (magnitude = 1)
        assert np.isclose(np.linalg.norm(result), 1.0, atol=1e-7)

        # Check that the direction is preserved (negative)
        expected = np.array([-0.6, -0.8, 0.0])  # [-3/5, -4/5, 0/5]
        np.testing.assert_allclose(result, expected, atol=1e-7)

    def test_normalize_2d_vector(self):
        """Test normalization of a 2D vector."""
        input_vector = np.array([1.0, 1.0])  # This has magnitude sqrt(2)
        result = normalize_vector(input_vector)

        # Check that the result is a unit vector
        assert np.isclose(np.linalg.norm(result), 1.0, atol=1e-7)

        # Check specific values (normalized to unit vector in diagonal direction)
        expected_magnitude = np.sqrt(2)
        expected = np.array([1.0 / expected_magnitude, 1.0 / expected_magnitude])
        np.testing.assert_allclose(result, expected, atol=1e-7)

    def test_normalize_3d_vector(self):
        """Test normalization of a 3D vector."""
        input_vector = np.array([1.0, 2.0, 2.0])  # This has magnitude 3
        result = normalize_vector(input_vector)

        # Check that the result is a unit vector
        assert np.isclose(np.linalg.norm(result), 1.0, atol=1e-7)

        # Check specific values (each component divided by 3)
        expected = np.array([1.0 / 3.0, 2.0 / 3.0, 2.0 / 3.0])
        np.testing.assert_allclose(result, expected, atol=1e-7)

    def test_normalize_large_magnitude_vector(self):
        """Test normalization of a vector with large magnitude."""
        scale = 1000.0
        input_vector = np.array([3.0 * scale, 4.0 * scale, 0.0 * scale])
        result = normalize_vector(input_vector)

        # Check that the result is a unit vector
        assert np.isclose(np.linalg.norm(result), 1.0, atol=1e-7)

        # Direction should be preserved
        expected = np.array([0.6, 0.8, 0.0])  # Same direction as [3,4,0]
        np.testing.assert_allclose(result, expected, atol=1e-7)

    def test_normalize_already_normalized_vector(self):
        """Test normalization of a vector that's already normalized."""
        # Create a random unit vector
        np.random.seed(123)
        random_vector = np.random.rand(5)
        unit_vector = random_vector / np.linalg.norm(random_vector)

        result = normalize_vector(unit_vector)

        # Should be unchanged (within floating point precision)
        np.testing.assert_allclose(result, unit_vector, atol=1e-10)
        # Should still have unit length
        assert np.isclose(np.linalg.norm(result), 1.0, atol=1e-7)
