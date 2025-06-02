from fastapi import APIRouter, status, HTTPException
import sqlalchemy
from src import database as db
import asyncio
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(
    prefix="/health",
    tags=["health"],
)

@router.get("", status_code=status.HTTP_200_OK)
async def health_check():
    """
    /health: check endpoint to verify API and database are up
    if both are up it will return 200, if database is down it will return 503
    if database connection times out it will also return 503
    """
    try:
        async def check_db():
            try:
                with db.engine.connect() as connection:
                    # Check if required tables exist
                    required_tables = ['watchlists', 'movies', 'movie_ratings', 'users']
                    for table in required_tables:
                        result = connection.execute(
                            sqlalchemy.text(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
                        )
                        if not result.scalar():
                            print(f"Required table '{table}' does not exist")
                            return False
                    return True
            except SQLAlchemyError as e:
                print(f"Database connection failed: {str(e)}")
                return False

        # 2 sec timeout
        is_healthy = await asyncio.wait_for(asyncio.to_thread(check_db), timeout=2.0)
        
        if is_healthy:
            return {"status": "healthy", "database": "connected"}
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection failed or required tables missing"
            )
    except asyncio.TimeoutError:
        print("Database connection timed out")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection timed out"
        )
    except Exception as e:
        print(f"Unexpected error during health check: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        ) 