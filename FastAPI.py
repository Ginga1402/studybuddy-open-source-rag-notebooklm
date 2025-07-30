from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import asyncio
from concurrent.futures import ThreadPoolExecutor
import os
from configuration import DIRECTORY_PATH,VECTORSORE_PATH
from ingestion import create_vectorstore_from_pdfs
from create_diagram import diagram_creation
from create_summary import summary_creation
import uvicorn  # make sure uvicorn is installed
from fastapi.middleware.cors import CORSMiddleware
from QA_Rag import generate_answer
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime
import pytz  # Optional: for timezone-aware timestamp
from collections import defaultdict
import time
from create_topics import topics_from_vectorstore
from create_quiz import quiz_creation
from typing import Optional
from create_faq import FAQ_creation

# Service start time
service_start_time = time.time()

# API request counter
request_counter = defaultdict(int)


app = FastAPI(
    title="📚 StudyBuddy – Open Source RAG-Based AI Notebook and Google NotebookLM Alternative",
    description="StudyBuddy is a free, open source alternative to Google NotebookLM that lets you chat with your documents, generate smart summaries, and organize knowledge with AI—all securely on your terms.",
    version="1.0.0"
)

# Allow CORS (optional but helpful for frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# ThreadPool for concurrency
executor = ThreadPoolExecutor()

@app.middleware("http")
async def count_requests_middleware(request: Request, call_next):
    route = request.url.path
    request_counter[route] += 1
    response = await call_next(request)
    return response



@app.get("/")
def root():
    return {"message": "👋 StudyBuddy – Open Source RAG-Based AI Notebook and Google NotebookLM Alternative FastAPI"}


@app.get("/heartbeat")
async def heartbeat():
    """
    Health check endpoint to verify the API is alive.
    """
    current_time = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S %Z")
    return {
        "status": "✅ API is alive",
        "timestamp": current_time
    }


@app.get("/metrics")
async def metrics():
    """
    Returns uptime and API usage count per route.
    """
    current_time = time.time()
    uptime_seconds = int(current_time - service_start_time)

    uptime_str = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))

    return {
        "status": "✅ Metrics OK",
        "uptime": uptime_str,
        "uptime_seconds": uptime_seconds,
        "request_counts": dict(request_counter)
    }



class VectorStoreRequest(BaseModel):
    filenames: List[str]
    vectorstore_name: str

@app.post("/create-vectorstore/")
async def create_vectorstore(req: VectorStoreRequest):
    """
    Async endpoint to trigger vector store creation from PDF filenames.
    """
    missing_files = [f for f in req.filenames if not os.path.isfile(os.path.join(DIRECTORY_PATH, f))]
    if missing_files:
        raise HTTPException(status_code=400, detail=f"❌ Missing files: {missing_files}")

    try:
        await asyncio.get_event_loop().run_in_executor(
            executor,
            create_vectorstore_from_pdfs,
            req.filenames,
            req.vectorstore_name
        )
        return {
            "status": "✅ Success",
            "vectorstore_path": f"Vectorstore/{req.vectorstore_name}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Failed to create vector store: {str(e)}")



class DiagramRequest(BaseModel):
    subject: str
    vectorstore_name: str


