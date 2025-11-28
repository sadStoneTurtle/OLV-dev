"""Document loader utilities for RAG storybook mode"""

import os
import re
from typing import List, Dict, Any, Tuple
from pathlib import Path
from loguru import logger


def chunk_text(
    text: str,
    chunk_size: int = 300,
    chunk_overlap: int = 50,
) -> List[str]:
    """
    Split text into chunks with overlap for better context preservation.

    Args:
        text: Text to split into chunks
        chunk_size: Maximum size of each chunk in words
        chunk_overlap: Number of words to overlap between chunks

    Returns:
        List of text chunks
    """
    if not text or not text.strip():
        return []

    # Split into sentences using simple regex (handles ., !, ?, and line breaks)
    sentence_endings = r'(?<=[.!?])\s+|\n\n+'
    sentences = re.split(sentence_endings, text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return []

    chunks = []
    current_chunk = []
    current_word_count = 0

    for sentence in sentences:
        sentence_words = sentence.split()
        sentence_word_count = len(sentence_words)

        # If single sentence exceeds chunk_size, split it
        if sentence_word_count > chunk_size:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_word_count = 0

            # Split long sentence into smaller chunks
            for i in range(0, len(sentence_words), chunk_size - chunk_overlap):
                chunk_words = sentence_words[i : i + chunk_size]
                chunks.append(" ".join(chunk_words))
            continue

        # Check if adding this sentence would exceed chunk_size
        if current_word_count + sentence_word_count > chunk_size and current_chunk:
            # Save current chunk
            chunks.append(" ".join(current_chunk))

            # Start new chunk with overlap
            overlap_words = []
            overlap_count = 0
            for prev_sentence in reversed(current_chunk):
                prev_words = prev_sentence.split()
                if overlap_count + len(prev_words) <= chunk_overlap:
                    overlap_words.insert(0, prev_sentence)
                    overlap_count += len(prev_words)
                else:
                    break

            current_chunk = overlap_words
            current_word_count = overlap_count

        current_chunk.append(sentence)
        current_word_count += sentence_word_count

    # Add remaining chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def load_text_file(file_path: str) -> str | None:
    """
    Load content from a text or markdown file.

    Args:
        file_path: Path to the file to load

    Returns:
        File content as string, or None if loading fails
    """
    try:
        # Try common encodings
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]

        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    content = f.read()
                    if content.strip():
                        logger.debug(
                            f"Successfully loaded {file_path} with encoding {encoding}"
                        )
                        return content
            except UnicodeDecodeError:
                continue

        logger.warning(f"Failed to decode {file_path} with any encoding")
        return None

    except Exception as e:
        logger.error(f"Error loading file {file_path}: {e}")
        return None


def load_pdf_file(file_path: str) -> str | None:
    """
    Load content from a PDF file (optional, requires PyPDF2).

    Args:
        file_path: Path to the PDF file

    Returns:
        Extracted text content, or None if loading fails
    """
    try:
        import PyPDF2

        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text_parts = []

            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_parts.append(page.extract_text())

            content = "\n\n".join(text_parts)
            logger.debug(
                f"Successfully loaded PDF {file_path} ({len(pdf_reader.pages)} pages)"
            )
            return content

    except ImportError:
        logger.warning(
            f"PyPDF2 not installed, skipping PDF file {file_path}. "
            "Install with: uv add PyPDF2"
        )
        return None
    except Exception as e:
        logger.error(f"Error loading PDF file {file_path}: {e}")
        return None


async def load_storybook_documents(
    directory: str,
    chunk_size: int = 300,
    chunk_overlap: int = 50,
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Load all storybook documents from a directory and split into chunks.

    Args:
        directory: Path to directory containing storybook files
        chunk_size: Maximum size of each chunk in words
        chunk_overlap: Number of words to overlap between chunks

    Returns:
        Tuple of (documents, metadatas) where:
        - documents: List of text chunks
        - metadatas: List of metadata dicts for each chunk
    """
    if not os.path.exists(directory):
        logger.warning(f"Storybook directory does not exist: {directory}")
        return [], []

    if not os.path.isdir(directory):
        logger.warning(f"Storybook path is not a directory: {directory}")
        return [], []

    documents = []
    metadatas = []

    # Supported file extensions
    text_extensions = {".txt", ".md", ".markdown"}
    pdf_extensions = {".pdf"}
    supported_extensions = text_extensions | pdf_extensions

    # Walk through directory recursively
    file_count = 0
    for root, dirs, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            file_ext = Path(filename).suffix.lower()

            if file_ext not in supported_extensions:
                continue

            file_count += 1
            logger.info(f"📖 Loading storybook file: {filename}")

            # Load file content
            content = None
            if file_ext in text_extensions:
                content = load_text_file(file_path)
            elif file_ext in pdf_extensions:
                content = load_pdf_file(file_path)

            if not content:
                logger.warning(f"⚠️  Skipping empty or unreadable file: {filename}")
                continue

            # Split content into chunks
            chunks = chunk_text(content, chunk_size, chunk_overlap)

            if not chunks:
                logger.warning(f"⚠️  No chunks generated from file: {filename}")
                continue

            # Add chunks with metadata
            relative_path = os.path.relpath(file_path, directory)
            for chunk_idx, chunk in enumerate(chunks):
                documents.append(chunk)
                metadatas.append(
                    {
                        "source": file_path,
                        "filename": filename,
                        "relative_path": relative_path,
                        "chunk_index": chunk_idx,
                        "total_chunks": len(chunks),
                    }
                )

            logger.info(
                f"✅ Loaded {len(chunks)} chunks from {filename} "
                f"({len(content.split())} words)"
            )

    if file_count == 0:
        logger.warning(
            f"No supported files found in {directory}. "
            f"Supported extensions: {', '.join(supported_extensions)}"
        )
    else:
        logger.info(
            f"📚 Total: Loaded {len(documents)} chunks from {file_count} files"
        )

    return documents, metadatas


def get_storybook_path(base_directory: str, conf_uid: str) -> str:
    """
    Get the full path to a character's storybook directory.

    Args:
        base_directory: Base storybooks directory (e.g., 'storybooks')
        conf_uid: Character configuration UID

    Returns:
        Full path to the character's storybook directory
    """
    return os.path.join(base_directory, conf_uid)

