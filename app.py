from flask import Flask, render_template, request
import yt_dlp
import os

app = Flask(__name__)

# Make downloads folder
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    if request.method == "POST":
        url = request.form.get("url")
        mode = request.form.get("mode")
        quality = request.form.get("quality")

        try:
            qlty = int(quality)
        except:
            qlty = 720

        if mode == "video":
            ydl_opts = {
                'format': f"bestvideo[height<={qlty}]+bestaudio/best",
                'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            }
        else:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            message = "Download completed!"
        except Exception as e:
            message = f"Error: {str(e)}"

    return render_template("index.html", message=message)

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)