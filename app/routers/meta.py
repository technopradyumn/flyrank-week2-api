from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["meta"])


@router.get("/")
def get_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"],
    }


@router.get("/health")
def get_health():
    return {"status": "ok"}
