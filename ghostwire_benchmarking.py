import argparse
import asyncio
import time

import httpx
import numpy as np
import psutil

# USAGE:
# python ghostwire-benchmarking.py --controller http://localhost:8000 --repeat 1000000
# python ghostwire-benchmarking.py --controller http://localhost:8000 --threads 16 --repeat 100

OLLAMA_URL = "http://localhost:11434"
CONTROLLER_URL = "http://localhost:8000"
MODELS = [
    "embeddinggemma",
    "granite-embedding",
    "nomic-embed-text",
    "mxbai-embed-large",
    "snowflake-arctic-embedz",
    "all-minilm",
    "gemma3:1b",
    "gemma3n:e2b",
    "gemma3n:e4b",
]

TEXTS = {
    "short": "The quick brown fox jumps over the lazy dog.",
    "medium": " ".join(["The quick brown fox jumps over the lazy dog."] * 50),
    "long": " ".join(["The quick brown fox jumps over the lazy dog."] * 400),
}

CONTROLLER_ROUTES = []


# =========================
# Embedding helpers
# =========================
async def embed_text(model: str, text: str):
    async with httpx.AsyncClient(timeout=30.0) as client:
        start = time.perf_counter()
        resp = await client.post(
            f"{OLLAMA_URL}/api/embeddings", json={"model": model, "prompt": text}
        )
        latency = time.perf_counter() - start
        resp.raise_for_status()
        data = resp.json()
        vec = np.array(data.get("embedding", []))
        return latency, vec


def compute_ghostwire_score(latency, stability, mem_usage):
    return 0.5 * (1 / (1 + latency)) + 0.3 * stability + 0.2 * (1 / (1 + mem_usage))


# =========================
# Controller detection
# =========================
async def detect_controller_routes():
    global CONTROLLER_ROUTES
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{CONTROLLER_URL}/openapi.json")
            resp.raise_for_status()
            openapi_data = resp.json()
            routes = list(openapi_data.get("paths", {}).keys())
            CONTROLLER_ROUTES = [
                r for r in routes if "embed" in r or "chat_embedding" in r
            ]
            print(f"Controller embedding route(s): {CONTROLLER_ROUTES}")
    except Exception as e:
        print(f"[WARN] Could not auto-detect controller routes: {e}")
        CONTROLLER_ROUTES = ["/chat_embedding"]


# =========================
# Controller benchmark
# =========================
async def controller_embed(text: str):
    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = {
            "model": "granite-embedding",  # adjust if your controller uses a different embedding model
            "input": text,
        }

        start = time.perf_counter()
        resp = await client.post(f"{CONTROLLER_URL}/v1/embeddings", json=payload)
        latency = time.perf_counter() - start

        print(f"[DEBUG] controller /v1/embeddings returned {resp.status_code}")
        if not resp.text.strip():
            raise RuntimeError("Empty response from controller /v1/embeddings")

        resp.raise_for_status()
        try:
            data = resp.json()
        except Exception as e:
            print(f"[ERROR] Failed to parse JSON from /v1/embeddings: {e}")
            print(f"[DEBUG] Raw body: {resp.text[:200]!r}")
            raise

        vec_data = data.get("data", [{}])[0].get("embedding")
        if vec_data is None:
            raise RuntimeError("Controller returned null embedding (no data computed)")
        vec = np.array(vec_data)
        if len(vec) == 0:
            raise RuntimeError("Controller returned no embedding data")

        return latency, vec


async def run_controller_benchmark():
    print(f"\n🌐 Running controller benchmark phase...")
    print(f"🔍 Starting benchmark for controller at {CONTROLLER_URL}")
    print("=" * 80)
    await detect_controller_routes()

    results = []
    for label, text in TEXTS.items():
        try:
            before_mem = psutil.virtual_memory().used / (1024**3)
            latency, vec = await controller_embed(text)
            after_mem = psutil.virtual_memory().used / (1024**3)
            mem_diff = after_mem - before_mem
            dim = len(vec)
            results.append((label, latency, dim, mem_diff))
            ghostwire_score = compute_ghostwire_score(latency, 1.0, mem_diff)
            print(
                f"  {label:<8} | {latency:.3f}s | dim={dim} | Δmem={mem_diff:.3f} GB | Ghostwire={ghostwire_score:.3f}"
            )
        except Exception as e:
            print(f"  {label:<8} | ERROR: {e}")

    print("\n✅ Controller benchmark complete.\n")
    print(
        f"{'Text Size':<10}{'Latency(s)':<12}{'Dim':<10}{'ΔMem(GB)':<10}{'Ghostwire':<10}"
    )
    print("-" * 70)
    for label, latency, dim, mem_diff in results:
        ghostwire_score = compute_ghostwire_score(latency, 1.0, mem_diff)
        print(
            f"{label:<10}{latency:<12.3f}{dim:<10}{mem_diff:<10.3f}{ghostwire_score:<10.3f}"
        )
    return results


