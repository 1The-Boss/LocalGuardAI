from fastapi import FastAPI
from app.db.database import engine, Base
from app.routes.report_routes import router
from contextlib import asynccontextmanager
from app.routes import auth_routes
from app.models.report import Report

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    print("====================================")
    print("STARTING LOCALGUARDAI")
    print("====================================")

    print("Registered SQLAlchemy tables:")
    print(Base.metadata.tables.keys())

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Database tables created/verified.")

    yield

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health_check():
    return {"status": "ok"}


# Register all routers
app.include_router(router)
app.include_router(auth_routes.router)