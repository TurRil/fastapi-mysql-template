from fastapi import APIRouter

router = APIRouter()


@router.get("/status", name="status")
async def status() -> dict[str, str]:
    return {"status": "ok"}