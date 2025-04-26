from kafka import KafkaProducer
import json
from datetime import datetime

def publish_to_kafka(topic, data, kafka_server='localhost:9092'):
    """
    Publishes data to a Kafka topic.

    Args:
        topic (str): The Kafka topic to send data to.
        data (dict): The data to publish in JSON format.
        kafka_server (str): The Kafka server address (default: localhost:9093).

    Returns:
        None
    """
    # Convert datetime objects to string (ISO format) in the data dictionary
    def serialize_datetimes(data):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()  # Converts datetime to string in ISO 8601 format
            elif isinstance(value, dict):
                serialize_datetimes(value)  # Recursively handle nested dictionaries
        return data

    # Serialize the datetime fields before passing to json.dumps
    data = serialize_datetimes(data)

    # Now serialize the entire data dictionary to JSON
    producer = KafkaProducer(
        bootstrap_servers=kafka_server,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    # Send the data to Kafka
    producer.send(topic, value=data)
    producer.flush()
    #Ensure publishing.
    print(f"Data published to Kafka topic '{topic}'")


