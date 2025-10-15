"""
Document service for GhostWire Refractory to handle document ingestion and chunking
"""

import hashlib
import logging
from pathlib import Path

from ..models.memory import MemoryCreate
from ..services.embedding_service import embedding_service
from ..services.memory_service import memory_service
from ..utils.error_handling import EmbeddingError


class DocumentChunker:
    """Handles chunking of documents into smaller pieces for embedding"""

    def __init__(self, max_chunk_size: int = 512, overlap_size: int = 50):
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size

    def chunk_text(self, text: str, source: str = "unknown") -> list[dict]:
        """
        Chunk text into smaller pieces with overlap
        """
        if not text:
            return []

        # Split text into sentences first to avoid breaking sentences
        sentences = self._split_sentences(text)

        chunks = []
        current_chunk = ""
        current_position = 0

        for sentence in sentences:
            # If adding the sentence would exceed chunk size
            if len(current_chunk) + len(sentence) > self.max_chunk_size:
                # Save current chunk if it's substantial
                if len(current_chunk) > self.overlap_size:
                    chunks.append(
                        {
                            "content": current_chunk.strip(),
                            "position": current_position,
                            "source": source,
                        }
                    )

                    # Add overlap by taking the last part of the chunk
                    if self.overlap_size > 0:
                        overlap_start = max(0, len(current_chunk) - self.overlap_size)
                        current_chunk = current_chunk[overlap_start:]
                    else:
                        current_chunk = ""

                # If the new sentence is still too big, we'll need to split it
                if len(sentence) > self.max_chunk_size:
                    sub_chunks = self._split_large_sentence(sentence)
                    for sub_chunk in sub_chunks[:-1]:  # Add all but the last
                        chunks.append(
                            {
                                "content": sub_chunk.strip(),
                                "position": current_position + len(current_chunk),
                                "source": source,
                            }
                        )
                    # Add the last sub-chunk to the current chunk for potential combination
                    if sub_chunks:
                        current_chunk = current_chunk + sub_chunks[-1]
                else:
                    current_chunk = current_chunk + sentence
            else:
                current_chunk = current_chunk + sentence

        # Add the final chunk if it has content
        if current_chunk.strip():
            chunks.append(
                {
                    "content": current_chunk.strip(),
                    "position": current_position,
                    "source": source,
                }
            )

        return chunks

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences"""
        import re

        # Split on sentence endings, preserving the punctuation
        sentences = re.split(r"(?<=[.!?])\s+", text)
        # Add the sentence ending back to each sentence except the last one
        result = []
        for i, sentence in enumerate(sentences):
            if i < len(sentences) - 1:
                result.append(
                    sentence + ". "
                )  # Add period back assuming most sentences
            else:
                result.append(sentence)
        return result

    def _split_large_sentence(self, sentence: str) -> list[str]:
        """Split a sentence that's too large into smaller chunks"""
        if len(sentence) <= self.max_chunk_size:
            return [sentence]

        chunks = []
        for i in range(0, len(sentence), self.max_chunk_size - self.overlap_size):
            chunk = sentence[i : i + self.max_chunk_size]
            chunks.append(chunk)
        return chunks


