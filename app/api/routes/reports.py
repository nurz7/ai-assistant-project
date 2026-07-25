from fastapi import APIRouter, HTTPException, status

from app.models.schemas import MonitoringReportRequest, MonitoringReportResponse
from app.services.report_service import build_monitoring_report

router = APIRouter(tags=["reports"])


@router.post(
    "/reports",
    response_model=MonitoringReportResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "No synthetic report data was found for the request"
        }
    },
)
async def generate_monitoring_report(
    request: MonitoringReportRequest,
) -> MonitoringReportResponse:
    """Build a read-only grounded monitoring report from synthetic demo data."""

    report = build_monitoring_report(
        request.reservoir_name,
        start_date=request.start_date,
        end_date=request.end_date,
    )
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No synthetic reservoir report data was found for this request.",
        )

    return MonitoringReportResponse(
        text=report.text,
        reservoir=report.reservoir,
        observations=report.observations,
        calculation_result=report.calculation_result,
        anomaly_flags=report.anomaly_flags,
        quality_assessment=report.quality_assessment,
        sources=report.sources,
        warnings=report.warnings,
    )
