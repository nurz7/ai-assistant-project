import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _resolve_project_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


@dataclass(frozen=True)
class Settings:
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-5.4-mini")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "")
    methodology_docs_path: Path = _resolve_project_path(
        os.getenv(
            "METHODOLOGY_DOCS_PATH",
            os.getenv("SOP_DOCS_PATH", "data/docs"),
        )
    )

    @property
    def sop_docs_path(self) -> Path:
        """Backward-compatible alias for older retrieval code and tests."""
        return self.methodology_docs_path


settings = Settings()
