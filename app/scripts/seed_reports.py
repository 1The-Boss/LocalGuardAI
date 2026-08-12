import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import asyncio, json
from app.db.database import AsyncSessionLocal
from app.schemas.report import ReportCreate
from app.services.report_service import create_report


async def seed():
    file_path = Path(__file__).parent.parent / "data" / "sample_complaints.json"
    with open(file_path, encoding="utf-8") as f:
        complaints = json.load(f)
    async with AsyncSessionLocal() as db:
        for c in complaints:
            report_data = ReportCreate(description=c["text"], lat=c["lat"], lng=c["lng"])
            await create_report(db, report_data)
            print(f"Seeded #{c['id']}")

if __name__ == "__main__":
    asyncio.run(seed())