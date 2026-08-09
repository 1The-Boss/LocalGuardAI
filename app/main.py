from fastapi import FastAPI
from app.db.database import engine, Base, AsyncSessionLocal
from app.routes.report_routes import router
from contextlib import asynccontextmanager
from app.routes import auth_routes
from app.models.report import Report
from app.models.user import User
from sqlalchemy.future import select
from app.core.security import pwd_context
from app.officers import OFFICERS
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User  
from app.db.database import AsyncSessionLocal  



async def seed_officers():
    async with AsyncSessionLocal() as session:
        for officer in OFFICERS:
            result = await session.execute(select(User).filter(User.username == officer["username"]))
            existing = result.scalars().first()
            if not existing:
                hashed_pw = pwd_context.hash(officer["password"])
                new_user = User(
                    username=officer["username"],
                    hashed_password=hashed_pw,
                    role=officer["role"]
                )
                session.add(new_user)
                print(f"Seeded officer: {officer['username']}")
            else:
                print(f"Officer {officer['username']} already exists.")
        await session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    print("====================================")
    print("STARTING LOCALGUARDAI")
    print("====================================")


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
    await seed_officers()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health_check():
    return {"status": "ok"}



# Register all routers
app.include_router(router)
app.include_router(auth_routes.router)
