from fastapi import Depends
from carvekit.web.deps import config, db_manager
from carvekit.web.handlers.response import Authenticate
from carvekit.web.routers.router import api_router
from starlette.responses import JSONResponse
from carvekit.web.responses.api import error_dict

@api_router.get("/admin/config")
def status(auth: str = Depends(Authenticate)):
    """
    Returns the current server config.
    """
    if not auth or auth != "admin":
        return JSONResponse(
            content=error_dict("Authentication failed"), status_code=403
        )
    resp = JSONResponse(content=config.model_dump_json(), status_code=200)
    resp.headers["X-Credits-Charged"] = "0"
    return resp
