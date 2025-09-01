from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import tempfile
import os
import glob

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Flask Test</title></head>
    <body>
        <h2>Hello, Flask is running ✅</h2>
        <p>If you see this page, the server is working fine.</p>
    </body>
    </html>
    """

@app.route("/download", methods=["POST"])
def download_video():
    data = request.json
    link = data.get("link")
    if not link:
        return jsonify({"error": "No link provided"}), 400

    try:
        tmpdir = tempfile.mkdtemp()
        outtmpl = os.path.join(tmpdir, "video.%(ext)s")

        ydl_opts = {
            "outtmpl": outtmpl,
            "format": "bv*+ba/b",
            "merge_output_format": "mp4"
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])

        files = glob.glob(os.path.join(tmpdir, "video.*"))
        if not files:
            return jsonify({"error": "No file created"}), 500

        filepath = files[0]

        response = send_file(
            filepath,
            as_attachment=True,
            download_name="video.mp4",
            mimetype="video/mp4"
        )

        @response.call_on_close
        def cleanup():
            try:
                os.remove(filepath)
                os.rmdir(tmpdir)
            except:
                pass

        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
