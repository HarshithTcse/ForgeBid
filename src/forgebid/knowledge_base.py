
from pathlib import Path
import hashlib

import chromadb
from sentence_transformers import SentenceTransformer


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"
CHROMA_DIR = PROJECT_ROOT / "data" / "chroma"

# Local embedding model; no Gemini API calls
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

COLLECTION_NAME = "company_knowledge"

CHUNK_SIZE = 180
CHUNK_OVERLAP = 30


def split_into_chunks(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """Split text into overlapping word-based chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size.")

    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])

        if chunk:
            chunks.append(chunk)

        if end == len(words):
            break

        start = end - overlap

    return chunks


class CompanyKnowledgeBase:
    """Load company documents, index them, and retrieve relevant evidence."""

    def __init__(self) -> None:
        if not KNOWLEDGE_BASE_DIR.exists():
            raise FileNotFoundError(
                f"Knowledge base folder not found: {KNOWLEDGE_BASE_DIR}"
            )

        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

        CHROMA_DIR.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def index_documents(self) -> int:
        """Index Markdown and text documents; return the chunk count."""
        documents = sorted(
            list(KNOWLEDGE_BASE_DIR.glob("*.md"))
            + list(KNOWLEDGE_BASE_DIR.glob("*.txt"))
        )

        if not documents:
            raise ValueError(
                f"No .md or .txt documents found in {KNOWLEDGE_BASE_DIR}"
            )

        # Rebuild this collection from the current source files so deleted
        # or changed files don't leave stale chunks behind.
        self.client.delete_collection(COLLECTION_NAME)
        self.collection = self.client.create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

        ids = []
        texts = []
        metadatas = []

        for file_path in documents:
            content = file_path.read_text(encoding="utf-8").strip()

            if not content:
                continue

            for chunk_number, chunk in enumerate(split_into_chunks(content)):
                stable_id = hashlib.sha256(
                    f"{file_path.name}:{chunk_number}:{chunk}".encode("utf-8")
                ).hexdigest()

                ids.append(stable_id)
                texts.append(chunk)
                metadatas.append(
                    {
                        "source": file_path.name,
                        "chunk_number": chunk_number,
                    }
                )

        if not texts:
            raise ValueError("The knowledge base documents are empty.")

        embeddings = self.embedding_model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings.tolist(),
        )

        return len(texts)

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """Return the most relevant evidence chunks for a query."""
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        if self.collection.count() == 0:
            raise ValueError(
                "Knowledge base is empty. Run index_documents() first."
            )

        query_embedding = self.embedding_model.encode(
            [query.strip()],
            normalize_embeddings=True,
        )

        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=min(top_k, self.collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        matches = []

        for document, metadata, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            matches.append(
                {
                    "text": document,
                    "source": metadata["source"],
                    "chunk_number": metadata["chunk_number"],
                    "distance": distance,
                }
            )

        return matches
