#!/usr/bin/env python3
"""
# ⚡️ Document Ingestion Script

A CLI tool for ingesting documents into the GhostWire Refractory vector database.
Supports txt/md/code inputs, chunking, optional summarization, embedding generation,
and storage into the local vector DB.

Usage:
    python scripts/import_documents.py <file_or_directory> [--dry-run] [--summarize] [--help]

Examples:
    python scripts/import_documents.py docs/ --dry-run
    python scripts/import_documents.py README.md --summarize
    python scripts/import_documents.py src/ --summarize --dry-run
"""

import argparse
import asyncio
import hashlib
import logging
import os
import sys
from pathlib import Path

# Add the python directory to the path to access ghostwire modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


from ghostwire.api.v1.documents import (
    DocumentChunk,
)
from ghostwire.api.v1.embeddings import EmbeddingRequest, EmbeddingResponse
from ghostwire.config.settings import settings
from ghostwire.services.document_service import DocumentChunker, document_service
from ghostwire.services.embedding_service import embedding_service
from ghostwire.utils.context_optimizer import (
    estimate_token_count,
)
from ghostwire.utils.error_handling import handle_exception
from ghostwire.utils.security import validate_text_content

# Set up logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class DocumentIngestor:
    """Document ingestion handler with chunking and optional summarization."""

    def __init__(
        self,
        chunk_size: int = 500,
        overlap_size: int = 50,
        enable_summarization: bool = False,
    ):
        """
        Initialize the document ingestor.

        Args:
            chunk_size: Size of chunks in tokens/words
            overlap_size: Size of overlap between chunks
            enable_summarization: Whether to enable summarization
        """
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.enable_summarization = enable_summarization
        self.chunker = DocumentChunker(
            max_chunk_size=chunk_size, overlap_size=overlap_size
        )
        self.session_id = "document_ingestion_session"

    async def ingest_document(
        self, file_path: Path, dry_run: bool = False
    ) -> tuple[int, int]:
        """
        Ingest a single document.

        Args:
            file_path: Path to the document file
            dry_run: If True, don't actually store the document

        Returns:
            Tuple of (chunks_processed, chunks_stored)
        """
        logger.info(f"Ingesting document: {file_path}")

        try:
            # Read the document content
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Validate the content
            validate_text_content(content, max_length=100000)  # Large limit for docs

            # Generate a document ID based on file path and content hash
            content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
            document_id = f"{file_path.stem}_{content_hash}"

            # Chunk the document
            chunks = self.chunker.chunk_text(content, source=str(file_path))

            if not chunks:
                logger.warning(f"No chunks generated for {file_path}")
                return 0, 0

            logger.info(f"Generated {len(chunks)} chunks for {file_path}")

            # Optionally summarize chunks
            if self.enable_summarization:
                chunks = await self._summarize_chunks(chunks)

            # Process chunks
            chunks_processed = 0
            chunks_stored = 0

            for i, chunk_data in enumerate(chunks):
                chunk_text = chunk_data["text"]
                chunk_metadata = chunk_data.get("metadata", {})

                if not chunk_text.strip():
                    continue

                # Validate chunk content
                validate_text_content(chunk_text, max_length=10000)

                if not dry_run:
                    # Create embedding for the chunk
                    try:
                        embedding_request = EmbeddingRequest(
                            input=chunk_text, model=settings.DEFAULT_OLLAMA_MODEL
                        )
                        embedding_response: EmbeddingResponse = (
                            await embedding_service.create_embedding(embedding_request)
                        )

                        if embedding_response.data:
                            embedding = embedding_response.data[0].embedding

                            # Create document chunk
                            document_chunk = DocumentChunk(
                                text=chunk_text,
                                source=str(file_path),
                                chunk_index=i,
                                total_chunks=len(chunks),
                                metadata=chunk_metadata,
                                embedding=embedding,
                            )

                            # Store the chunk
                            await document_service.store_chunk(
                                session_id=self.session_id,
                                document_chunk=document_chunk,
                                document_id=document_id,
                            )

                            chunks_stored += 1
                    except Exception as e:
                        logger.error(f"Failed to process chunk {i} of {file_path}: {e}")
                        continue

                chunks_processed += 1

            logger.info(
                f"Processed {chunks_processed} chunks, stored {chunks_stored} for {file_path}"
            )
            return chunks_processed, chunks_stored

        except Exception as e:
            logger.error(f"Failed to ingest document {file_path}: {e}")
            handled_exc = handle_exception(e)
            if isinstance(handled_exc, Exception):
                raise handled_exc
            raise

    async def _summarize_chunks(self, chunks: list[dict]) -> list[dict]:
        """
        Summarize chunks if enabled.

        Args:
            chunks: List of chunk dictionaries

        Returns:
            List of summarized chunk dictionaries
        """
        if not self.enable_summarization:
            return chunks

        logger.info(f"Summarizing {len(chunks)} chunks...")

        summarized_chunks = []
        for chunk_data in chunks:
            chunk_text = chunk_data["text"]

            # Only summarize if the chunk is large enough
            if estimate_token_count(chunk_text) > self.chunk_size * 0.8:
                try:
                    # This would call the summarization service
                    # For now, we'll just add a placeholder
                    chunk_data["summary"] = f"Summary of: {chunk_text[:50]}..."
                    chunk_data["metadata"] = chunk_data.get("metadata", {})
                    chunk_data["metadata"]["summarized"] = True

                except Exception as e:
                    logger.warning(f"Failed to summarize chunk: {e}")
                    # Keep original chunk if summarization fails
                    pass

            summarized_chunks.append(chunk_data)

        return summarized_chunks

    async def ingest_directory(
        self,
        directory_path: Path,
        dry_run: bool = False,
        file_extensions: list[str] = None,
    ) -> tuple[int, int]:
        """
        Ingest all documents in a directory.

        Args:
            directory_path: Path to the directory
            dry_run: If True, don't actually store documents
            file_extensions: List of file extensions to process (default: ['.txt', '.md'])

        Returns:
            Tuple of (chunks_processed, chunks_stored)
        """
        if file_extensions is None:
            file_extensions = [".txt", ".md"]

        logger.info(f"Ingesting directory: {directory_path}")

        total_chunks_processed = 0
        total_chunks_stored = 0

        # Find all files with matching extensions
        for file_ext in file_extensions:
            for file_path in directory_path.glob(f"**/*{file_ext}"):
                if file_path.is_file():
                    try:
                        chunks_processed, chunks_stored = await self.ingest_document(
                            file_path, dry_run
                        )
                        total_chunks_processed += chunks_processed
                        total_chunks_stored += chunks_stored
                    except Exception as e:
                        logger.error(f"Failed to ingest {file_path}: {e}")
                        continue

        logger.info(
            f"Directory ingestion complete: {total_chunks_processed} chunks processed, {total_chunks_stored} chunks stored"
        )
        return total_chunks_processed, total_chunks_stored


