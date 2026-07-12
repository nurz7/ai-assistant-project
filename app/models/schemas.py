from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

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


QualityStatus = Literal[
    "USE",
    "USE_WITH_CAUTION",
    "FIX_ROI_OR_USE_CAUTION",
    "EXCLUDE_LOW_SIGNAL",
]


class QualityAssessment(BaseModel):
    status: QualityStatus
    decision: str
    dates_count: int
    nonzero_dates: int
    zero_area_share: float
    high_cloud_share: float
    method_conflict_share: float
    mean_area_km2: float
    median_area_km2: float
    max_area_km2: float
    median_ratio_to_passport: float | None = None
    max_ratio_to_passport: float | None = None
    issues: list[str] = Field(default_factory=list)


class GEEObservationInput(BaseModel):
    reservoir_name: str = Field(min_length=1, max_length=120)
    observation_date: str
    source: str = Field(min_length=1, max_length=120)
    scl_water_area_km2: float = Field(ge=0)
    mndwi_area_km2: float = Field(ge=0)
    ndwi_area_km2: float = Field(ge=0)
    cloud_percent: float = Field(ge=0, le=100)
    roi_area_km2: float = Field(gt=0)
    method_version: str = Field(min_length=1, max_length=80)

    @field_validator("reservoir_name", "source", "method_version")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return " ".join(value.strip().split())

    @field_validator("observation_date")
    @classmethod
    def validate_iso_date(cls, value: str) -> str:
        from datetime import date

        normalized = value.strip()
        date.fromisoformat(normalized)
        return normalized

    @model_validator(mode="after")
    def validate_water_areas_fit_roi(self) -> "GEEObservationInput":
        areas = (
            self.scl_water_area_km2,
            self.mndwi_area_km2,
            self.ndwi_area_km2,
        )
        if any(area > self.roi_area_km2 for area in areas):
            raise ValueError("Water area must not exceed ROI area")
        return self


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
    quality_assessment: QualityAssessment | None = None
    warnings: list[str] = Field(default_factory=list)
