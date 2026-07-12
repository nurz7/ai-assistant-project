from typing import Literal

from pydantic import BaseModel, Field, field_validator

MAX_MESSAGE_LENGTH = 4_000


class SourceReference(BaseModel):
    document: str
    section: str
    chunk_id: str


ChatIntent = Literal[
    "methodology_qa",
    "reservoir_lookup",
    "observation_analysis",
    "report_generation",
    "unsupported",
]


class ReservoirReference(BaseModel):
    name: str
    region: str
    passport_area_km2: float | None = None
    normal_level_m: float | None = None
    dead_level_m: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    notes: str | None = None


class CalculationResult(BaseModel):
    metric: str
    value: float
    unit: str
    explanation: str


class ReservoirObservation(BaseModel):
    observation_id: int
    observation_date: str
    source: str
    scl_water_area_km2: float
    mndwi_area_km2: float
    ndwi_area_km2: float
    cloud_percent: float
    roi_area_km2: float
    method_version: str


class AnomalyFlag(BaseModel):
    observation_id: int | None = None
    observation_date: str | None = None
    alert_type: str
    severity: str
    message: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=MAX_MESSAGE_LENGTH)

    @field_validator("message")
    @classmethod
    def normalize_message(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Message must not be empty")
        return normalized


class ChatResponse(BaseModel):
    user_message: str
    answer: str
    mode: Literal["mock", "llm"]
    intent: ChatIntent
    sources: list[SourceReference] = Field(default_factory=list)
    reservoir: ReservoirReference | None = None
    calculation_result: CalculationResult | None = None
    observations: list[ReservoirObservation] = Field(default_factory=list)
    anomaly_flags: list[AnomalyFlag] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
