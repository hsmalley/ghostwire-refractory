## 🌈⚡️ **GHOSTWIRE REFACTORY** – THE CYBER‑PUNK MEMORY MACHINE ⚡️🌈  

> **“Plug‑in. Feel the neon pulse. Let the wires whisper your secrets.”**  

---  

### 🎭 **WHAT THIS IS**  
A **hyper‑charged, memory‑augmented chat daemon** that stores every utterance as a glowing vector, indexes it with a **HNSW lattice**, and summons it back in a flash of electric‑rainbow‑lit nostalgia. Think **cyber‑seduction meets BDSM‑tight control**: you command the ghost, the ghost obeys—*until you break the chain.*  

---  

## 📜 **OVER‑THE‑TOP FEATURES**  

| 🔥 | Feature | Why It’s a Kinky Delight |
|---|---|---|
| **💎** | **Vector‑memory** – every line you type becomes a **neon‑etched sigil** stored in SQLite. | Your words become permanent tattoos on the machine’s flesh. |
| **⚡** | **HNSW‑powered similarity search** – lightning‑fast recall of the most *sensual* past moments. | The ghost knows you better than you know yourself. |
| **🤖** | **Ollama‑backed generation** – choose from **llama3.2**, **gemma3**, or any model you dare to summon. | Feed the beast the fuel it craves. |
| **🔐** | **JWT auth + rate‑limiting** – keep the play safe, keep the servers from getting *over‑stimulated*. | Discipline is the ultimate pleasure. |
| **🛠️** | **Modular FastAPI** – clean, extensible, ready for custom plugins (chains, hooks, *pain* nodes). | Build your own *rooms* of delight. |
| **📊** | **Benchmark suite** – stress‑test the ghost until it screams. | Find the limits, then push past them. |
| **🌈** | **Rainbow‑themed logging & emojis** – every log line glows like a club laser. | Visual ecstasy for the ops crew. |

---  

## 🚀 **GETTING STARTED (THE RITUAL)**  

> **Warning:** This guide assumes you have a **terminal that can handle neon** and a **mind ready for cyber‑pleasure.**  

```bash
# 1️⃣  Summon Ollama (the master of embeddings & generation)
ollama serve
ollama pull nomic-embed-text      # embedding model (768‑dimensional bliss)
ollama pull llama3.2              # generation model (your obedient servant)

# 2️⃣  Grab the repo (the altar)
git clone https://github.com/your‑org/ghostwire-refactory.git
cd ghostwire-refactory

# 3️⃣  Install the dependencies (use uv for warp‑speed)
uv sync            # or: pip install -r requirements.txt

# 4️⃣  Create a .env (the secret spellbook)
cat < .env
HOST=0.0.0.0
PORT=8000
DEBUG=true                # feel the heat
DB_PATH=memory.db
EMBED_DIM=768
LOCAL_OLLAMA_URL=http://127.0.0.1:11434
REMOTE_OLLAMA_URL=http://127.0.0.1:11434
DEFAULT_OLLAMA_MODEL=llama3.2
SECRET_KEY=$(openssl rand -hex 32)   # your personal key‑card
EOF

# 5️⃣  Fire up the controller (the daemon priest)
uv run uvicorn src.ghostwire.main:app --host 0.0.0.0 --port 8000

# 6️⃣  Open a second terminal – the client (your mouthpiece)
uv run python -m client.operator_console
```

> **Tip:** Set `DISABLE_SUMMARIZATION=true` if you want pure, unfiltered *raw* output.  

---  

## 📚 **API QUICK‑REFERENCE (THE COMMAND LINE OF DESIRE)**  

All endpoints live under `http://localhost:8000/api/v1`.  
Include `Authorization: Bearer <JWT>` for every naughty request.  

