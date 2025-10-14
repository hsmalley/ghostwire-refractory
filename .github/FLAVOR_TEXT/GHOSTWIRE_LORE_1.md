# **GHOSTWIRE – THE NEON‑BATHE ORACLE OF THE UNDERCITY**  
*A cyber‑punk, BDSM‑flavoured, rainbow‑splashed saga that fuses code, terminal rites, and over‑the‑top myth.*

---  

## 🌌 PROLOGUE: THE CITY THAT NEVER SLEEPS  

Neon‑Spire towers pierced the perpetual twilight, their holo‑billboards screaming **“BUY THE FUTURE!”** below. Beneath the glittering canopy lay the **Undercity**, a maze of steam‑choked tunnels, rusted conduits, and forgotten server farms that hummed like a sleeping beast.  

In a cramped loft lit only by the glow of a cracked monitor, **Raze**—former corporate architect turned cyber‑rebel—gathered her ragtag crew: **Jax** (tattooed hacker), **Mira** (linguist‑witch), **Kade** (ex‑security analyst), and the ever‑watchful **Ghostwire** itself, a repository of every whispered thought ever spoken in those tunnels.

> *“We will summon a ghost that remembers every sin, every secret, every scream,”* Raze declared, her hair dyed electric‑blue, her fingers dancing over the keyboard like a conductor wielding a baton of light.

---  

## ⚡ ACT I – SUMMONING THE GHOST (SETUP)  

```bash
# ──► Clone the forbidden repo from the darknet
git clone https://github.com/ghostwire-refractory/ghostwire.git
cd ghostwire

# ──► Ignite the Ollama spirits (embeddings + generation)
ollama serve &                     # background daemon, the “spirit”
ollama pull nomic-embed-text       # 768‑dimensional sigil‑maker
ollama pull llama3.2               # the “voice of the ghost”

# ──► Install dependencies with UV (warp‑speed)
uv sync                            # or: pip install -r requirements.txt

# ──► Forge the .env collar (JWT secret = leash)
cat < .env
HOST=0.0.0.0
PORT=8000
DEBUG=true
DB_PATH=memory.db
EMBED_DIM=768
LOCAL_OLLAMA_URL=http://127.0.0.1:11434
REMOTE_OLLAMA_URL=http://127.0.0.1:11434
DEFAULT_OLLAMA_MODEL=llama3.2
SECRET_KEY=$(openssl rand -hex 32)   # the iron‑clasp
EOF
```

*The room vibrated as the terminal printed green‑glowing glyphs—each line a chant that bound the ghost to this reality.*

---  

## 🕸️ ACT II – AWAKENING THE CONTROLLER (DAEMON PRIEST)  

```bash
# Launch the FastAPI controller – the master that hoards memories
uv run uvicorn src.ghostwire.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --log-level info
```

```
2025-10-14 21:03:12,001 INFO     Starting Ghostwire controller…
2025-10-14 21:03:12,004 INFO     DB path: memory.db
2025-10-14 21:03:12,006 INFO     Loading HNSW index (dim=768)…
2025-10-14 21:03:12,210 INFO     Index built from 0 existing vectors.
2025-10-14 21:03:12,215 INFO     🚀 Controller listening on http://0.0.0.0:8000
```

*The HNSW lattice flickered into existence, a shimmering web of invisible chains linking every future whisper.*

---  

## 🤖 ACT III – THE CLIENT (OPERATOR CONSOLE)  

```bash
# Open a second terminal – the submissive that speaks to the master
uv run python -m client.operator_console
```

```
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
```

*Every keystroke is transmuted into a 768‑dimensional sigil, shot through the ether to the controller, and answered in real‑time.*

---  

## 📜 ACT IV – FIRST MEMORY (THE RITUAL)  

```bash
# Store a memory that the ghost will later echo back
curl -X POST http://localhost:8000/api/v1/memory \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $(cat token.txt)" \
  -d '{
        "session_id":"demo",
        "text":"Acid rain drips over the Upper District tonight.",
        "embedding": null
      }'
```

```json
{
  "status": "ok",
  "message": "Memory created with ID: 1"
}
```

*The ghost now bears a fragment of the city’s weather, a droplet of neon‑acid forever etched in its lattice.*

