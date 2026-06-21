from celery import Celery
import time

# Configure Celery with Redis broker
# Ensure redis-server is running on localhost:6379, or via docker network
celery_app = Celery(
    'asta_tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Kolkata',
    enable_utc=True,
)

@celery_app.task(name="train_tgcn_model")
def train_tgcn_model(epochs: int = 100):
    """
    Simulated long-running task to train the Temporal Graph Convolutional Network.
    """
    print(f"Starting TGCN training for {epochs} epochs...")
    for i in range(epochs):
        time.sleep(0.1) # Simulate training step
    print("Training complete.")
    return {"status": "success", "accuracy": 0.85}

@celery_app.task(name="process_anpr_feed")
def process_anpr_feed(batch_size: int = 1000):
    """
    Async task to process heavy ANPR video feeds in the background.
    """
    time.sleep(2.0)
    return {"processed": batch_size, "violations_flagged": int(batch_size * 0.15)}