class DocumentService:
    """Service for document ingestion, parsing, and storage"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.chunker = DocumentChunker()
        self.supported_formats = {
            ".txt": self._parse_text,
            ".md": self._parse_markdown,
            ".py": self._parse_python,
            ".js": self._parse_text,  # Could implement JavaScript-specific parsing
            ".ts": self._parse_text,  # Could implement TypeScript-specific parsing
            ".html": self._parse_html,
            ".css": self._parse_text,  # Could implement CSS-specific parsing
            ".json": self._parse_json,
            ".xml": self._parse_xml,
        }

    async def ingest_document(
        self, content: str, source: str, session_id: str, document_id: str | None = None
    ) -> list[int]:
        """
        Ingest a document and store chunks in memory
        """
        try:
            # Generate document ID if not provided
            if not document_id:
                content_hash = hashlib.md5(content.encode()).hexdigest()[:12]
                document_id = f"doc_{content_hash}"

            self.logger.info(f"Ingesting document {document_id} from {source}")

            # Apply format-specific parsing if the source has a recognizable extension
            parsed_content = content
            source_path = Path(source)
            if source_path.suffix.lower() in self.supported_formats:
                parser = self.supported_formats[source_path.suffix.lower()]
                parsed_content = parser(content)

            # Chunk the document content
            chunks = self.chunker.chunk_text(parsed_content, source)
            stored_memory_ids = []

            # Process each chunk
            for i, chunk in enumerate(chunks):
                chunk_content = chunk["content"]

                # Create memory entry for this chunk
                memory_create = MemoryCreate(
                    session_id=session_id,
                    prompt_text=chunk_content,  # Store the chunk as prompt_text
                    answer_text=f"Document chunk from {source}",  # Context about the document
                    embedding=[],  # Will be filled in below
                    summary_text=f"Document: {source}, Chunk: {i + 1}/{len(chunks)}",
                )

                # Generate embedding for the chunk content
                try:
                    embedding = await embedding_service.embed_text(chunk_content)
                    if not embedding:
                        self.logger.warning(
                            f"Failed to generate embedding for chunk {i + 1}, skipping"
                        )
                        continue
                    memory_create.embedding = embedding
                except Exception as e:
                    self.logger.error(
                        f"Error generating embedding for chunk {i + 1}: {e}"
                    )
                    continue

                # Store in memory service
                try:
                    memory = memory_service.create_memory(memory_create)
                    stored_memory_ids.append(memory.id)
                    self.logger.info(f"Stored chunk {i + 1} as memory {memory.id}")
                except Exception as e:
                    self.logger.error(
                        f"Error storing chunk {i + 1} in memory service: {e}"
                    )
                    continue

            self.logger.info(
                f"Successfully ingested document {document_id} as {len(stored_memory_ids)} chunks"
            )
            return stored_memory_ids

        except Exception as e:
            self.logger.error(f"Error ingesting document: {e}")
            raise

    async def ingest_document_from_path(
        self, file_path: str, session_id: str, document_id: str | None = None
    ) -> list[int]:
        """
        Ingest a document from file path
        """
        try:
            path = Path(file_path)

            if not path.exists():
                raise FileNotFoundError(f"Document file not found: {file_path}")

            # Check if the format is supported
            if path.suffix.lower() not in self.supported_formats:
                raise ValueError(f"Unsupported document format: {path.suffix}")

            # Read the file content
            with open(path, encoding="utf-8") as file:
                content = file.read()

            # Apply format-specific parsing
            parser = self.supported_formats[path.suffix.lower()]
            parsed_content = parser(content)

            return await self.ingest_document(
                parsed_content, str(path), session_id, document_id
            )

        except Exception as e:
            self.logger.error(f"Error ingesting document from path {file_path}: {e}")
            raise

    def _parse_text(self, content: str) -> str:
        """
        Parse plain text documents
        """
        return content

    def _parse_python(self, content: str) -> str:
        """
        Parse Python code files, extracting function/class definitions and docstrings
        """
        try:
            import ast

            # Parse the Python code to extract functions, classes, and their docstrings
            tree = ast.parse(content)
            extracted_parts = []

            for node in ast.walk(tree):
                if isinstance(
                    node,
                    (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module),
                ):
                    # Extract the relevant code block with context
                    code_lines = content.split("\n")
                    start_line = node.lineno - 1
                    end_line = (
                        node.end_lineno
                        if hasattr(node, "end_lineno")
                        else start_line + 10
                    )
                    # Ensure we don't go beyond the content
                    end_line = min(end_line, len(code_lines))

                    # Extract code for this function/class
                    relevant_lines = code_lines[start_line:end_line]
                    extracted_parts.append("\n".join(relevant_lines).strip())

            if extracted_parts:
                return "\n\n".join(extracted_parts)
            else:
                return content
        except (SyntaxError, AttributeError, TypeError):
            # If parsing fails, return the content as is
            return content

    def _parse_json(self, content: str) -> str:
        """
        Parse JSON files, extracting structure and content
        """
        try:
            import json

            data = json.loads(content)

            # Extract key structure information but keep it readable
            def extract_structure(obj, depth=0, max_depth=3):
                if depth >= max_depth:
                    return str(obj)[:200]  # Limit deep nested structures
                if isinstance(obj, dict):
                    result = []
                    for key, value in obj.items():
                        if isinstance(value, (dict, list)):
                            result.append(
                                f"Key: {key}, Type: {type(value).__name__}, Content: {extract_structure(value, depth + 1, max_depth)}"
                            )
                        else:
                            result.append(f"Key: {key}, Value: {str(value)[:100]}")
                    return ". ".join(result)
                elif isinstance(obj, list):
                    result = []
                    for i, item in enumerate(obj[:5]):  # Limit to first 5 items
                        result.append(
                            f"Index {i}: {extract_structure(item, depth + 1, max_depth)}"
                        )
                    return ". ".join(result)
                else:
                    return str(obj)

            return extract_structure(data)
        except (ValueError, TypeError):
            # If parsing fails, return the content as is
            return content

    def _parse_html(self, content: str) -> str:
        """
        Parse HTML, extracting text content while preserving structure information
        """
        try:
            from html.parser import HTMLParser

            class HTMLTextExtractor(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.text_parts = []
                    self.title = ""
                    self.current_tag = ""

                def handle_starttag(self, tag, attrs):
                    self.current_tag = tag
                    if tag == "title":
                        self.title = ""

                def handle_endtag(self, tag):
                    if tag == "title":
                        self.current_tag = ""

                def handle_data(self, data):
                    if self.current_tag != "script" and self.current_tag != "style":
                        stripped_data = data.strip()
                        if stripped_data:
                            self.text_parts.append(stripped_data)

            extractor = HTMLTextExtractor()
            extractor.feed(content)
            return " ".join(extractor.text_parts)
        except (Exception,):
            # If parsing fails, return the content as is
            return content

    def _parse_markdown(self, content: str) -> str:
        """
        Parse Markdown, extracting headers, lists, and other structural elements
        """
        lines = content.split("\n")
        processed_lines = []

        for line in lines:
            # Add emphasis to structural elements when extracting
            if (
                line.strip().startswith("#")
                or line.strip().startswith(("- ", "* ", "+ "))
                or line.strip().startswith(("1. ", "2. ", "3. "))
                or line.strip().endswith(("?", "!", "."))
                or line.strip()
            ):  # Headers
                processed_lines.append(line.strip())

        return "\n".join(processed_lines)

    def _parse_xml(self, content: str) -> str:
        """
        Parse XML, extracting element names and text content
        """
        try:
            import xml.etree.ElementTree as ET

            root = ET.fromstring(content)

            def extract_elements(element, depth=0, max_depth=5):
                if depth >= max_depth:
                    return ""

                result = [element.tag]

                # Add attributes
                for key, value in element.attrib.items():
                    result.append(f"{key}: {value}")

                # Add text content if present
                if element.text and element.text.strip():
                    result.append(element.text.strip())

                # Recursively process children
                for child in element:
                    child_result = extract_elements(child, depth + 1, max_depth)
                    if child_result:
                        result.append(child_result)

                return " | ".join(result)

            return extract_elements(root)
        except (Exception,):
            # If parsing fails, return the content as is
            return content

    async def search_document_chunks(
        self, query: str, session_id: str, limit: int = 10
    ) -> list[dict]:
        """
        Search for document chunks similar to the query
        """
        try:
            # Generate embedding for the query
            query_embedding = await embedding_service.embed_text(query)
            if not query_embedding:
                raise EmbeddingError("Failed to generate embedding for query")

            # Query similar memories using the memory service
            from ..models.memory import MemoryQuery

            memory_query = MemoryQuery(
                session_id=session_id, embedding=query_embedding, limit=limit
            )

            memories = memory_service.query_similar_memories(memory_query)

            # Format results
            results = []
            for memory in memories:
                results.append(
                    {
                        "id": memory.id,
                        "content": memory.prompt_text,
                        "source": memory.answer_text,  # Contains document source info
                        "summary": memory.summary_text,
                        "session_id": memory.session_id,
                    }
                )

            return results

        except Exception as e:
            self.logger.error(f"Error searching document chunks: {e}")
            raise

    async def list_documents_in_session(self, session_id: str) -> list[dict]:
        """
        List all document chunks in a session
        """
        try:
            # Get all memories in the session
            memories = memory_service.get_memories_by_session(
                session_id, limit=1000
            )  # Large limit

            # Filter and format document-related memories
            documents = []
            for memory in memories:
                if memory.summary_text and memory.summary_text.startswith("Document:"):
                    documents.append(
                        {
                            "id": memory.id,
                            "content_preview": memory.prompt_text[:100] + "..."
                            if len(memory.prompt_text) > 100
                            else memory.prompt_text,
                            "source": memory.answer_text,
                            "summary": memory.summary_text,
                            "timestamp": memory.timestamp,
                        }
                    )

            return documents
        except Exception as e:
            self.logger.error(f"Error listing documents in session: {e}")
            raise


# Global instance
document_service = DocumentService()
