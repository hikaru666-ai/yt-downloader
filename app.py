from flask import Flask, render_template, request
import yt_dlp
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""

    if request.method == "POST":
        url = request.form.get("url")
        choice = request.form.get("type")
        qlty = request.form.get("quality")

        try:
            qlty = int(qlty)
        except:
            qlty = 720

        if choice == "video":
            ydl_opts = {
                'format': f"bestvideo[height<={qlty}]+bestaudio/best",
                'outtmpl': 'downloads/%(title)s.%(ext)s',
            }
        else:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

        try:
            os.makedirs("downloads", exist_ok=True)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            message = "Download completed ✅"
        except Exception as e:
            message = f"Error: {str(e)}"

    return render_template("index.html", message=message)

if __name__ == "__main__":
    app.run(debug=True)