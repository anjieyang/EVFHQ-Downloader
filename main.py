import os
import pika
import json
import threading
import time
import functools
import logging
from video_downloader import VideoDownloader

logging.basicConfig(level=logging.INFO)


def setup_rabbitmq_connection():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=os.getenv('RABBITMQ_HOST'),
                    port=int(os.getenv('RABBITMQ_PORT')),
                    heartbeat=3600,
                    blocked_connection_timeout=600,
                    connection_attempts=5,
                    retry_delay=5
                ))
            return connection
        except pika.exceptions.AMQPConnectionError:
            logging.error(
                "Failed to connect to RabbitMQ. Retrying in 5 seconds...")
            time.sleep(5)


def request_task(channel, server_id):
    message = json.dumps({'server_id': server_id})
    channel.basic_publish(
        exchange='',
        routing_key='task_request_queue',
        body=message,
        properties=pika.BasicProperties(delivery_mode=2)
    )
    logging.info("Requested new task for server_id: %s", server_id)


def handle_download(channel, method, properties, body, args):
    logging.info(f"Received raw message: {body.decode()}")
    data = json.loads(body.decode())
    video_id = data['video_id']
    resolution = data['resolution']
    save_dir, server_id = args

    try:
        response = VideoDownloader.download_video(
            save_dir, video_id, resolution, server_id)
        logging.info(
            f"Task for video_id {video_id} processed with status: {response['status_code']}.")
        channel.basic_publish(
            exchange='',
            routing_key='video_download_response_queue',
            body=json.dumps(response),
            properties=pika.BasicProperties(delivery_mode=2)
        )
    except Exception as e:
        logging.error(
            f"Error processing download for video_id {video_id}: {str(e)}")
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    else:
        channel.basic_ack(delivery_tag=method.delivery_tag)
        request_task(channel, server_id)


def consume_tasks(channel, queue_name, callback):
    while True:
        try:
            channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                auto_ack=False
            )
            channel.start_consuming()
        except pika.exceptions.ConnectionClosedByBroker:
            logging.warning(
                "Connection closed by broker, attempting to reconnect...")
            time.sleep(5)
            channel = setup_rabbitmq_connection().channel()
        except pika.exceptions.AMQPConnectionError:
            logging.error("Connection lost, attempting to reconnect...")
            time.sleep(5)
            channel = setup_rabbitmq_connection().channel()
        except KeyboardInterrupt:
            logging.info("Consumer stopped by user.")
            break


def main():
    connection = setup_rabbitmq_connection()
    channel = connection.channel()
    channel.queue_declare(queue="task_request_queue", durable=True)
    channel.queue_declare(queue="video_download_queue", durable=True)
    channel.queue_declare(queue="video_download_response_queue", durable=True)

    server_id = os.getenv('SERVER_ID')
    save_dir = os.getenv('SAVE_DIR')

    handle_download_task = functools.partial(
        handle_download, args=(save_dir, server_id))

    request_task(channel, server_id)

    consumer_thread = threading.Thread(target=consume_tasks, args=(
        channel, "video_download_queue", handle_download_task))
    consumer_thread.start()

    logging.info(
        f"Downloader on server {server_id} is running. Waiting for download tasks...")
    try:
        consumer_thread.join()
    except KeyboardInterrupt:
        logging.info("Stopping downloader.")
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    main()
