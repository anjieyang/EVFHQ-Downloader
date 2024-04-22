import os
import subprocess
import logging


class VideoDownloader:
    @staticmethod
    def download_video(save_dir, video_id, resolution, server_id):
        save_path = os.path.join(save_dir, f"vid_{video_id}.mp4")
        format_code = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        command = [
            "yt-dlp",
            f"https://www.youtube.com/watch?v={video_id}",
            "--output", save_path,
            "-f", format_code,
            "--external-downloader", "aria2c",
            "--external-downloader-args", "aria2c:-x 4 -s 4 -k 1M --console-log-level=warn --quiet",
            "--quiet",
            "--user-agent", user_agent,
            "--concurrent-fragments", "4",
            "--buffer-size", "16K",
            "--http-chunk-size", "512K",
            "--fragment-retries", "2",
            "--check-formats"
        ]
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True
        )
        stdout, stderr = process.communicate()

        if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
            logging.info("Video %s downloaded successfully to %s",
                         video_id, save_path)
            return {
                'status_code': 0,
                'video_id': video_id,
                'location': save_path,
                'server_id': server_id
            }
        else:
            logging.error(
                "Failed to download video %s. Error: %s", video_id, stdout)
            return {
                'status_code': 1,
                'video_id': video_id,
                'location': save_path,
                'server_id': server_id
            }
