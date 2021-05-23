"""
To deploy API on server, run the following in the terminal:

> uvicorn src.api.fastapi_main:app --workers 6 --port 6128 --timeout-keep-alive 3600 --host 0.0.0.0
"""

import orjson
import typing
from conf import loguru_logger
from fastapi import FastAPI, Request, Body
from fastapi.responses import JSONResponse

from src.optimisation_model.main import main
from src.api.fastapi_pydantic_models import *  # pydantic Models for Swagger API Docs


# ========== API Definition ==========
class ORJSONResponse(JSONResponse):
    """Custom JSONResponse class for returning NaN float values in JSON."""
    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        return orjson.dumps(content)


app = FastAPI(default_response_class=ORJSONResponse)
app.logger = loguru_logger


@app.get('/')
async def home(request: Request):
    user_ip = request.client.host
    request.app.logger.info(f"[{user_ip}] Default home '/' is called.")
    return "Welcome to My LAW Project! Please refer to /docs/ path for Swagger API documentation."


# ============================== MLNG TIGA ==============================
@app.post('/run_optimisation/', tags=['optimisation'])
async def run_optimisation(
    request: Request,
    inputs: OptimisationModelInput
):

    user_ip = request.client.host
    request.app.logger.info(f"[{user_ip}] /run_optimisation/ is called.")
    json_data = inputs.dict()  # Loading input data

    # Run optimisation
    optimisation_results = main(**json_data)

    request.app.logger.info(f"[{user_ip}] /run_optimisation/ completed.")

    return JSONResponse(content=optimisation_results)


if __name__ == '__main__':

    import uvicorn
    uvicorn.run("src.api.fastapi_main:app", host='0.0.0.0', port=6128, debug=False, reload=False)
