from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import tempfile
import os
import glob

app = Flask(__name__)
CORS(app)  # allow frontend

@app.route("/download", methods=["POST"])
def download_video():
    data = request.json
    link = data.get("link")
    if not link:
        return jsonify({"error": "No link provided"}), 400

    try:
        # create a temp folder
        tmpdir = tempfile.mkdtemp()

        # save output as mp4 inside that folder
        outtmpl = os.path.join(tmpdir, "video.%(ext)s")

        ydl_opts = {
            "outtmpl": outtmpl,
            "format": "bv*+ba/b",
            "merge_output_format": "mp4"
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])

        # find the actual file yt-dlp created
        files = glob.glob(os.path.join(tmpdir, "video.*"))
        if not files:
            return jsonify({"error": "No file created"}), 500

        filepath = files[0]

        # send to browser
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
    app.run(port=5000, debug=True)
