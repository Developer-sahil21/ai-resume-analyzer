# modules/similarity_scorer.py
# Hybrid similarity scoring: TF-IDF + Semantic (BERT) embeddings

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import re


# ---------------------------------------------------------------------------
# Initialize BERT model (cached)
# ---------------------------------------------------------------------------
try:
    _model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception:
    _model = None


# ---------------------------------------------------------------------------
# Text pre-processing
# ---------------------------------------------------------------------------

def _clean(text: str) -> str:
    """Strip noise characters; keep alphanumeric + spaces."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ---------------------------------------------------------------------------
# TF-IDF Similarity
# ---------------------------------------------------------------------------

def compute_tfidf_similarity(resume_text: str, job_text: str) -> float:
    """
    Return a 0-100 match score using TF-IDF cosine similarity.
    """
    if not resume_text or not job_text:
        return 0.0

    corpus = [_clean(resume_text), _clean(job_text)]

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        stop_words="english",
        max_features=5000,
        sublinear_tf=True,
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
    except ValueError:
        return 0.0

    raw_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    boosted = min(raw_score * 115, 100.0)
    return round(float(boosted), 1)


# ---------------------------------------------------------------------------
# Semantic Similarity (BERT)
# ---------------------------------------------------------------------------

def compute_semantic_similarity(resume_text: str, job_text: str) -> float:
    """
    Return a 0-100 semantic match score using BERT embeddings (sentence-transformers).
    
    This understands context and meaning, not just keyword frequency.
    """
    if not resume_text or not job_text or _model is None:
        return 0.0

    try:
        # Encode texts to embeddings
        embeddings1 = _model.encode(resume_text, convert_to_tensor=False)
        embeddings2 = _model.encode(job_text, convert_to_tensor=False)
        
        # Compute cosine similarity directly with numpy arrays
        from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine
        similarity_score = sklearn_cosine([embeddings1], [embeddings2])[0][0]
        
        # Convert to percentage and ensure it's a Python float
        score = float(similarity_score) * 100
        
        return round(score, 1)
    except Exception as e:
        # Log error for debugging and return 0
        return 0.0


# ---------------------------------------------------------------------------
# Hybrid Similarity Score
# ---------------------------------------------------------------------------

def compute_similarity(resume_text: str, job_text: str) -> dict:
    """
    Return a dict with both similarity scores:
        semantic_score  – BERT-based semantic similarity (0-100)
        keyword_score   – TF-IDF keyword match (0-100)
    
    These are combined later in ats_breakdown with skills match for overall score.
    """
    if not resume_text or not job_text:
        return {
            "semantic_score": 0.0,
            "keyword_score": 0.0,
        }

    semantic = compute_semantic_similarity(resume_text, job_text)
    keyword = compute_tfidf_similarity(resume_text, job_text)

    return {
        "semantic_score": semantic,
        "keyword_score": keyword,
    }


# ---------------------------------------------------------------------------
# ATS-style scoring breakdown
# ---------------------------------------------------------------------------

def ats_breakdown(resume_skills: set, job_skills: set, similarity_scores: dict) -> dict:
    """
    Return a structured ATS breakdown dict using hybrid scoring:
        40% Semantic Similarity (BERT) – understands context
        30% Keyword Match (TF-IDF)     – exact term frequency
        30% Skills Match               – skills coverage
    
    Args:
        resume_skills        – set of skills extracted from resume
        job_skills           – set of skills extracted from job description
        similarity_scores    – dict with 'semantic_score' and 'keyword_score'
    
    Returns:
        dict with matched/missing/extra skills, scores, and grade
    """
    matched = resume_skills & job_skills
    missing = job_skills - resume_skills
    extra   = resume_skills - job_skills

    # Calculate skills match percentage
    skills_score = (len(matched) / len(job_skills) * 100) if job_skills else 0.0
    skills_score = round(skills_score, 1)

    # Extract individual scores
    semantic_score = similarity_scores.get("semantic_score", 0.0)
    keyword_score = similarity_scores.get("keyword_score", 0.0)

    # Weighted hybrid scoring
    # 40% Semantic + 30% Keyword + 30% Skills
    overall = round(
        (semantic_score * 0.40) +
        (keyword_score * 0.30) +
        (skills_score * 0.30),
        1
    )

    # Grade assignment
    if overall >= 80:
        grade = "A"
    elif overall >= 65:
        grade = "B"
    elif overall >= 50:
        grade = "C"
    elif overall >= 35:
        grade = "D"
    else:
        grade = "F"

    return {
        "matched_skills":  sorted(matched),
        "missing_skills":  sorted(missing),
        "extra_skills":    sorted(extra),
        "skills_score":    skills_score,
        "semantic_score":  semantic_score,
        "keyword_score":   keyword_score,
        "similarity_score": semantic_score,  # For UI compatibility
        "overall_score":   overall,
        "grade":           grade,
    }
