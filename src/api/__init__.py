from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "PMCursor API"}


# All routes are imported from routes.py