@app.post("/generate-diagram/")
async def generate_diagram(req: DiagramRequest):
    """
    Async endpoint to generate ASCII diagram from a subject and vector store.
    """
    vectorstore_path = os.path.join(VECTORSORE_PATH, req.vectorstore_name)

    if not os.path.exists(vectorstore_path):
        raise HTTPException(status_code=404, detail=f"❌ Vectorstore '{req.vectorstore_name}' not found.")

    try:
        diagram = await asyncio.get_event_loop().run_in_executor(
            executor,
            diagram_creation,
            req.subject,
            vectorstore_path
        )

        return {
            "status": "✅ Success",
            "subject": req.subject,
            "diagram": diagram
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Failed to generate diagram: {str(e)}")


class SummaryRequest(BaseModel):
    subject: str
    vectorstore_name: str

@app.post("/generate-summary/")
async def generate_summary(req: SummaryRequest):
    """
    Async endpoint to generate a student-friendly summary from a subject and vector store.
    """
    vectorstore_path = os.path.join(VECTORSORE_PATH, req.vectorstore_name)

    if not os.path.exists(vectorstore_path):
        raise HTTPException(status_code=404, detail=f"❌ Vectorstore '{req.vectorstore_name}' not found.")

    try:
        summary = await asyncio.get_event_loop().run_in_executor(
            executor,
            summary_creation,
            req.subject,
            vectorstore_path
        )

        return {
            "status": "✅ Success",
            "subject": req.subject,
            "summary": summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Failed to generate summary: {str(e)}")


class QARequest(BaseModel):
    question: str
    vectorstore_name: str

@app.post("/QA-Guide/")
async def qa_guide(req: QARequest):
    """
    Async endpoint to perform question-answering over a selected vector store using RAG.
    Returns the generated answer and source document.
    """
    vectorstore_path = os.path.join(VECTORSORE_PATH, req.vectorstore_name)

    # Validate vector store existence
    if not os.path.exists(vectorstore_path):
        raise HTTPException(status_code=404, detail=f"❌ Vectorstore '{req.vectorstore_name}' not found.")

    try:
        print(f"📨 [QA] Received question: {req.question}")
        print(f"📁 [QA] Using vectorstore: {vectorstore_path}")

        # Run RAG logic in a separate thread for non-blocking performance
        answer, source = await asyncio.get_event_loop().run_in_executor(
            executor,
            generate_answer,
            req.question,
            req.vectorstore_name
        )

        return {
            "status": "✅ Success",
            "question": req.question,
            "answer": answer,
            "source": source
        }

    except Exception as e:
        print(f"❌ [QA] Error: {e}")
        raise HTTPException(status_code=500, detail=f"❌ Failed to generate answer: {str(e)}")
    


class TopicGenerationRequest(BaseModel):
    vectorstore_name: str

@app.post("/generate-important-topics/")
async def generate_important_topics(req: TopicGenerationRequest):
    """
    Async endpoint to generate high-level topic clusters from a vectorstore using LDA + LLM.
    """
    vectorstore_path = os.path.join(VECTORSORE_PATH, req.vectorstore_name)

    if not os.path.exists(vectorstore_path):
        raise HTTPException(status_code=404, detail=f"❌ Vectorstore '{req.vectorstore_name}' not found.")

    try:
        # Run topic generation in background executor
        result = await asyncio.get_event_loop().run_in_executor(
            executor,
            topics_from_vectorstore,
            vectorstore_path
        )

        return {
            "status": "✅ Success",
            "vectorstore": req.vectorstore_name,
            "topics_description": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Failed to generate topics: {str(e)}")


class QuizRequest(BaseModel):
    subject: str
    vectorstore_name: str
    num_questions: int

@app.post("/generate-quiz/")
async def generate_quiz(req: QuizRequest):
    """
    Async endpoint to generate a multiple-choice quiz based on a subject and vector store.

    - Checks if the vectorstore exists
    - Fetches relevant content via FAISS retriever
    - Generates quiz using the LLM pipeline
    """
    vectorstore_path = os.path.join(VECTORSORE_PATH, req.vectorstore_name)

    if not os.path.exists(vectorstore_path):
        raise HTTPException(
            status_code=404,
            detail=f"❌ Vectorstore '{req.vectorstore_name}' not found."
        )

    try:
        print(f"📩 Request received to generate quiz on: '{req.subject}'")
        quiz = await asyncio.get_event_loop().run_in_executor(
            executor,
            quiz_creation,
            req.subject,
            req.vectorstore_name,
            req.num_questions
        )

        return {
            "status": "✅ Success",
            "subject": req.subject,
            "num_questions": req.num_questions,
            "quiz": quiz
        }

    except Exception as e:
        print(f"❌ Exception in /generate-quiz: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"❌ Failed to generate quiz: {str(e)}"
        )


class FAQRequest(BaseModel):
    subject: str
    vector_store_name: str
    num_questions: Optional[int] = 5

@app.post("/generate-FAQ")
async def generate_faq(request: FAQRequest):
    """
    Endpoint to generate FAQs using a vector store and LLM.
    """

    try:
        # Call the refactored FAQ generator function
        result = FAQ_creation(
            subject=request.subject,
            vector_store_name=request.vector_store_name,
            num_questions=request.num_questions
        )

        # Return error message if something failed inside FAQ_creation
        if result.startswith("Error"):
            raise HTTPException(status_code=500, detail=result)

        print("✅ Successfully generated FAQs.")
        return {"status": "success", "faq": result}

    except Exception as e:
        print(f"❌ Exception in generate-FAQ endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"FAQ generation failed: {str(e)}")



@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 405:
        return JSONResponse(
            status_code=405,
            content={
                "status": "❌ Method Not Allowed",
                "message": f"Method {request.method} not allowed on this route: {request.url.path}"
            },
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "❌ Error",
            "message": exc.detail,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "status": "❌ Validation Error",
            "message": exc.errors(),
        },
    )



@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    print(f"🔥 Unhandled Error on {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "❌ Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
        },
    )






# 👇 This is the block that lets you run via `python api.py`
if __name__ == "__main__":
    uvicorn.run("FastAPI:app", host="0.0.0.0", port=9000, reload=True)