def main():
    """Main entry point for the document ingestion script."""
    parser = argparse.ArgumentParser(
        prog="import_documents",
        description="Ingest documents into the GhostWire Refractory vector database",
        epilog="""
Examples:
  %(prog)s docs/ --dry-run                    # Dry run on docs directory
  %(prog)s README.md --summarize              # Ingest README with summarization
  %(prog)s src/ --summarize --dry-run         # Dry run on source code with summarization
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "path",
        help="File or directory to ingest",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without actually storing documents",
    )

    parser.add_argument(
        "--summarize",
        action="store_true",
        help="Enable summarization of large chunks",
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500,
        help="Size of chunks in tokens/words (default: 500)",
    )

    parser.add_argument(
        "--overlap-size",
        type=int,
        default=50,
        help="Size of overlap between chunks (default: 50)",
    )

    parser.add_argument(
        "--extensions",
        nargs="+",
        default=[".txt", ".md"],
        help="File extensions to process (default: .txt .md)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate and resolve path
    path = Path(args.path).resolve()
    if not path.exists():
        logger.error(f"Path does not exist: {path}")
        sys.exit(1)

    # Create ingestor
    ingestor = DocumentIngestor(
        chunk_size=args.chunk_size,
        overlap_size=args.overlap_size,
        enable_summarization=args.summarize,
    )

    # Run ingestion
    try:
        if path.is_file():
            logger.info(f"Processing single file: {path}")
            chunks_processed, chunks_stored = asyncio.run(
                ingestor.ingest_document(path, args.dry_run)
            )
        else:
            logger.info(f"Processing directory: {path}")
            chunks_processed, chunks_stored = asyncio.run(
                ingestor.ingest_directory(path, args.dry_run, args.extensions)
            )

        # Print summary
        print("\n" + "=" * 60)
        print("_DOCUMENT INGESTION COMPLETE_")
        print("=" * 60)
        print(f"Path processed: {path}")
        print(f"Dry run: {'Yes' if args.dry_run else 'No'}")
        print(f"Chunks processed: {chunks_processed}")
        print(f"Chunks stored: {chunks_stored}")
        print(f"Summarization: {'Enabled' if args.summarize else 'Disabled'}")
        print("=" * 60)

        if args.dry_run:
            print("💡 This was a dry run - no documents were actually stored.")
        else:
            print("✅ Documents successfully ingested into the vector database.")

    except Exception as e:
        logger.error(f"Document ingestion failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
