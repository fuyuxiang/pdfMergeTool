import os
from io import BytesIO

from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename

try:
    # pypdf is actively maintained
    from pypdf import PdfReader, PdfWriter
except Exception:  # pragma: no cover
    # Fallback if user installs PyPDF2 instead of pypdf
    from PyPDF2 import PdfReader, PdfWriter  # type: ignore


ALLOWED_EXTENSIONS = {"pdf"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def create_app() -> Flask:
    app = Flask(__name__)

    # Secret key: set FLASK_SECRET_KEY in production
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

    # Optional upload size limit (bytes). Example: 200MB -> 200 * 1024 * 1024
    max_len = os.environ.get("MAX_CONTENT_LENGTH", "").strip()
    if max_len.isdigit():
        app.config["MAX_CONTENT_LENGTH"] = int(max_len)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/merge")
    def merge():
        files = request.files.getlist("pdfs")
        if not files or all(f.filename == "" for f in files):
            flash("请先选择至少一个 PDF 文件。", "error")
            return redirect(url_for("index"))

        writer = PdfWriter()
        merged_pages = 0

        for f in files:
            if not f or f.filename == "":
                continue

            filename = secure_filename(f.filename)
            if not allowed_file(filename):
                flash(f"不支持的文件类型：{filename}（仅支持 .pdf）", "error")
                return redirect(url_for("index"))

            data = f.read()
            if not data:
                flash(f"文件为空：{filename}", "error")
                return redirect(url_for("index"))

            try:
                reader = PdfReader(BytesIO(data))

                # Encrypted PDFs: try empty password, otherwise fail fast
                if getattr(reader, "is_encrypted", False):
                    try:
                        reader.decrypt("")  # type: ignore[attr-defined]
                    except Exception:
                        flash(f"无法读取加密 PDF：{filename}（需要密码）", "error")
                        return redirect(url_for("index"))

                for page in reader.pages:
                    writer.add_page(page)
                    merged_pages += 1

            except Exception:
                flash(f"读取失败：{filename} 可能不是有效 PDF。", "error")
                return redirect(url_for("index"))

        if merged_pages == 0:
            flash("没有可合并的页面。", "error")
            return redirect(url_for("index"))

        output = BytesIO()
        writer.write(output)
        output.seek(0)

        out_name = (request.form.get("output_name") or "").strip() or "merged"
        out_name = secure_filename(out_name) or "merged"
        if not out_name.lower().endswith(".pdf"):
            out_name += ".pdf"

        return send_file(
            output,
            as_attachment=True,
            download_name=out_name,
            mimetype="application/pdf",
            max_age=0,
            etag=False,
            last_modified=None,
        )

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
