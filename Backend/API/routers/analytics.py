"""
Analytics API Router

Endpoints for business intelligence, metrics, and reporting.
Provides access to analytics service for engagement metrics and BI reports.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel

from services.analytics_service import analytics_service


router = APIRouter()


# --- Request/Response Models ---
class ReportRequest(BaseModel):
    report_type: str
    filters: Optional[Dict[str, Any]] = None
    date_range: Optional[Dict[str, str]] = None


class UserActionRequest(BaseModel):
    user_id: str
    action: str
    context: Optional[Dict[str, Any]] = None


class DataConsolidationRequest(BaseModel):
    data_sources: List[str]
    date_range: Dict[str, str]


# --- Engagement and Participation Endpoints ---
@router.get("/participation/dashboard")
async def get_participation_dashboard(
    time_range: str = Query("7d", description="Time range: 1d, 7d, 30d, 90d")
) -> Dict[str, Any]:
    """
    Get participation and engagement dashboard metrics.
    """
    try:
        return analytics_service.get_participation_dashboard(time_range=time_range)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving participation dashboard: {str(e)}"
        )


@router.get("/retention/metrics")
async def get_retention_metrics(
    cohort_period: str = Query("weekly", description="Cohort period: daily, weekly, monthly")
) -> Dict[str, Any]:
    """
    Get user retention and churn metrics.
    """
    try:
        return analytics_service.get_user_retention_metrics(cohort_period=cohort_period)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving retention metrics: {str(e)}"
        )


# --- Business Intelligence Endpoints ---
@router.post("/reports/generate")
async def generate_report(request: ReportRequest) -> Dict[str, Any]:
    """
    Generate comprehensive BI reports for different stakeholders.
    """
    try:
        return analytics_service.generate_bi_report(request.report_type, request.filters)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating report: {str(e)}"
        )





# --- Real-time Analytics ---
@router.get("/realtime/metrics")
async def get_realtime_metrics() -> Dict[str, Any]:
    """
    Get real-time KPIs and system metrics for live monitoring.
    """
    try:
        return analytics_service.get_realtime_metrics()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving real-time metrics: {str(e)}"
        )


# --- User Behavior Tracking ---
@router.post("/track/action")
async def track_user_action(request: UserActionRequest) -> Dict[str, str]:
    """
    Track user actions for analytics and behavior analysis.
    """
    try:
        success = analytics_service.track_user_action(
            user_id=request.user_id,
            action=request.action,
            context=request.context
        )
        
        if success:
            return {"status": "success", "message": "Action tracked successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to track action"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error tracking user action: {str(e)}"
        )


# --- Administrative Endpoints ---
@router.get("/admin/dashboard")
async def get_admin_dashboard() -> Dict[str, Any]:
    """
    Get administrative dashboard for system health and operations monitoring.
    """
    try:
        return analytics_service.get_admin_dashboard()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving admin dashboard: {str(e)}"
        )


@router.post("/data/consolidate")
async def consolidate_operational_data(request: DataConsolidationRequest) -> Dict[str, Any]:
    """
    Consolidate operational data from multiple sources for comprehensive reporting.
    """
    try:
        return analytics_service.consolidate_operational_data(
            data_sources=request.data_sources,
            date_range=request.date_range
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error consolidating operational data: {str(e)}"
        )


# --- Health Check ---
@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Check analytics service health."""
    return {
        "status": "healthy",
        "service": "Analytics and BI Service",
        "version": "1.0.0"
    }