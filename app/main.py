from fastapi import FastAPI
from app.db.database import engine, Base, AsyncSessionLocal
from app.routes.report_routes import router
from contextlib import asynccontextmanager
from app.routes import auth_routes
from app.models.report import Report
from app.models.user import User
from sqlalchemy.future import select
from app.core.security import pwd_context

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

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).filter(User.username == "leader"))
        leader = result.scalars().first()
        if not leader:
            hashed_pw = pwd_context.hash("admin")
            new_leader = User(username="leader", hashed_password=hashed_pw, role="leader")
            session.add(new_leader)
            await session.commit()
            print("Seeded leader user: leader / admin")
        else:
            print("Leader user already exists.")

    yield

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health_check():
    return {"status": "ok"}


# Register all routers
app.include_router(router)
app.include_router(auth_routes.router)