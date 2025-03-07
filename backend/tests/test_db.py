
from app.core.db.main import AsyncSessionLocal, engine
from app.users.model import User, Role



from app.core.models import Base


async def prepare_test_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    
    