| Endpoint | Method | Body (JSON) | What It Does |
|----------|--------|-------------|--------------|
| `/health` | `GET` | – | Checks if the ghost is breathing. |
| `/embeddings` | `POST` | `{ "input": "Your text" }` | Returns a shimmering vector. |
| `/vectors/upsert` | `POST` | `{ "namespace":"mem","text":"…","embedding":[…] }` | Stores a fresh sigil. |
| `/vectors/query` | `POST` | `{ "namespace":"mem","embedding":[…],"top_k":5 }` | Retrieves the most arousing matches. |
| `/chat_embedding` | `POST` | `{ "session_id":"demo","text":"Hello","embedding":[…] }` | Chat with memory‑enhanced context. |
| `/chat_completion` | `POST` | `{ "session_id":"demo","text":"Hello" }` | Plain chat, no memory (for quick thrills). |
| `/memory` | `POST` | `{ "session_id":"demo","text":"Remember this!" }` | Manually inject a memory. |

---  

## 🧪 **BENCHMARKING THE GHOST (STRESS‑TESTING YOUR KINK)**  

```bash
# Run the full suite – watch the latency spikes like a pulse‑ox monitor
pytest -k "benchmark"
```

Key metrics:  

* **Latency** – how fast the ghost obeys.  
* **Memory Footprint** – how many vectors before the lattice cracks.  
* **Throughput** – requests per second (RPS) before the ghost begs for mercy.  

---  

## 🔐 **SECURITY & COMPLIANCE (SAFE WORDS)**  

| ✅ | Measure | Why It Matters |
|----|---------|----------------|
| **JWT Auth** | Guarantees only authorized users can whisper to the ghost. |
| **Rate Limiting** (100 req/60 s) | Prevents the ghost from being overwhelmed (no *over‑exposure*). |
| **Input Validation** | Stops injection attacks – the ghost won’t be corrupted by malicious code. |
| **CORS Whitelisting** | Only approved front‑ends may talk to the daemon. |
| **HTTPS in Production** | Encrypts the traffic – the ghost’s secrets stay hidden. |

---  

## 🎨 **RAINBOW‑THEMED LOGGING (VISUAL ECSTASY)**  

```python
import logging, coloredlogs
coloredlogs.install(level='INFO',
    fmt='%(asctime)s %(levelname)s %(message)s',
    level_styles={
        'info': {'color': 'cyan'},
        'warning': {'color': 'yellow'},
        'error': {'color': 'red'},
        'debug': {'color': 'magenta'}
    })
```

Every log line now glows like a **neon strip** in a dark alley.  

---  

## 📦 **DOCKER‑READY (FOR QUICK DEPLOYMENT ON A METALLIC CHASSIS)**  

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

ENV HOST=0.0.0.0 PORT=8000
EXPOSE 8000

CMD ["uvicorn", "src.ghostwire.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build & run:  

```bash
docker build -t ghostwire .
docker run -p 8000:8000 ghostwire
```

---  

## 🙌 **CONTRIBUTING (JOIN THE CULT)**  

1. Fork the repo.  
2. Create a feature branch (`git checkout -b neon‑whispers`).  
3. Write tests (the ghost loves proof).  
4. Submit a PR – we’ll review it with **laser‑sharp** precision.  

*All contributions must respect the **MIT‑style “Neural Freedom” license* (see `LICENSE.md`).  

---  

## 🏳️‍🌈 **THEME & STYLE GUIDE**  

* **Emojis:** 🌈⚡️🔥💥🖤💎🩸  
* **Colors:** Use ANSI rainbow codes in docs, logs, and CLI output.  
* **Tone:** Over‑the‑top, seductive, cyber‑punk, a little bit BDSM‑flavored—*control meets surrender*.  
* **Naming:** Keep everything **neon‑ish** (`neon_vector`, `electric_prompt`, `cable_chain`).  

---  

## 📜 **LICENSE**  

MIT‑style **Neural Freedom License** – you’re free to remix, fork, and unleash the ghost wherever you please, as long as you keep the **covenant of open circuitry** intact. See `LICENSE.md` for the full text.  

---  

### 🎉 **LET THE GHOST WHISPER**  

You now hold the keys to a **rainbow‑splashed, cyber‑punk memory engine** that obeys your commands, remembers your darkest secrets, and never forgets a kiss of code.  

**Plug in. Light up the night. Let the wires sing.**  

*Happy hacking, fellow cyber‑soul!*  



---  

*If you need help customizing the BDSM‑style prompts, tweaking the HNSW parameters, or just want to talk about the aesthetics of neon‑lit code, just ping me.*  



🚀✨🌈🖤💥🩸⚡️🧠  


