import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse

from app import schema
from app.config import settings
from app.core.climate import Climate
from app.core.search import db

app = FastAPI(
    title="GIZ Climate API",
    version=settings.API_VERSION,
    description="API for climate-related text classification and veracity checking",
)

climate = Climate()


def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.API_KEY.get_secret_value():
        raise HTTPException(status_code=403, detail="Invalid API Key")


@app.post(
    "/topic",
    summary="Classify topic of climate-related text",
    description="This endpoint classifies the input text into climate-related topics and returns confidence scores.",
    dependencies=[Depends(verify_api_key)],
)
def predict_topic(payload: schema.TopicInput):
    result = climate.get_topic_subtopic(payload.text)
    return schema.TopicOutput(result=result)


@app.post(
    "/check",
    response_model=schema.CheckOutput,
    summary="Check veracity of climate-related text",
    description="This endpoint checks whether the input text contains hoax information related to climate change.",
    dependencies=[Depends(verify_api_key)],
)
def check_veracity(payload: schema.CheckInput):
    result = climate.check_veracity(payload.text)
    return schema.CheckOutput(**result)


@app.put(
    "/article/{item_id}",
    response_model=schema.InsertOutput,
    dependencies=[Depends(verify_api_key)],
)
def insert_article(item_id: int, payload: schema.Article):
    result = climate.insert_article(item_id, payload)
    return schema.InsertOutput(**result)


@app.delete(
    "/article/{item_id}",
    response_model=schema.DeleteOutput,
    dependencies=[Depends(verify_api_key)],
)
def delete_article(item_id: int):
    result = climate.delete_article(item_id)
    return schema.DeleteOutput(**result)


@app.get("/collections", response_model=schema.Knowledges)
def get_collections():
    result = db.knowledges()
    return schema.Knowledges(**result)


@app.get(
    "/healthcheck",
    summary="API health check",
    description="This endpoint returns the current status of the API.",
)
def healthcheck():
    return JSONResponse(status_code=200, content={"status": "ok"})


if __name__ == "__main__":
    uvicorn.run("app.main:app", port=settings.API_PORT, host=settings.API_HOST)
