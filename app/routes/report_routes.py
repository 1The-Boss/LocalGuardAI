# app/routes/report_routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import List

# Database dependency
from app.db.dependencies import get_db

# Pydantic schemas
from app.schemas.report import (
    ReportCreate,
    ReportUpdate,
    ReportResponse
)

# Service-layer functions
from app.services.report_service import (
    create_report,
    get_reports,
    get_report_by_id,
    update_report,
    delete_report
)


# Creates a group of related routes
router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


# =========================================================
# CREATE REPORT
# =========================================================

@router.post("/", response_model=ReportResponse)
async def create_new_report(
    report: ReportCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new report.

    The request is validated by ReportCreate.
    Business logic is handled by report_service.py.
    """

    return await create_report(db, report)


# =========================================================
# GET ALL REPORTS
# =========================================================

@router.get("/", response_model=List[ReportResponse])
async def read_all_reports(
    db: AsyncSession = Depends(get_db)
):
    """
    Return all reports stored in PostgreSQL.
    """

    return await get_reports(db)


# =========================================================
# GET SINGLE REPORT
# =========================================================

@router.get("/{report_id}", response_model=ReportResponse)
async def read_single_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Return one report using its UUID.
    """

    report = await get_report_by_id(db, report_id)

    # If UUID doesn't exist in database
    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    return report


# =========================================================
# UPDATE REPORT
# =========================================================

@router.patch("/{report_id}", response_model=ReportResponse)
async def modify_report(
    report_id: UUID,
    updates: ReportUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update only the fields supplied by the client.
    """

    report = await get_report_by_id(db, report_id)

    # Check whether report exists
    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    # Convert Pydantic model into a dictionary.
    # exclude_unset=True means only supplied fields are updated.
    updated_report = await update_report(
        db,
        report,
        updates.model_dump(exclude_unset=True)
    )

    return updated_report


# =========================================================
# DELETE REPORT
# =========================================================

@router.delete("/{report_id}")
async def remove_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a report using its UUID.
    """

    report = await get_report_by_id(db, report_id)

    # Check whether report exists
    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    await delete_report(db, report)

    return {
        "message": "Report deleted successfully"
    }

@router.get("/items/")
async def read_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM reports"))
    return result.all()