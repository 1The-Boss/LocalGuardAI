from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.report import Report
from app.schemas.report import ReportCreate, ReportUpdate


async def create_report(db: AsyncSession, report_data: ReportCreate):
    # Create a new Report object.
    # priority_score is temporarily 0.0.
    # Later, our AI model will calculate the actual score.

    new_report = Report(
        description=report_data.description,
        lat=report_data.lat,
        lng=report_data.lng,
        category=report_data.category,
        priority_score=0.0,
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

    # Update only the fields supplied by the client.
    for key, value in update_data.items():
        setattr(report, key, value)

    # Prevent reopening closed reports.
    if report.status == "closed" and update_data.get("status") == "open":
        raise ValueError("Closed reports cannot be reopened")

    await db.commit()
    await db.refresh(report)

    return report


async def delete_report(db: AsyncSession, report: Report):
    await db.delete(report)
    await db.commit()