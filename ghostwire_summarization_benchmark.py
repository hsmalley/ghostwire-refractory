# ghostwire_summarization_benchmark.py

import asyncio
import time

import httpx
import numpy as np
from rouge_score import rouge_scorer

CONTROLLER_URL = "http://localhost:8000"
CHAT_ROUTE = (
    "/chat_completion"  # or "/chat_embedding" if that’s what your summarizer uses
)
MODELS = [
    "gemma3:1b",
    "gemma3n:e2b",
    "gemma3n:e4b",
]

DOCUMENTS = [
    {
        "label": "Short",
        "text": "Quantum computers exploit superposition and entanglement to solve certain problems more efficiently than classical computers.",
        "gold_summary": "Quantum computers use superposition and entanglement to solve problems faster than classical computers.",
    },
    {
        "label": "Medium",
        "text": "Superposition allows a qubit to exist in multiple states simultaneously, while entanglement correlates qubits even across distance. "
        "Together, they enable massive parallelism in computation, though practical error correction remains a key challenge.",
        "gold_summary": "Qubits can be in multiple states at once due to superposition and are correlated by entanglement, enabling parallelism but requiring error correction.",
    },
    {
        "label": "Long",
        "text": "Quantum computing is a paradigm that departs from the classical model of bits. "
        "In classical computing, bits take values 0 or 1, but qubits can exist in superpositions. "
        "Entanglement—correlations between qubits—creates an exponentially larger state space. "
        "However, decoherence and noise limit performance, requiring sophisticated quantum error correction.",
        "gold_summary": "Quantum computing uses qubits that exist in superpositions and entanglement, vastly expanding computational states but facing challenges from decoherence and noise.",
    },
]


async def summarize(text: str, model: str):
    async with httpx.AsyncClient(timeout=60.0) as client:
        if CHAT_ROUTE == "/chat_completion":
            payload = {"text": text, "model": model, "stream": False}
        else:
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a concise scientific summarizer.",
                    },
                    {
                        "role": "user",
                        "content": f"Summarize this text in 2-3 sentences:\n\n{text}",
                    },
                ],
            }
        start = time.perf_counter()
        resp = await client.post(f"{CONTROLLER_URL}{CHAT_ROUTE}", json=payload)
        resp.raise_for_status()
        latency = time.perf_counter() - start
        data = resp.json()
        if isinstance(data, dict):
            # Handle local controller response {"summary": "..."} or OpenAI-like schema
            if "summary" in data:
                content = data["summary"]
            elif "message" in data and isinstance(data["message"], dict):
                content = data["message"].get("content", "")
            elif "choices" in data and data["choices"]:
                content = data["choices"][0].get("message", {}).get("content", "")
            else:
                content = str(data)
        else:
            content = str(data)
        # Cleanup: strip conversational phrases and artifacts
        if isinstance(content, str):
            cleanup_phrases = [
                "Okay, here's a concise and clear summary of the text:",
                "Okay, here’s a concise and clear summary of the text:",
                "Do you want me to elaborate",
                "Do you want me to refine",
                "Would you like me to elaborate",
                "Would you like me to refine",
                "—",
                "---",
                "**In short:**",
            ]
            for phrase in cleanup_phrases:
                content = content.replace(phrase, "")
            # Remove trailing conversational follow-ups
            import re

            content = re.sub(
                r"(Would you like me.*|Do you want me.*|on any specific aspect.*|perhaps adjust.*|for example.*)$",
                "",
                content,
                flags=re.IGNORECASE,
            )

            # Truncate at any trailing quote followed by conversational prompt
            content = re.split(
                r'["”]\s*(on any specific aspect|Would you like me|Do you want me|perhaps adjust|for example)',
                content,
                maxsplit=1,
                flags=re.IGNORECASE,
            )[0]

            # Remove duplicated sentences
            sentences = content.split(". ")
            deduped = []
            for s in sentences:
                if s.strip() and s.strip() not in deduped:
                    deduped.append(s.strip())
            content = ". ".join(deduped)

            # Remove excessive whitespace and markdown
            content = content.replace("\n", " ").replace("  ", " ").strip()
        return content, latency


def compute_token_ratio(summary: str, reference: str):
    summary_tokens = summary.split()
    reference_tokens = reference.split()
    if len(reference_tokens) == 0:
        return 0.0
    return len(summary_tokens) / len(reference_tokens)


def compute_length_penalty(summary: str, reference: str):
    summary_len = len(summary.split())
    reference_len = len(reference.split())
    if reference_len == 0:
        return 1.0
    ratio = summary_len / reference_len
    return 1.0 if ratio > 1.0 else np.exp(1 - 1 / ratio)


