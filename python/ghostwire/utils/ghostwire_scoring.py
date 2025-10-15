"""
GHOSTWIRE Scoring Utilities for Benchmarking
Provides standardized scoring functions for comparing models across different benchmarks.
"""

import numpy as np
from typing import Union, Dict, Any


def compute_general_ghostwire_score(
    latency: float,
    stability: float = 1.0,
    memory_usage: float = 0.5,
    weight_latency: float = 0.5,
    weight_stability: float = 0.3,
    weight_memory: float = 0.2
) -> float:
    """
    Compute a general GHOSTWIRE score based on latency, stability, and memory usage.
    
    Args:
        latency: Time taken for the operation (lower is better)
        stability: Stability metric (e.g., embedding consistency, higher is better)
        memory_usage: Memory usage during operation (lower is better)
        weight_latency: Weight for latency component (default 0.5)
        weight_stability: Weight for stability component (default 0.3)
        weight_memory: Weight for memory component (default 0.2)
        
    Returns:
        float: GHOSTWIRE score (higher is better)
    """
    # Normalize the components to be in [0, 1] range
    # For latency and memory usage, lower is better, so we use inverse functions
    normalized_latency = 1 / (1 + latency)  # Approaches 1 as latency approaches 0
    normalized_memory = 1 / (1 + memory_usage)  # Approaches 1 as memory usage approaches 0
    
    # Stability is already in [0, 1] range where higher is better
    normalized_stability = stability
    
    # Compute the weighted score
    score = (
        weight_latency * normalized_latency +
        weight_stability * normalized_stability +
        weight_memory * normalized_memory
    )
    
    return score


def compute_rag_ghostwire_score(
    quality: float,
    hallucination: float,
    latency: float,
    weight_quality: float = 0.4,
    weight_hallucination: float = 0.3,
    weight_latency: float = 0.3
) -> float:
    """
    Compute GHOSTWIRE score for RAG (Retrieval-Augmented Generation) benchmarks.
    
    Args:
        quality: Quality of the response (higher is better)
        hallucination: Hallucination rate (lower is better)
        latency: Time taken (lower is better)
        weight_quality: Weight for quality component (default 0.4)
        weight_hallucination: Weight for hallucination component (default 0.3)
        weight_latency: Weight for latency component (default 0.3)
        
    Returns:
        float: GHOSTWIRE score for RAG (higher is better)
    """
    # Normalize components to [0, 1] range where higher is better
    normalized_quality = quality  # Already in [0, 1] range
    normalized_hallucination = 1 - hallucination  # Invert since lower hallucination is better
    normalized_latency = 1 / (1 + latency)  # Lower latency is better
    
    # Compute the weighted score
    score = (
        weight_quality * normalized_quality +
        weight_hallucination * normalized_hallucination +
        weight_latency * normalized_latency
    )
    
    return score


def compute_retrieval_ghostwire_score(
    consistency: float,
    avg_similarity: float,
    latency: float,
    weight_consistency: float = 0.4,
    weight_similarity: float = 0.4,
    weight_latency: float = 0.2
) -> float:
    """
    Compute GHOSTWIRE score for retrieval benchmarks.
    
    Args:
        consistency: Retrieval consistency (higher is better)
        avg_similarity: Average embedding similarity (higher is better)
        latency: Time taken (lower is better)
        weight_consistency: Weight for consistency component (default 0.4)
        weight_similarity: Weight for similarity component (default 0.4)
        weight_latency: Weight for latency component (default 0.2)
        
    Returns:
        float: GHOSTWIRE score for retrieval (higher is better)
    """
    # All components are already in [0, 1] range where higher is better
    normalized_consistency = consistency
    normalized_similarity = avg_similarity
    normalized_latency = 1 / (1 + latency)  # Lower latency is better
    
    # Compute the weighted score
    score = (
        weight_consistency * normalized_consistency +
        weight_similarity * normalized_similarity +
        weight_latency * normalized_latency
    )
    
    return score


def compute_summarization_ghostwire_score(
    quality: float,
    hallucination: float,
    length_penalty: float,
    latency: float,
    weight_quality: float = 0.4,
    weight_hallucination: float = 0.3,
    weight_length: float = 0.2,
    weight_latency: float = 0.1
) -> float:
    """
    Compute GHOSTWIRE score for summarization benchmarks.
    
    Args:
        quality: Quality of the summary (higher is better)
        hallucination: Hallucination rate (lower is better)
        length_penalty: Penalty for length (higher is better if appropriate length)
        latency: Time taken (lower is better)
        weight_quality: Weight for quality component (default 0.4)
        weight_hallucination: Weight for hallucination component (default 0.3)
        weight_length: Weight for length component (default 0.2)
        weight_latency: Weight for latency component (default 0.1)
        
    Returns:
        float: GHOSTWIRE score for summarization (higher is better)
    """
    # Normalize components to [0, 1] range where higher is better
    normalized_quality = quality
    normalized_hallucination = 1 - hallucination  # Invert since lower hallucination is better
    normalized_length_penalty = length_penalty  # Assuming this is already normalized
    normalized_latency = 1 / (1 + latency)  # Lower latency is better
    
    # Compute the weighted score
    score = (
        weight_quality * normalized_quality +
        weight_hallucination * normalized_hallucination +
        weight_length * normalized_length_penalty +
        weight_latency * normalized_latency
    )
    
    return score


