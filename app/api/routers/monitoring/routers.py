"""
Monitoring routes
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK

router = APIRouter()


@router.get("/healthz", tags=["monitoring"])
def healthz():
    """
    Router to check health of application
    """
    return JSONResponse(status_code=HTTP_200_OK, content={"message": "Healthy!"})