# =========================
# Ollama benchmark
# =========================
async def run_benchmark():
    print(f"🔍 Starting benchmark for models: {MODELS}")
    print("=" * 80)
    results = []
    for model in MODELS:
        print(f"\n📦 Testing model: {model}")
        for label, text in TEXTS.items():
            try:
                before_mem = psutil.virtual_memory().used / (1024**3)
                latency, vec = await embed_text(model, text)
                after_mem = psutil.virtual_memory().used / (1024**3)
                mem_diff = after_mem - before_mem
                ghostwire_score = compute_ghostwire_score(latency, 1.0, mem_diff)
                results.append((model, label, latency, len(vec), mem_diff))
                print(
                    f"  {label:<8} | {latency:.3f}s | dim={len(vec)} | Δmem={mem_diff:.3f} GB | Ghostwire={ghostwire_score:.3f}"
                )
            except Exception as e:
                print(f"  {label:<8} | ERROR: {e}")

    print("\n✅ Benchmark complete.\n")
    print(
        f"{'Model':<20}{'Text Size':<10}{'Latency(s)':<12}{'Dim':<10}{'ΔMem(GB)':<10}"
    )
    print("-" * 60)
    for model, label, latency, dim, mem_diff in results:
        print(f"{model:<20}{label:<10}{latency:<12.3f}{dim:<10}{mem_diff:<10.3f}")
    return results


# =========================
# Stability test
# =========================
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


async def test_stability():
    print("\n🧠 Measuring embedding stability (cosine similarity across runs):")
    print("=" * 80)
    for model in MODELS:
        try:
            runs = []
            for _ in range(3):
                _, vec = await embed_text(model, TEXTS["short"])
                runs.append(vec)
            sims = [
                cosine_similarity(runs[i], runs[j])
                for i in range(3)
                for j in range(i + 1, 3)
            ]
            avg_sim = np.mean(sims)
            ghostwire_score = compute_ghostwire_score(
                latency=1.0, stability=avg_sim, mem_usage=0.5
            )
            print(
                f"  {model:<20} | avg cosine similarity: {avg_sim:.4f} | Ghostwire score: {ghostwire_score:.3f}"
            )
        except Exception as e:
            print(f"  {model:<20} | ERROR: {e}")


# =========================
# Concurrent benchmark
# =========================
async def run_concurrent_benchmark(num_threads: int, repeat: int):
    print(
        f"\n⚙️ Running concurrent benchmark with {num_threads} workers × {repeat} requests"
    )
    print("=" * 80)

    async def worker(worker_id: int):
        total_latency = 0
        for _ in range(repeat):
            latency, _ = await embed_text("granite-embedding", TEXTS["short"])
            total_latency += latency
        avg_latency = total_latency / repeat
        print(f"Worker {worker_id:02d} avg latency: {avg_latency:.3f}s")
        return avg_latency

    start = time.perf_counter()
    latencies = await asyncio.gather(*[worker(i) for i in range(num_threads)])
    duration = time.perf_counter() - start
    print("=" * 80)
    print(f"🏁 Completed {num_threads * repeat} requests in {duration:.2f}s total")
    print(f"🧮 Average per request: {duration / (num_threads * repeat):.4f}s")
    print(
        f"📈 Per-thread avg latency: {np.mean(latencies):.4f}s (std {np.std(latencies):.4f})"
    )


# =========================
# Main entry
# =========================
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--controller", type=str, default="http://localhost:8000")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--threads", type=int, default=1)
    args = parser.parse_args()

    CONTROLLER_URL = args.controller

    asyncio.run(run_benchmark())
    asyncio.run(test_stability())

    if args.threads > 1:
        asyncio.run(run_concurrent_benchmark(args.threads, args.repeat))

    asyncio.run(run_controller_benchmark())
