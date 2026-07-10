from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DocumentChunk:
    document: str
    title: str
    section: str
    chunk_id: str
    content: str


@dataclass(frozen=True, slots=True)
class SearchResult:
    chunk: DocumentChunk
    score: float
