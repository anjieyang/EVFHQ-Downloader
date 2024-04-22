import os
import subprocess
import logging
import time
import random


class VideoDownloader:
    @staticmethod
    def download_video(save_dir, video_id, resolution, server_id, retry_count=3):
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
            "Mozilla/5.0 (iPad; CPU OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
        ]
        user_agent = random.choice(user_agents)

        save_path = os.path.join(save_dir, f"vid_{video_id}.mp4")
        format_code = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"

        command = [
            "yt-dlp",
            f"https://www.youtube.com/watch?v={video_id}",
            "--output", save_path,
            "-f", format_code,
            "--external-downloader", "aria2c",
            "--external-downloader-args", "-x 8 -s 8 -k 1M --console-log-level=warn --quiet=true",
            "--quiet",
            "--user-agent", user_agent,
            "--concurrent-fragments", "8",
            "--buffer-size", "16K",
            "--http-chunk-size", "5M",
            "--fragment-retries", "3",
            "--check-formats"
        ]

        attempt = 0
        while attempt < retry_count:
            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
            )
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                logging.info(
                    "Video %s downloaded successfully to %s", video_id, save_path)
                return {
                    'status_code': 0,
                    'video_id': video_id,
                    'location': save_path,
                    'server_id': server_id
                }
            else:
                logging.error(
                    "Attempt %d: Error downloading video %s: %s", attempt + 1, video_id, stderr)
                attempt += 1
                delay = random.randint(5, 10)
                time.sleep(delay)

        return {
            'status_code': process.returncode,
            'video_id': video_id,
            'location': None,
            'server_id': server_id,
            'error': stderr
        }
