import asyncio
from uuid import uuid4

from sip.core.contracts.experts import Expert, ExpertStatus, ExpertConfig
from sip.core.config import get_settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sip.infrastructure.database.repositories import PostgresExpertRepository

async def main() -> None:
    engine = create_async_engine(get_settings().postgres.dsn)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        repo = PostgresExpertRepository(session)
        
        # We need an id for SIP architect that matches the ingested one.
        # But we'll just seed standard ones and they can reingest if needed.
        # First, check if they exist to avoid duplicates
        existing_sip = await repo.get_by_slug("sip-architect")
        
        if not existing_sip:
            print("Seeding experts...")
            python_expert = Expert(
                name="Python Expert",
                slug="python",
                description="Specialist in Python ecosystem, standard library, and modern packaging.",
                status=ExpertStatus.READY,
                config=ExpertConfig()
            )
            docker_expert = Expert(
                name="Docker Expert",
                slug="docker",
                description="Specialist in containerization, Dockerfiles, and compose.",
                status=ExpertStatus.CONFIGURING,
                config=ExpertConfig()
            )
            sip_expert = Expert(
                name="SIP Architect",
                slug="sip-architect",
                description="Expert on the Software Intelligence Platform (SIP) internal architecture.",
                status=ExpertStatus.ACTIVE,
                config=ExpertConfig()
            )
            
            await repo.save(python_expert)
            await repo.save(docker_expert)
            await repo.save(sip_expert)
            await session.commit()
            print("Experts seeded successfully.")
        else:
            print("Experts already seeded.")

if __name__ == "__main__":
    asyncio.run(main())
