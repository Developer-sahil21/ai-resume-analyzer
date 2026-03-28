# modules/suggestions.py
# Rule-based suggestion engine: generates actionable resume improvement tips.

import re
from typing import List


# ---------------------------------------------------------------------------
# Strong action-verb bank (ATS-friendly)
# ---------------------------------------------------------------------------
ACTION_VERBS = [
    "Architected", "Developed", "Engineered", "Implemented", "Designed",
    "Optimised", "Automated", "Deployed", "Reduced", "Increased",
    "Led", "Collaborated", "Delivered", "Migrated", "Built",
    "Streamlined", "Launched", "Integrated", "Maintained", "Refactored",
]

# Weak verbs that should be replaced
WEAK_VERBS = {
    "worked on", "helped with", "did", "made", "was responsible for",
    "assisted", "involved in", "participated in", "dealt with",
}


# ---------------------------------------------------------------------------
# Bullet suggestion templates per skill
# ---------------------------------------------------------------------------
BULLET_TEMPLATES = {
    "python":       "Developed and maintained Python {version} microservices, reducing processing time by ~30%.",
    "machine learning": "Built and deployed ML models using scikit-learn / PyTorch, improving prediction accuracy by X%.",
    "nlp":          "Implemented NLP pipelines (tokenisation, NER, sentiment analysis) using spaCy / HuggingFace.",
    "aws":          "Designed and deployed cloud-native solutions on AWS (EC2, S3, Lambda, RDS), cutting infrastructure costs.",
    "docker":       "Containerised applications using Docker and orchestrated deployments with Kubernetes / Docker Compose.",
    "react":        "Built responsive single-page applications with React, improving user engagement by X%.",
    "sql":          "Wrote optimised SQL queries and managed relational databases (PostgreSQL / MySQL) for production workloads.",
    "flask":        "Developed RESTful APIs using Flask, serving X+ requests per day with 99.9% uptime.",
    "git":          "Managed source control with Git/GitHub, following GitFlow branching strategy across a team of X engineers.",
    "data analysis":"Performed end-to-end data analysis (collection, cleaning, visualisation) using Pandas, NumPy, and Matplotlib.",
    "tensorflow":   "Trained and fine-tuned deep learning models in TensorFlow/Keras, achieving X% accuracy on benchmark.",
    "kubernetes":   "Orchestrated container workloads on Kubernetes, enabling zero-downtime rolling deployments.",
    "agile":        "Participated in Agile/Scrum ceremonies (sprints, retrospectives) delivering features on a bi-weekly cadence.",
    "communication":"Presented technical findings to non-technical stakeholders, improving cross-team alignment.",
    "leadership":   "Led a team of X engineers, conducting code reviews and mentoring junior developers.",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_bullet_suggestions(missing_skills: List[str]) -> List[str]:
    """
    For each missing skill, return a ready-to-use bullet point template.
    Skills without a template get a generic suggestion.
    """
    suggestions = []
    for skill in missing_skills[:8]:   # cap to avoid overwhelming the user
        if skill in BULLET_TEMPLATES:
            suggestions.append(f"• [{skill.upper()}] {BULLET_TEMPLATES[skill]}")
        else:
            suggestions.append(
                f"• [{skill.upper()}] Add a bullet demonstrating hands-on "
                f"experience with {skill} – quantify impact where possible."
            )
    return suggestions


def generate_improvement_tips(
    resume_text: str,
    missing_skills: List[str],
    overall_score: float,
    matched_skills: List[str],
) -> List[str]:
    """
    Return a list of human-readable improvement tips based on:
    - Overall match score
    - Missing skills
    - Presence/absence of quantified metrics in the resume
    - Weak verb usage
    """
    tips: List[str] = []
    text_lower = resume_text.lower()

    # --- Score-based top-level advice ----------------------------------------
    if overall_score < 40:
        tips.append(
            "🔴 Low match: Tailor your resume heavily to this specific role. "
            "Mirror the exact language used in the job description."
        )
    elif overall_score < 65:
        tips.append(
            "🟡 Moderate match: Incorporate more role-specific keywords and "
            "reorder sections to front-load the most relevant experience."
        )
    else:
        tips.append(
            "🟢 Good match: Fine-tune by ensuring every JD keyword appears "
            "naturally in context, not just as a list."
        )

    # --- Missing skills ------------------------------------------------------
    if missing_skills:
        top_missing = ", ".join(missing_skills[:5])
        tips.append(
            f"📌 Add evidence of these missing skills: {top_missing}. "
            "Even a side project or course counts."
        )

    # --- Quantification check ------------------------------------------------
    numbers_found = len(re.findall(r"\b\d+[%x]?\b", resume_text))
    if numbers_found < 5:
        tips.append(
            "📊 Quantify your achievements (e.g., 'reduced load time by 40%', "
            "'managed a team of 6'). ATS and human reviewers both favour metrics."
        )

    # --- Weak verb check -----------------------------------------------------
    weak_found = [v for v in WEAK_VERBS if v in text_lower]
    if weak_found:
        examples = ", ".join(f'"{v}"' for v in weak_found[:3])
        tips.append(
            f"💬 Replace weak phrases ({examples}) with strong action verbs like: "
            + ", ".join(ACTION_VERBS[:5]) + "."
        )

    # --- Length heuristic ----------------------------------------------------
    word_count = len(resume_text.split())
    if word_count < 200:
        tips.append(
            "📝 Your resume appears short. Aim for 400–700 words for an "
            "entry-level role, 600–900 for mid-level."
        )
    elif word_count > 1000:
        tips.append(
            "✂️ Your resume may be too long for ATS parsing. "
            "Trim to 1–2 pages; focus on the last 5–7 years."
        )

    # --- Skills section tip --------------------------------------------------
    if "skills" not in text_lower and "technical skills" not in text_lower:
        tips.append(
            "🗂️ Add a dedicated 'Skills' section near the top. "
            "ATS systems scan for it explicitly."
        )

    # --- Summary / objective -------------------------------------------------
    if "summary" not in text_lower and "objective" not in text_lower and "profile" not in text_lower:
        tips.append(
            "✏️ Include a 2–3 sentence professional summary at the top "
            "that echoes the job title and key requirements."
        )

    return tips
