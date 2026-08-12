from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.report import Report
from ..schemas.report import ReportCreate, ReportUpdate
from ..ai.priority_engine import predict_priority
from ..ai.hybrid_classifier import classify
from ..ai.category_classifier import generate_citizen_response
from geoalchemy2.elements import WKTElement

URGENCY_BOOST = {"low": 0, "medium": 2, "high": 5}

async def get_existing_categories(db: AsyncSession) -> list[str]:
    result = await db.execute(select(Report.category).distinct())
    return [row[0] for row in result.all() if row[0]]

async def create_report(db: AsyncSession, report_data: ReportCreate):
    if report_data.category:
        classification = {"category": report_data.category, "urgency": "medium", "source": "manual"}
    else:
        existing_categories = await get_existing_categories(db)
        classification = await classify(report_data.description, existing_categories)

    print("DEBUG classification:", classification)

    try:
        base_priority = predict_priority(report_data.description)
    except Exception:
        base_priority = 0.0

    urgency_boost = URGENCY_BOOST.get(classification.get("urgency", "medium"), 2)

    new_report = Report(
        description=report_data.description,
        lat=report_data.lat,
        lng=report_data.lng,
        geo=WKTElement(f"POINT({report_data.lng} {report_data.lat})", srid=4326),
        category=report_data.category or classification.get("category"),
        priority_score=base_priority + urgency_boost,
        status="open"
    )

    print("DEBUG: Creating report")
    print("DEBUG priority_score:", new_report.priority_score)

    db.add(new_report)
    await db.commit()
    await db.refresh(new_report)

    # citizen-facing ack, generated after commit so we have new_report.id/status confirmed
    new_report.ack_message = generate_citizen_response(
        report_data.description, new_report.category, new_report.status
    )
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