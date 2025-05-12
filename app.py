
import os
from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import tempfile
from io import BytesIO

app = Flask(__name__)

def get_formats(url):
    ydl_opts = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info.get('formats', [info])
        result = []
        for f in formats:
            result.append({
                'format_id': f['format_id'],
                'ext': f['ext'],
                'resolution': f"{str(f.get('height', ''))+'p' if f.get('height') else 'audio'}",
                'note': f.get('format_note', '')
            })
        return result

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/formats", methods=["POST"])
def formats():
    url = request.form.get("url")
    try:
        formats = get_formats(url)
        return jsonify({"success": True, "formats": formats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")
    format_id = request.form.get("format_id")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                'format': format_id
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
            # File ko memory me load karo
            with open(filename, "rb") as f:
                file_data = BytesIO(f.read())
            file_data.seek(0)
            download_name = os.path.basename(filename)
            return send_file(
                file_data,
                as_attachment=True,
                download_name=download_name,
                mimetype="application/octet-stream"
            )
    except Exception as e:
        print("Download error:", e)
        return f"Error: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)
