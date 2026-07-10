import re
from pathlib import Path

from app.core.config import settings
from app.models.documents import DocumentChunk, SearchResult
from app.services.document_loader import load_document_chunks

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "be",
    "can",
    "do",
    "does",
    "for",
    "from",
    "get",
    "help",
    "how",
    "i",
    "in",
    "information",
    "is",
    "it",
    "me",
    "my",
    "need",
    "of",
    "on",
    "or",
    "our",
    "please",
    "should",
    "tell",
    "the",
    "to",
    "use",
    "want",
    "what",
    "when",
    "where",
    "who",
    "with",
    "you",
    "your",
}
TOKEN_ALIASES = {
    "areas": "area",
    "calculation": "calculate",
    "calculating": "calculate",
    "classes": "class",
    "clouds": "cloud",
    "compared": "compare",
    "comparing": "compare",
    "derived": "derive",
    "detecting": "detect",
    "detection": "detect",
    "estimates": "estimate",
    "estimating": "estimate",
    "extracted": "extract",
    "extraction": "extract",
    "filtered": "filter",
    "filtering": "filter",
    "levels": "level",
    "masks": "mask",
    "mndwi": "mndwi",
    "ndwi": "ndwi",
    "observations": "observation",
    "reservoirs": "reservoir",
    "sentinel": "sentinel2",
    "sentinel-2": "sentinel2",
    "suspicious": "anomaly",
    "warnings": "warning",
}
BLOCKED_REQUEST_PATTERN = re.compile(
    r"\b(api key|confidential|private|secret|delete|drop|truncate|update|insert|"
    r"write|remove all)\b",
    re.IGNORECASE,
)
STRUCTURED_LOOKUP_PATTERN = re.compile(
    r"\b(show|list|get|generate)\b.*\b(observations?|report|tasmola)\b",
    re.IGNORECASE,
)
EXACT_LEVEL_LOOKUP_PATTERN = re.compile(
    r"\b(exact|actual)\b.*\bwater level\b|\bunknown reservoir\b|"
    r"\b\d{4}-\d{2}-\d{2}\b",
    re.IGNORECASE,
)
METHODOLOGY_PATTERN = re.compile(
    r"\b(what|why|how|which|method|methodology|mean|used for|limitation|define|"
    r"explain)\b",
    re.IGNORECASE,
)


def _normalize_token(token: str) -> str:
    if token.endswith("ies") and len(token) > 4:
        return f"{token[:-3]}y"
    if token.endswith("s") and not token.endswith("ss") and len(token) > 3:
        return token[:-1]
    return token


def _tokenize(value: str) -> set[str]:
    tokens: set[str] = set()
    for raw_token in TOKEN_PATTERN.findall(value.lower()):
        token = _normalize_token(raw_token)
        if token in STOP_WORDS or len(token) <= 1:
            continue
        tokens.add(TOKEN_ALIASES.get(token, token))
    return tokens


def _looks_like_structured_data_request(query: str) -> bool:
    """Keep methodology retrieval from answering observation/report lookups."""

    normalized_query = query.strip().lower()
    if BLOCKED_REQUEST_PATTERN.search(normalized_query):
        return True
    if EXACT_LEVEL_LOOKUP_PATTERN.search(normalized_query):
        return True
    if STRUCTURED_LOOKUP_PATTERN.search(normalized_query):
        return True
    if METHODOLOGY_PATTERN.search(normalized_query):
        return False
    return False


def _score_chunk(query_tokens: set[str], chunk: DocumentChunk) -> float:
    if not query_tokens:
        return 0.0

    content_tokens = _tokenize(chunk.content)
    metadata_tokens = _tokenize(f"{chunk.title} {chunk.section}")
    matched_tokens = query_tokens & (content_tokens | metadata_tokens)
    if len(matched_tokens) < 2:
        return 0.0

    content_coverage = len(query_tokens & content_tokens) / len(query_tokens)
    metadata_coverage = len(query_tokens & metadata_tokens) / len(query_tokens)
    return (content_coverage * 0.8) + (metadata_coverage * 0.2)


def retrieve_relevant_chunks(
    query: str,
    *,
    docs_path: Path | None = None,
    top_k: int = 3,
    min_score: float = 0.35,
) -> list[SearchResult]:
    """Return the best local lexical matches for a methodology question."""

    if top_k <= 0:
        raise ValueError("top_k must be positive")
    if not 0 <= min_score <= 1:
        raise ValueError("min_score must be between 0 and 1")
    if _looks_like_structured_data_request(query):
        return []

    query_tokens = _tokenize(query)
    chunks = load_document_chunks(docs_path or settings.methodology_docs_path)
    results = [
        SearchResult(chunk=chunk, score=round(_score_chunk(query_tokens, chunk), 4))
        for chunk in chunks
    ]
    results.sort(key=lambda result: (-result.score, result.chunk.chunk_id))
    if not results or results[0].score < min_score:
        return []

    relative_cutoff = max(min_score, results[0].score * 0.8)
    return [result for result in results if result.score >= relative_cutoff][:top_k]
