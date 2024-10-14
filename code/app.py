import os
from fastapi import FastAPI
from pydantic import BaseModel
from load_docs import IndexUpdater
from typing import List
from rag import ChatBot


# Crear una instancia de FastAPI
app = FastAPI()


# Modelo para sumar dos números
class QuestionModel(BaseModel):
    question: str


class PageModel(BaseModel):
    page_ids: List[int]
    is_complete_overwrite: bool


PROJECT_ID = os.getenv("PROJECT_ID")
INDEX_ID = os.getenv("INDEX_ID")
INDEX_ENDPOINT_ID = os.getenv("INDEX_ENDPOINT_ID")


index_updater = IndexUpdater(
    project_id=PROJECT_ID,
    index_id=INDEX_ID,
    index_endpoint_id=INDEX_ENDPOINT_ID
)

chat_bot = ChatBot(
    project_id=PROJECT_ID,
    index_id=INDEX_ID,
    index_endpoint_id=INDEX_ENDPOINT_ID
)


@app.post("/update_index")
def update_index(data: PageModel):
    try:
        index_updater.update_index(data.page_ids, data.is_complete_overwrite)
    except Exception as e:
        return {"result": f"Error updating index: {e}"}
    else:
        return {"result": "Index update operation finished"}


@app.post("/chatbot")
def chatbot(data: QuestionModel):
    try:
        response = chat_bot.resolve_question(data.question)
    except Exception as e:
        return {"result": f"Error answering question: {e}"}
    else:
        return {"result": response}