def compute_comprehensive_ghostwire_score(
    latency: float,
    throughput: float,
    memory_usage: float,
    quality: float,
    stability: float = 1.0,
    weight_latency: float = 0.2,
    weight_throughput: float = 0.2,
    weight_memory: float = 0.2,
    weight_quality: float = 0.3,
    weight_stability: float = 0.1
) -> float:
    """
    Compute a comprehensive GHOSTWIRE score considering multiple performance dimensions.
    
    Args:
        latency: Time taken for the operation (lower is better)
        throughput: Operations per second (higher is better)
        memory_usage: Memory usage during operation (lower is better)
        quality: Quality of output (higher is better)
        stability: Stability metric (higher is better)
        weight_latency: Weight for latency component (default 0.2)
        weight_throughput: Weight for throughput component (default 0.2)
        weight_memory: Weight for memory component (default 0.2)
        weight_quality: Weight for quality component (default 0.3)
        weight_stability: Weight for stability component (default 0.1)
        
    Returns:
        float: Comprehensive GHOSTWIRE score (higher is better)
    """
    # Normalize components to [0, 1] range where higher is better
    normalized_latency = 1 / (1 + latency)  # Lower latency is better
    normalized_throughput = min(throughput, 1.0)  # Higher throughput is better
    normalized_memory = 1 / (1 + memory_usage)  # Lower memory usage is better
    normalized_quality = quality  # Already in [0, 1] range
    normalized_stability = stability  # Already in [0, 1] range
    
    # Compute the weighted score
    score = (
        weight_latency * normalized_latency +
        weight_throughput * normalized_throughput +
        weight_memory * normalized_memory +
        weight_quality * normalized_quality +
        weight_stability * normalized_stability
    )
    
    return score


def format_benchmark_results_with_scores(results: Dict[str, Any], score_function_name: str = "general") -> str:
    """
    Format benchmark results with GHOSTWIRE scores for display.
    
    Args:
        results: Dictionary containing benchmark results
        score_function_name: Name of the scoring function to use
        
    Returns:
        str: Formatted results string with GHOSTWIRE scores
    """
    if score_function_name == "general":
        score_function = compute_general_ghostwire_score
    elif score_function_name == "rag":
        score_function = compute_rag_ghostwire_score
    elif score_function_name == "retrieval":
        score_function = compute_retrieval_ghostwire_score
    elif score_function_name == "summarization":
        score_function = compute_summarization_ghostwire_score
    elif score_function_name == "comprehensive":
        score_function = compute_comprehensive_ghostwire_score
    else:
        # Default to general if unknown
        score_function = compute_general_ghostwire_score

    # Attempt to compute a score based on available metrics in results
    try:
        if score_function_name == "general":
            # Extract required parameters for the general score function
            latency = results.get("embedding_latency", results.get("search_latency", results.get("storage_latency", 1.0)))
            memory_usage = results.get("memory_usage_gb", 0.5)
            score = score_function(latency=latency, memory_usage=memory_usage)
        elif score_function_name == "rag":
            latency = results.get("rag_latency", results.get("retrieval_latency", 1.0))
            quality = results.get("quality", 0.5)
            hallucination = results.get("hallucination_rate", 0.2)
            score = score_function(quality=quality, hallucination=hallucination, latency=latency)
        elif score_function_name == "comprehensive":
            latency = results.get("embedding_latency", results.get("search_latency", 1.0))
            throughput = results.get("throughput", 1.0)
            memory_usage = results.get("memory_usage_gb", 0.5)
            quality = results.get("quality", 0.5)
            score = score_function(
                latency=latency,
                throughput=throughput,
                memory_usage=memory_usage,
                quality=quality
            )
        else:
            # For other types, we'll just return a placeholder
            score = 0.0  # Placeholder until we have full metrics

        result_str = f"📊 BENCHMARK RESULTS WITH GHOSTWIRE SCORES:\n"
        result_str += f"-" * 60 + "\n"
        
        for key, value in results.items():
            if isinstance(value, float):
                result_str += f"{key.replace('_', ' ').title()}: {value:.4f}\n"
            else:
                result_str += f"{key.replace('_', ' ').title()}: {value}\n"
        
        result_str += f"Overall GHOSTWIRE Score: {score:.4f}\n"
        result_str += f"Score Type: {score_function_name.title()}\n"
        result_str += f"-" * 60 + "\n"
        
        return result_str
    except Exception as e:
        # If we can't compute a score, just format the results without it
        result_str = f"📊 BENCHMARK RESULTS (GHOSTWIRE score computation failed: {e}):\n"
        result_str += f"-" * 60 + "\n"
        
        for key, value in results.items():
            if isinstance(value, float):
                result_str += f"{key.replace('_', ' ').title()}: {value:.4f}\n"
            else:
                result_str += f"{key.replace('_', ' ').title()}: {value}\n"
        
        result_str += f"-" * 60 + "\n"
        
        return result_str