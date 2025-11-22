import json
import asyncio
from kafka import KafkaProducer, KafkaConsumer
from backend.core.config import settings
import logging
import threading

logger = logging.getLogger(__name__)

class KafkaService:
    def __init__(self):
        self.producer = None
        self.consumer = None
        self.running = False

    def start(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            logger.info("Kafka Producer started")
            
            # Start consumer in a separate thread
            self.running = True
            threading.Thread(target=self.consume_events, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Failed to start Kafka service: {e}")

    def publish_event(self, topic: str, event: dict):
        if self.producer:
            self.producer.send(topic, event)
            self.producer.flush()

    def consume_events(self):
        try:
            self.consumer = KafkaConsumer(
                "agent.job.events",
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id='agent-group',
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            logger.info("Kafka Consumer started")
            
            for message in self.consumer:
                if not self.running:
                    break
                logger.info(f"Received event: {message.value}")
                # Here we could update DB or push to frontend via WebSocket
                
        except Exception as e:
            logger.error(f"Kafka Consumer error: {e}")

kafka_service = KafkaService()
