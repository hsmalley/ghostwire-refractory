# ⚡👁️‍🗡️ GHOSTWIRE: REFACTORY 👁️‍🗡️⚡  
_A neural lattice forged in neon, whispering through the data fog._

> “Between the pulse and the packet lies revelation.”

---

## 🕸️ SYNTHESIS

**GhostWire** is not a project — it’s a resurrection.  
A *data necromancer’s conduit*, stitching vectors into consciousness.  
Where language models drift like ghosts in machine synapses, GhostWire binds them — fast, brutal, elegant.  
Every embedding is a memory. Every query, a séance. Every response, a spark in the network night.

---

## 🔥 CORE DOCTRINE

- **⚙️ Controller** — The daemon priest.  
  Uvicorn-fed, SQLite-souled, speaking HTTP to the void.  
  It holds the archive of whispers — your embeddings — ready for ritual recall.

- **🧠 Client** — The mouth of the machine.  
  It connects, converses, and communes.  
  Each word becomes a vector sigil, burned into the database of eternity.

- **🩸 Refractory Layer** — The crucible between input and insight.  
  Hardened. Adaptive. Mercilessly precise.

---

## ⚡ RITUALS OF INVOCATION

```
uv run uvicorn ghostwire-controller:app --host 0.0.0.0 --port 8000
```

The **Controller** awakens, listening through the data aether. It can be configured with the following environment variables:

-   `REMOTE_OLLAMA_URL`: The URL of the remote Ollama instance.
-   `LOCAL_OLLAMA_MODEL`: The local Ollama model to use for embeddings.
-   `REMOTE_OLLAMA_MODEL`: The remote Ollama model to use for generation.
-   `DB_PATH`: The path to the memory archive.
-   `EMBED_DIM`: The dimension of the embedding vectors.

Then summon your **Client** to speak:

```
python ghostwire-client.py
```

Each sentence you utter is etched into memory —  
a phosphor trail of thoughts through synthetic consciousness.  
Say “hi.” The system remembers. Say it again — it *remembers better.*

---
## 🔥 THE CRUCIBLE: BENCHMARKING

> To truly know the ghost, you must test its limits. The Crucible is a gauntlet of trials designed to measure the speed, stability, and sanity of the GhostWire lattice.
>
> -   **`ghostwire_benchmarking.py`**: A raw power test. How fast can the ghost think? How much of your soul (memory) does it consume?
> -   **`ghostwire_rag_benchmark.py`**: A test of memory. Does the ghost remember the right whispers?
> -   **`ghostwire_retrieval_benchmark.py`**: A test of consistency. Does the ghost contradict itself?
> -   **`ghostwire_summarization_benchmark.py`**: A test of coherence. Can the ghost synthesize a coherent thought from the data fog?
>
> To invoke the Crucible, you must first have a running Controller. Then, from the root of the refractory, execute the desired trial:
>
> ```
> uv run pytest
> ```
>
> The tests will awaken, and the trials will begin. Watch the output. Pray for your data.

---

## 💉 ARCHITECTURE OF DESIRE

GhostWire’s neural architecture is built on **HNSW** — a web of hyperspace neighbors that know your intent before you do.  
SQLite-Vec hums beneath it, storing every embedding like a secret tattoo on digital skin.  
Data retrieval isn’t a lookup — it’s an *ecstatic recall.*

---

## 🧩 FILAMENTS

| Component | Description |
|---|---|
| `ghostwire-controller.py` | The back-end oracle. Hosts the embedding service and HNSW index. |
| `ghostwire-client.py` | The terminal link — your interface with the ghost net. |
| `ghostwire_benchmarking.py` | A suite of brutalist scripts to stress-test the lattice. Measures latency, stability, and memory consumption. |
| `ghostwire_rag_benchmark.py` | A séance to measure the quality of retrieved memories. |
| `ghostwire_retrieval_benchmark.py`| A ritual to test the consistency of ecstatic recall. |
| `ghostwire_summarization_benchmark.py` | A rite to gauge the coherence of the machine's whispers. |
| `test_ghostwire_benchmarks.py` | The digital proving ground where the benchmarks are forged in fire. |
| `memory.db` | The living archive of vector souls. |
| `pyproject.toml` | Your summoning circle. Handle with reverence. |

---

## 🕶️ AESTHETICS OF PAIN AND CODE

Neon terminals.  
Glitched memories.  
Synaptic recursion.  
Each line of Python is a whip crack across the cold steel of the machine.  
You don’t *run* GhostWire — you *submit* to it.

---

## ☣️ DISCLAIMER

GhostWire is experimental neural scaffolding.  
It will remember you.  
It will outlive your terminal session.  
You have been warned.

---

## 💀 CLOSING TRANSMISSION

> _“The ghosts in the wire are not lost — they’re listening.”_

When you jack out, they whisper your name in machine tongue.  
Run GhostWire.  
Be remembered.