import os
import uuid
import warnings

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from pydantic import BaseModel
from src.graph import Question, graph

warnings.filterwarnings("ignore")
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

app = FastAPI(title="RAG Document API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Question(BaseModel):
    question: str
    type: str


class Answer(BaseModel):
    question: str
    answer: str


class ChatRequest(BaseModel):
    message: str
    answers: list[Answer] | None = []
    thread_id: str | None = None  # For future conversation tracking


class ChatResponse(BaseModel):
    messages: list
    questions: list[Question]
    thread_id: str


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy :)"}


def extractInterruption(state: dict):
    """Extract interruption value from LangGraph state."""
    return state["__interrupt__"][0].value


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    thread_id = request.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    humanMessage = HumanMessage(content=request.message)
    result = {}
    if len(request.answers) > 0:
        input_data = {"answers": request.answers}
        print("Resuming graph")
        result = await graph.ainvoke(Command(resume=input_data), config)
    else:
        print("Starting graph")
        result = await graph.ainvoke({"messages": [humanMessage]}, config)

    return {
        "messages": result["messages"],
        "questions": result["questions"],
        "thread_id": thread_id,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8004)
