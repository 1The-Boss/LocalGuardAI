from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.report import Report
from app.schemas.report import ReportCreate, ReportUpdate
from app.ai.priority_engine import predict_priority


async def create_report(db: AsyncSession, report_data: ReportCreate):
    # Calculate priority score using AI model
    try:
        calculated_priority = predict_priority(report_data.description)
    except Exception:
        calculated_priority = 0.0

    new_report = Report(
        description=report_data.description,
        lat=report_data.lat,
        lng=report_data.lng,
        category=report_data.category,
        priority_score=calculated_priority,
        status="open"
    )

    print("DEBUG: Creating report")
    print("DEBUG priority_score:", new_report.priority_score)

    db.add(new_report)
    await db.commit()
    await db.refresh(new_report)

    return new_report


async def get_reports(db: AsyncSession):
    result = await db.execute(select(Report))
    return result.scalars().all()


async def get_report_by_id(db: AsyncSession, report_id):
    result = await db.execute(select(Report).filter(Report.id == report_id))
    return result.scalars().first()


async def update_report(db: AsyncSession, report: Report, update_data: dict):

    # Prevent reopening closed reports.
    if report.status == "closed" and update_data.get("status") == "open":
        raise ValueError("Closed reports cannot be reopened")

    # Update only the fields supplied by the client.
    for key, value in update_data.items():
        setattr(report, key, value)

    await db.commit()
    await db.refresh(report)

    return report


async def delete_report(db: AsyncSession, report: Report):
    await db.delete(report)
    await db.commit()