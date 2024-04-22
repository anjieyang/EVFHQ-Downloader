import os
import pika
import json
import time
import functools
from video_downloader import VideoDownloader


def setup_rabbitmq_connection():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=os.getenv('RABBITMQ_HOST'),
            port=os.getenv('RABBITMQ_PORT'),
            heartbeat=600,
            blocked_connection_timeout=300,
            connection_attempts=5,
            retry_delay=5
        ))
    channel = connection.channel()
    return connection, channel


def request_task(channel, server_id):
    message = json.dumps({'server_id': server_id})
    channel.basic_publish(
        exchange='',
        routing_key='task_request_queue',
        body=message,
        properties=pika.BasicProperties(delivery_mode=2)
    )


def handle_download(channel, method, properties, body, args):
    print(f"Received raw message: {body.decode()}")
    data = json.loads(body.decode())
    video_id = data['video_id']
    resolution = data['resolution']
    save_dir, server_id = args

    try:
        response = VideoDownloader.download_video(
            save_dir, video_id, resolution, server_id)
        print(
            f"Task for video_id {video_id} processed with status: {response['status_code']}.")
        channel.basic_publish(
            exchange='',
            routing_key='video_download_response_queue',
            body=json.dumps(response),
            properties=pika.BasicProperties(delivery_mode=2)
        )
    except Exception as e:
        print(f"Error processing download for video_id {video_id}: {str(e)}")
    finally:
        channel.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection, channel = setup_rabbitmq_connection()
    channel.queue_declare(queue="task_request_queue", durable=True)
    channel.queue_declare(queue="video_download_queue", durable=True)
    channel.queue_declare(queue="video_download_response_queue", durable=True)

    server_id = os.getenv('SERVER_ID')
    save_dir = os.getenv('SAVE_DIR')

    request_task(channel, server_id)

    handle_download_task = functools.partial(
        handle_download, args=(save_dir, server_id))

    channel.basic_consume(
        queue="video_download_queue",
        on_message_callback=handle_download_task,
        auto_ack=False
    )

    print(
        f"Downloader on server {server_id} is running. Waiting for download tasks...")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Stopping downloader.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
