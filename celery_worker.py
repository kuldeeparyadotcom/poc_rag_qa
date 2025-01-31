from celery_config import celery_app
import pdfplumber
from sentence_transformers import SentenceTransformer
import weaviate
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery
# broker_url = os.getenv('CELERY_BROKER_URL')
# app = Celery('pdf_processing', broker=broker_url)

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

@celery_app.task
def process_pdf(file_path):
    try:
        logger.info(f"Processing PDF within Celery worker: {file_path}")
        # Extract text from PDF
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text()

        # Split text into chunks
        chunks = [text[i:i + 500] for i in range(0, len(text), 500)]

        # Generate embeddings and store in Weaviate
        for chunk in chunks:
            embedding = model.encode(chunk)
            client.collections.get("Document").data.insert(
                properties={"text": chunk},
                vector=embedding
            )

        # Clean up the uploaded file
        os.remove(file_path)

        logger.info(f"PDF processed successfully: {file_path}")
        return {"status": "success", "message": "PDF processed successfully"}
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        return {"status": "error", "message": str(e)}
