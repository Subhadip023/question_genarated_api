from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(
    title="Question Generator API",
    description="A small demo FastAPI application.",
    version="0.1.0",
)


class QuestionRequest(BaseModel):
    topic: str
    count: int = 3


@app.get("/")
def read_root():
    return {"message": "Welcome to the Question Generator API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/questions")
def generate_questions(request: QuestionRequest):
    questions = [
        f"Question {number}: What do you know about {request.topic}?"
        for number in range(1, request.count + 1)
    ]
    return {"topic": request.topic, "questions": questions}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
