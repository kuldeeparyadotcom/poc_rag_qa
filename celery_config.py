from celery import Celery
import os

# Initialize Celery
broker_url = os.getenv('CELERY_BROKER_URL')
celery_app = Celery('pdf_processing', broker=broker_url)

# Optional: Configure Celery (e.g., result backend, timezone, etc.)
celery_app.conf.update(
    result_backend=broker_url,
    timezone='UTC',
)