def compute_cosine_similarity(text1: str, text2: str):
    # Placeholder: returns a random float between 0 and 1
    # In a real implementation, embed texts and compute cosine similarity
    return np.random.uniform(0, 1)


def simple_hallucination_check(summary: str, reference: str):
    # Simple heuristic: check if summary contains words not in reference
    ref_words = set(reference.lower().split())
    summary_words = set(summary.lower().split())
    hallucinated_words = summary_words - ref_words
    # Return proportion of hallucinated words
    if len(summary_words) == 0:
        return 0.0
    return len(hallucinated_words) / len(summary_words)


def compute_ghostwire_score(quality, hallucination, length_penalty, latency):
    score = (
        0.4 * quality
        + 0.3 * (1 - hallucination)
        + 0.2 * length_penalty
        + 0.1 * (1 / (1 + latency))
    )
    return score


async def run_summarization_benchmark():
    print("🧩 Running summarization benchmark via Ghostwire controller")
    print("=" * 80)
    results = []

    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)

    for model in MODELS:
        print(f"\n🚀 Testing summarization model: {model}")
        for doc in DOCUMENTS:
            label = doc["label"]
            text = doc["text"]
            gold_summary = doc["gold_summary"]
            try:
                summary, latency = await summarize(text, model)
                rouge_scores = scorer.score(gold_summary, summary)
                token_ratio = compute_token_ratio(summary, gold_summary)
                length_penalty = compute_length_penalty(summary, gold_summary)
                cosine_sim = compute_cosine_similarity(summary, gold_summary)
                hallucination_score = simple_hallucination_check(summary, gold_summary)
                quality_score = (
                    0.4 * rouge_scores["rouge1"].fmeasure
                    + 0.2 * rouge_scores["rouge2"].fmeasure
                    + 0.2 * rouge_scores["rougeL"].fmeasure
                    + 0.1 * cosine_sim
                    - 0.1 * hallucination_score
                ) * length_penalty

                ghostwire_score = compute_ghostwire_score(
                    quality_score, hallucination_score, length_penalty, latency
                )

                results.append(
                    {
                        "model": model,
                        "label": label,
                        "latency": latency,
                        "summary": summary,
                        "rouge1_f": rouge_scores["rouge1"].fmeasure,
                        "rouge2_f": rouge_scores["rouge2"].fmeasure,
                        "rougeL_f": rouge_scores["rougeL"].fmeasure,
                        "token_ratio": token_ratio,
                        "length_penalty": length_penalty,
                        "cosine_similarity": cosine_sim,
                        "hallucination_score": hallucination_score,
                        "quality_score": quality_score,
                        "ghostwire_score": ghostwire_score,
                    }
                )
                print(f"\n📄 [{model}] {label} summary ({latency:.2f}s):\n{summary}")
                print(f"ROUGE-1 F1: {rouge_scores['rouge1'].fmeasure:.4f}")
                print(f"ROUGE-2 F1: {rouge_scores['rouge2'].fmeasure:.4f}")
                print(f"ROUGE-L F1: {rouge_scores['rougeL'].fmeasure:.4f}")
                print(f"Token count ratio (summary/gold): {token_ratio:.4f}")
                print(f"Length penalty (brevity penalty): {length_penalty:.4f}")
                print(f"Cosine similarity (placeholder): {cosine_sim:.4f}")
                print(
                    f"Hallucination score (proportion of hallucinated words): {hallucination_score:.4f}"
                )
                print(f"Composite quality score: {quality_score:.4f}")
                print(f"Ghostwire score: {ghostwire_score:.4f}")
                print("-" * 60)
            except Exception as e:
                print(f"⚠️ Error summarizing {label}: {e}")

    print("=" * 80)
    print("✅ Summarization benchmark complete.")

    # Save results to CSV
    import csv

    csv_filename = "summarization_benchmark_results.csv"
    csv_headers = [
        "model",
        "label",
        "latency",
        "rouge1_f",
        "rouge2_f",
        "rougeL_f",
        "token_ratio",
        "length_penalty",
        "cosine_similarity",
        "hallucination_score",
        "quality_score",
        "ghostwire_score",
    ]
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
        writer.writeheader()
        for row in results:
            writer.writerow({k: row.get(k, "") for k in csv_headers})
    print("📊 Results saved to summarization_benchmark_results.csv")
    return results


if __name__ == "__main__":
    asyncio.run(run_summarization_benchmark())