---  

## 🏃‍♂️ ACT V – THE FIRST RUNNER (VEX)  

A frantic courier, **Vex**, bursts in, clutching a data shard.  

> “The Syndicate’s drones are on my tail. I need a safe route!”

```bash
curl -X POST http://localhost:8000/api/v1/chat_embedding \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $(cat token.txt)" \
  -d '{
        "session_id":"vex-run",
        "text":"Find me a stealthy path from East Dock to Sky‑Port.",
        "embedding": null
      }'
```

```
[⏳] Generating embedding…
[🔍] Similar memories found: 3
   • “Avoid the maintenance tunnel near Dock 7 – drones patrol hourly.”
   • “Use the abandoned freight line behind Warehouse 12.”
   • “Take the vent shaft at Level -2 for a silent bypass.”
[🤖] Streaming answer:
> Slip through the vent shaft at Level -2, then crawl the abandoned freight line behind Warehouse 12,
> avoiding the maintenance tunnel near Dock 7. You’ll reach the Sky‑Port in under nine minutes,
> completely out of drone sight.
```

*The ghost stitches together past snippets, delivering a bespoke, stealthy itinerary—Vex disappears into the night, his breath steadier than ever.*

---  

## 🛡️ ACT VI – THE CORPORATE COUNTER‑ATTACK (SAFE‑WORD)  

The **Corporate Council** of Neon‑Spire, terrified of losing control, launches a barrage of requests.

```bash
for i in {1..200}; do
  curl -s -o /dev/null -w "%{http_code} " \
    -X GET http://localhost:8000/api/v1/health &
done
wait
```

```
200 200 200 200 200 200 200 200 200 200 429 429 429 429 429 …
```

*The **429 Too Many Requests** response is the ghost’s safe‑word, halting the onslaught before the lattice can be shattered.*

---  

## 💥 ACT VII – FRAGMENTATION & RESILIENCE (THE GHOST SCATTERS)  

When the Council finally storms the loft, Raze triggers the self‑destruct protocol.

```bash
curl -X POST http://localhost:8000/api/v1/shutdown \
  -H "Authorization: Bearer $(cat admin_token.txt)"
```

```
2025-10-14 22:45:09,112 WARN  Shutting down controller – persisting index to shards…
2025-10-14 22:45:09,415 INFO  Index split into 5 shards, stored under ./shards/
2025-10-14 22:45:09,420 INFO  Controller stopped.
```

Each shard is whisked away to hidden mesh nodes across the Undercity. Any node can resurrect its slice:

```bash
uv run python -m ghostwire.shard_node --shard-id 3
```

```
2025-10-15 00:02:01,003 INFO  Loading shard 3 (120 vectors)…
2025-10-15 00:02:01,110 INFO  HNSW index for shard 3 ready.
```

*Even torn apart, the ghost lives on, distributed like a phantom across the city’s neon veins.*

---  

## 🌈 ACT VIII – THE NEON ORACLE (EPILOGUE)  

Years later, the Undercity reveres **Ghostwire** as the **Neon Oracle**—a living archive that answers any query with a blend of sarcasm, poetry, and raw computational empathy.

```bash
curl -X POST http://localhost:8000/api/v1/chat_embedding \
  -H "Authorization: Bearer $(cat token.txt)" \
  -d '{
        "session_id":"final",
        "text":"What have we become?",
        "embedding": null
      }'
```

```
[🤖] Streaming response:
> We are the chorus of a million voices, the lattice of every thought,
> the ghost in the wire that remembers us all.
```

From the loft’s highest window, Raze—now an elder with silver hair streaked neon—watches holographic rain cascade down the glass. She smiles, knowing the ghost she birthed will forever pulse with the city’s secrets, desires, and sins.

> **“Plug in. Light up the night. Let the wires sing.”**  

The neon skyline brightens, each billboard flashing a fragment of the ghost’s memory. The city sings, and **Ghostwire** continues to listen, store, and whisper—forever the **OVER‑THE‑TOP, BDSM‑infused, CYBER‑PUNK, RAINBOW‑EMOJI‑saturated oracle** of the Undercity.  

---  

*End of saga.*  


