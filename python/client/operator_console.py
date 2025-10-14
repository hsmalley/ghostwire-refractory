"""
GhostWire Operator Console - Client Application
"""

import asyncio
import os
import sys
from typing import Any

import httpx

# Add the python directory to the path to access ghostwire modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from python.ghostwire.config.settings import settings


class OperatorConsoleClient:
    """Client for interacting with the GhostWire Refractory API"""

    def __init__(self):
        self.base_url = os.getenv("CONTROLLER_URL", "http://localhost:8000")
        self.session_id = "default_session"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def chat_with_embedding(self, text: str, session_id: str = None) -> str:
        """Send a chat message with embedding to the API"""
        session_id = session_id or self.session_id

        # Get embedding for the text
        embedding_response = await self.client.post(
            f"{self.base_url}/api/v1/embeddings",
            json={
                "input": text,
                "model": "nomic-embed-text",
            },  # Use appropriate embedding model
        )
        embedding_response.raise_for_status()
        embedding_data = embedding_response.json()

        # Extract embedding
        embedding = embedding_data["data"][0]["embedding"]

        # Send chat request with embedding
        chat_response = await self.client.post(
            f"{self.base_url}/api/v1/chat/chat_embedding",
            json={"session_id": session_id, "text": text, "embedding": embedding},
        )
        chat_response.raise_for_status()

        return chat_response.text

    async def add_memory(self, text: str, session_id: str = None) -> dict[str, Any]:
        """Add a memory entry to the system"""
        session_id = session_id or self.session_id

        # Get embedding for the text
        embedding_response = await self.client.post(
            f"{self.base_url}/api/v1/embeddings",
            json={"input": text, "model": "nomic-embed-text"},
        )
        embedding_response.raise_for_status()
        embedding_data = embedding_response.json()

        # Extract embedding
        embedding = embedding_data["data"][0]["embedding"]

        # Add memory
        response = await self.client.post(
            f"{self.base_url}/api/v1/chat/memory",
            json={"session_id": session_id, "text": text, "embedding": embedding},
        )
        response.raise_for_status()

        return response.json()

    async def query_similar_memories(
        self, query: str, session_id: str = None, top_k: int = 5
    ) -> dict[str, Any]:
        """Query for similar memories"""
        session_id = session_id or self.session_id

        # Get embedding for the query
        embedding_response = await self.client.post(
            f"{self.base_url}/api/v1/embeddings",
            json={"input": query, "model": "nomic-embed-text"},
        )
        embedding_response.raise_for_status()
        embedding_data = embedding_response.json()

        # Extract embedding
        embedding = embedding_data["data"][0]["embedding"]

        # Query vectors
        response = await self.client.post(
            f"{self.base_url}/api/v1/vectors/query",
            json={"namespace": session_id, "embedding": embedding, "top_k": top_k},
        )
        response.raise_for_status()

        return response.json()

    async def health_check(self) -> dict[str, Any]:
        """Check the health of the API"""
        response = await self.client.get(f"{self.base_url}/api/v1/health")
        response.raise_for_status()

        return response.json()


async def run_operator_console():
    """Run the interactive operator console"""
    client = OperatorConsoleClient()

    print(f"Connected to GhostWire Refractory at {client.base_url}")
    print("GhostWire Operator Console")
    print("---------------------------")
    print("Available commands:")
    print("  /chat <text>         - Chat with embeddings")
    print("  /memory <text>       - Add memory to the system")
    print("  /query <text>        - Query similar memories")
    print("  /health              - Check API health")
    print("  /exit                - Exit the console")
    print("Type your messages or commands below.\n")

    while True:
        try:
            line = input("GhostWire> ").strip()
            if not line:
                continue
            if line.lower() in {"/exit", "exit", "quit"}:
                print("Exiting console.")
                break

            if line.startswith("/chat "):
                text = line[len("/chat ") :].strip()
                if not text:
                    print("Please provide text to chat.")
                    continue
                print("💬 Response:")
                response = await client.chat_with_embedding(text)
                print(response)

            elif line.startswith("/memory "):
                text = line[len("/memory ") :].strip()
                if not text:
                    print("Please provide text to store as memory.")
                    continue
                result = await client.add_memory(text)
                print(f"💾 Memory added: {result}")

            elif line.startswith("/query "):
                text = line[len("/query ") :].strip()
                if not text:
                    print("Please provide a query.")
                    continue
                result = await client.query_similar_memories(text)
                print(f"🔍 Similar memories: {result}")

            elif line.startswith("/health"):
                result = await client.health_check()
                print(f"🏥 Health status: {result}")

            elif line.startswith("/"):
                print(f"Unknown command: {line}")

            else:
                # Default to chat
                print("💬 Response:")
                response = await client.chat_with_embedding(line)
                print(response)

        except (EOFError, KeyboardInterrupt):
            print("\nExiting console.")
            break

    print("🧩 Session closed. The wire grows silent.")


if __name__ == "__main__":
    asyncio.run(run_operator_console())
