from flask import Flask, render_template, request, send_from_directory
import yt_dlp
import os

app = Flask(__name__)

# Folder to save downloads
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Store progress in memory
download_progress = {}

def progress_hook(d):
    """Hook to update download progress"""
    video_id = d.get('info_dict', {}).get('id', 'unknown')
    if d['status'] == 'downloading':
        download_progress[video_id] = d.get('_percent_str', '0%')
    elif d['status'] == 'finished':
        download_progress[video_id] = "100%"

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    download_link = None
    progress = "0%"  # ⚡ define a default here

    if request.method == "POST":
        url = request.form.get("url")
        mode = request.form.get("mode")
        quality = request.form.get("quality")

        try:
            qlty = int(quality) if quality else 720
        except (ValueError, TypeError):
            qlty = 720

        # extract video id
        video_id = url.split("v=")[-1] if "v=" in url else "unknown"
        download_progress[video_id] = "0%"

        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'progress_hooks': [progress_hook]
        }

        if mode == "video":
            ydl_opts['format'] = f"bestvideo[height<={qlty}]+bestaudio/best"
        else:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if mode == "audio":
                    filename = os.path.splitext(filename)[0] + ".mp3"

                download_link = os.path.basename(filename)

        except Exception as e:
            message = f"Error: {str(e)}"

        # ⚡ Safe: get progress or default 0%
        progress = download_progress.get(video_id, "0%")

    return render_template("index.html", message=message, download_link=download_link, progress=progress)
# Serve downloaded files
@app.route('/downloads/<filename>')
def serve_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)