# app.py  –  AI Resume Analyzer & Job Matcher  (Flask backend)

import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename

from modules.resume_parser   import extract_text_from_upload, clean_text
from modules.skill_extractor  import extract_skills
from modules.similarity_scorer import compute_similarity, ats_breakdown
from modules.suggestions       import generate_bullet_suggestions, generate_improvement_tips

# ---------------------------------------------------------------------------
# App configuration
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024   # 5 MB upload limit
ALLOWED_EXTENSIONS = {"pdf", "txt"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Serve the main UI page."""
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    POST /analyze
    Form data:
        resume_file  – PDF or TXT upload   (optional if resume_text provided)
        resume_text  – plain text fallback  (optional if file uploaded)
        job_desc     – job description text (required)
    Returns JSON result dict.
    """
    # ---- 1. Extract resume text -------------------------------------------
    resume_text = ""
    file = request.files.get("resume_file")

    if file and file.filename and allowed_file(file.filename):
        try:
            resume_text = extract_text_from_upload(file)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
    else:
        # Fall back to pasted text
        resume_text = clean_text(request.form.get("resume_text", ""))

    if not resume_text.strip():
        return jsonify({"error": "Please upload a resume file or paste resume text."}), 400

    # ---- 2. Extract job description ----------------------------------------
    job_text = clean_text(request.form.get("job_desc", ""))
    if not job_text.strip():
        return jsonify({"error": "Job description cannot be empty."}), 400

    # ---- 3. Core NLP + scoring pipeline ------------------------------------
    resume_skills = extract_skills(resume_text)
    job_skills    = extract_skills(job_text)
    similarity_scores = compute_similarity(resume_text, job_text)
    breakdown     = ats_breakdown(resume_skills, job_skills, similarity_scores)

    # ---- 4. Suggestions ----------------------------------------------------
    bullets = generate_bullet_suggestions(breakdown["missing_skills"])
    tips    = generate_improvement_tips(
        resume_text,
        breakdown["missing_skills"],
        breakdown["overall_score"],
        breakdown["matched_skills"],
    )

    # ---- 5. Build response -------------------------------------------------
    return jsonify({
        "overall_score":    breakdown["overall_score"],
        "grade":            breakdown["grade"],
        "similarity_score": breakdown["semantic_score"],  # For frontend compatibility
        "semantic_score":   breakdown["semantic_score"],
        "keyword_score":    breakdown["keyword_score"],
        "skills_score":     breakdown["skills_score"],
        "matched_skills":   breakdown["matched_skills"],
        "missing_skills":   breakdown["missing_skills"],
        "extra_skills":     breakdown["extra_skills"],
        "bullet_suggestions": bullets,
        "improvement_tips":   tips,
    })


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(413)
def too_large(_):
    return jsonify({"error": "File too large. Maximum upload size is 5 MB."}), 413


@app.errorhandler(500)
def server_error(exc):
    app.logger.error("Unhandled exception: %s", exc)
    return jsonify({"error": "Internal server error. Please try again."}), 500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)
