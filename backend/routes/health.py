from fastapi import APIRouter

router = APIRouter()

@router.get("/healthz")
async def health_check():
    return {"status": "healthy", "service": "lesson-lab-2.0-api"}