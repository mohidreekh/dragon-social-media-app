"""
Health-check route — useful for load balancers and monitoring.
"""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Health check")
async def health_check():
    return {"status": "healthy", "message": "🐉 Dragon Project is running!"}
