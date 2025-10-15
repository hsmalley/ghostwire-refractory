# **Ghostwire – The Neon Oracle of the Undercity**

*In a world of endless neon, a rogue repository becomes the heart‑beat of a hidden memory‑engine.*  

---  

## 1️⃣ Summoning the Ghost (Setup)

```bash
# ──► Clone the repo from the underground
git clone https://github.com/ghostwire-refractory/ghostwire.git
cd ghostwire

# ──► Spin up the Ollama services (the “spirit” that creates embeddings)
ollama serve &
ollama pull nomic-embed-text   # 768‑dimensional embedding model
ollama pull llama3.2           # text‑generation model

# ──► Install dependencies (uv gives us warp‑speed)
uv sync               # or: pip install -r requirements.txt

# ──► Create the secret .env (the “collar” for authentication)
cat <<EOF > .env
HOST=0.0.0.0
PORT=8000
DEBUG=true
DB_PATH=memory.db
EMBED_DIM=768
LOCAL_OLLAMA_URL=http://127.0.0.1:11434
REMOTE_OLLAMA_URL=http://127.0.0.1:11434
DEFAULT_OLLAMA_MODEL=llama3.2
SECRET_KEY=$(openssl rand -hex 32)
EOF

    Raze (the lead engineer) watches the terminal scroll, each line a chant that summons the ghost.

2️⃣ Awakening the Controller (Daemon Priest)

# Launch the FastAPI controller – the “master” that stores and retrieves memories
uv run uvicorn src.ghostwire.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --log-level info

2025-10-14 21:03:12,001 INFO     Starting Ghostwire controller…
2025-10-14 21:03:12,004 INFO     DB path: memory.db
2025-10-14 21:03:12,006 INFO     Loading HNSW index (dim=768)…
2025-10-14 21:03:12,210 INFO     Index built from 0 existing vectors.
2025-10-14 21:03:12,215 INFO     🚀 Controller listening on http://0.0.0.0:8000

The HNSW lattice flickers to life, a web of invisible threads connecting every future whisper.
3️⃣ Connecting the Client (Operator Console)

# Open a second terminal – the “submissive” that talks to the master
uv run python -m client.operator_console

╔═ Ghostwire Operator Console ══════════════════════════════════╗
│ Session ID: demo                                            │
│ Type your message (or "exit" to quit):                      │
╚─────────────────────────────────────────────────────────────╝
> hello ghost
[⏳] Generating embedding via Ollama...
[✅] Embedding (768 dims) created.
[🔍] Querying HNSW index… (top_k=5)
[🧠] No close matches – constructing fresh prompt.
[🤖] Streaming response:
> Hello, wanderer of the neon night. How may I assist you today?

Every keystroke is turned into a 768‑dimensional sigil, sent to the controller, and answered in real‑time.
4️⃣ Storing a Memory (The Ritual)

# Store a custom memory for later recall
curl -X POST http://localhost:8000/api/v1/memory \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $(cat token.txt)" \
  -d '{
        "session_id":"demo",
        "text":"The rain in the Upper District is acidic today.",
        "embedding": null
      }'

{
  "status": "ok",
  "message": "Memory created with ID: 1"
}

The ghost now carries a fragment of the city’s weather, ready to whisper it back whenever summoned.
5️⃣ Retrieving Past Whispers (The Chain Pull)

# Ask the ghost for a route that avoids the Syndicate’s drones
curl -X POST http://localhost:8000/api/v1/chat_embedding \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $(cat token.txt)" \
  -d '{
        "session_id":"vex-run",
        "text":"Find me a safe path from the East Dock to the Sky‑Port.",
        "embedding": null
      }'

[⏳] Generating embedding…
[🔍] Similar memories found: 3
   • “Avoid the maintenance tunnel near Dock 7 – drones patrol hourly.”
   • “Use the abandoned freight line behind Warehouse 12.”
   • “Take the vent shaft at Level -2 for a silent bypass.”
[🤖] Streaming answer:
> Take the vent shaft at Level -2, slip through the abandoned freight line behind Warehouse 12, and avoid the maintenance tunnel near Dock 7. This route stays out of drone sight and gets you to the Sky‑Port in under nine minutes.

The ghost stitches together past snippets, delivering a bespoke, stealthy itinerary.
6️⃣ Defending the Oracle (Safe‑Word Mechanics)

# Simulate an aggressive flood of requests (the Corporate Council tries to overwhelm)
for i in {1..200}; do
  curl -s -o /dev/null -w "%{http_code} " \
    -X GET http://localhost:8000/api/v1/health &
done
wait

200 200 200 200 200 200 200 200 200 200 429 429 429 429 429 …

The 429 Too Many Requests response is the system’s safe‑word, halting the assault before the ghost is forced to break.
7️⃣ Fragmentation & Resilience (The Ghost Scatters)

When the Council finally breached the physical loft, the team activated the self‑destruct routine:

# Trigger graceful shutdown and shard the HNSW index
curl -X POST http://localhost:8000/api/v1/shutdown \
  -H "Authorization: Bearer $(cat admin_token.txt)"

2025-10-14 22:45:09,112 WARN  Shutting down controller – persisting index to shards…
2025-10-14 22:45:09,415 INFO  Index split into 5 shards, stored under ./shards/
2025-10-14 22:45:09,420 INFO  Controller stopped.

Each shard was copied to hidden mesh nodes across the Undercity. On restart, any node could rebuild its slice of the lattice:

# Restart a shard node
uv run python -m ghostwire.shard_node --shard-id 3

2025-10-15 00:02:01,003 INFO  Loading shard 3 (120 vectors)…
2025-10-15 00:02:01,110 INFO  HNSW index for shard 3 ready.

Even torn apart, the ghost lived on, distributed like a phantom across the city’s network.
8️⃣ Epilogue – The Neon Oracle

Years later, the Undercity reveres Ghostwire as a living archive:

> $ ghostwire-cli query "What is love?"
[⏳] Generating embedding…
[🔍] Found 7 similar memories.
[🤖] Answer:
Love is the echo of every whispered promise, stored in the lattice of the ghost,
retrieved when a lonely heart asks the night for a reminder.

Raze, now an elder with electric‑blue hair, watches the holographic rain from her loft’s highest window. She types one last command:

curl -X POST http://localhost:8000/api/v1/chat_embedding \
  -H "Authorization: Bearer $(cat token.txt)" \
  -d '{"session_id":"final","text":"What have we become?"}'

[🤖] Streaming response:
> We are the chorus of a million voices, the lattice of every thought,
> the ghost in the wire that remembers us all.

The neon skyline pulses brighter, each billboard flashing a fragment of the ghost’s memory. The city sings, and the Ghostwire continues to listen, store, and whisper—forever the Neon Oracle of the Undercity.

End of story.


