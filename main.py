from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import pdfplumber
from sentence_transformers import SentenceTransformer
import weaviate
import os
import uuid
from fastapi.middleware.cors import CORSMiddleware
from celery_worker import process_pdf
import logging

from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
# TODO - This is not a good practice, it's just for poc purpose
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO - COfig here needs to move to .env file or docker compose file
client = weaviate.connect_to_custom(
    http_host="weaviate",
    http_port=8080,
    http_secure=False,
    grpc_host="weaviate",
    grpc_port=50051,
    grpc_secure=False
)


# Initialize Sentence Transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded")

class Question(BaseModel):
    question: str
    threshold: float = 0.5

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        # Save the uploaded file temporarily
        file_path = f"/app/uploads/{file.filename}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        print("File saved:", file_path)

        # Trigger the Celery task to process the PDF in the background
        task = process_pdf.delay(file_path)
        print("Task handed off to celery:", task.id)

        return {"message" : "PDF is being processed", "task_id": task.id}
    except Exception as e:
        logger.error(f"Error serving uploads: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_question(question: Question):
    try:
        # Generate embedding for the question
        question_embedding = model.encode(question.question)

        print("Question embedding:", question_embedding[:10])  # Print first 10 values

        result = client.collections.get("Document").query.near_vector(
            near_vector=question_embedding,  # Pass the vector directly
            return_properties=["text"],
            distance=question.threshold,  # Use the threshold parameter from the request
            # limit=10
        )

        if not result.objects:  # In v4, results are stored in 'objects' list
            print("No results found")
            return {"answer": None}

        # Retrieve the most relevant chunk
        relevant_chunk = result.objects[0].properties["text"]  # Access text via properties


        try:
            openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Answer the question based on the context: {question.question} Context: {relevant_chunk}"}
                ]
            )
            answer = response.choices[0].message.content.strip()
            print("OpenAI response:", answer)

            return {"answer": answer}
        except Exception as e:
            print("Error with OpenAI API:", str(e))
            return {"answer": relevant_chunk}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
