from celery import Celery
from kombu import Queue
import os

def make_celery():
    celery = Celery(
        __name__,
        broker=os.getenv("CELERY_BROKER_URL"),
        backend=os.getenv("CELERY_RESULT_BACKEND"),   
    )

    celery.conf.update(
        worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
        worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
        worker_log_color=False,
        worker_redirect_stdouts_level="INFO",
        worker_redirect_stdouts=True,
        task_queues=(Queue("default", routing_key="task.#"),),
    )

    return celery

celery = make_celery()
import app.tasks