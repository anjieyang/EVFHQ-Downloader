import os
import subprocess
import logging


class VideoDownloader:
    @staticmethod
    def download_video(save_dir, video_id, resolution, server_id):
        save_path = os.path.join(save_dir, f"vid_{video_id}.mp4")
        # format_code = "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]" if resolution == 'sd' else "bestvideo[height>=720][ext=mp4]+bestaudio[ext=m4a]/best[height>=720]"
        format_code = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        command = [
            "yt-dlp",
            f"https://www.youtube.com/watch?v={video_id}",
            "--output", f"{save_path}",
            "-f", format_code,
            "--external-downloader", "aria2c",
            "--external-downloader-args", "aria2c:-x 4 -s 4 -k 5M --console-log-level=warn --quiet=true",
            "--quiet",
            "--concurrent-fragments", "8",
            "--buffer-size", "32K",
            "--http-chunk-size", "1M",
            "--fragment-retries", "3",
        ]
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True
        )
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            logging.info("Video %s downloaded successfully to %s",
                         video_id, save_path)
        else:
            logging.error("Error downloading video %s: %s", video_id, stdout)

        return {
            'status_code': process.returncode,
            'video_id': video_id,
            'location': save_path,
            'server_id': server_id
        }
