from celery import Celery
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Message, Base
import os
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

celery = Celery(__name__)

@celery.task(queue='default')
def process_message(content):
    logger.info("Entering process_message task")
    db = SessionLocal()
    try:
        logger.info(f"Processing message: {content}")
        message = Message(content=content)
        db.add(message)
        db.commit()
        logger.info("Message added to database")
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing message: {e}")
    finally:
        db.close()
    logger.info("Exiting process_message task")
