# modules/skill_extractor.py
# Hybrid skill extractor: hardcoded keyword bank + spaCy NLP noun-chunk extraction

import re
import spacy

# ---------------------------------------------------------------------------
# Hardcoded skill taxonomy (covers most tech/non-tech job postings)
# ---------------------------------------------------------------------------
SKILL_BANK = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "bash", "shell",

    # Web / Frontend
    "html", "css", "react", "reactjs", "angular", "vue", "vuejs", "nextjs",
    "nuxtjs", "svelte", "tailwind", "bootstrap", "sass", "webpack", "vite",

    # Backend / APIs
    "flask", "django", "fastapi", "nodejs", "express", "spring", "rails",
    "graphql", "rest", "restful", "grpc", "soap",

    # Databases
    "sql", "mysql", "postgresql", "postgres", "mongodb", "redis", "sqlite",
    "oracle", "cassandra", "dynamodb", "elasticsearch", "neo4j", "firebase",

    # Cloud / DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "k8s", "terraform",
    "ansible", "jenkins", "ci/cd", "github actions", "gitlab", "linux",
    "nginx", "apache", "helm",

    # Data / ML / AI
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
    "matplotlib", "seaborn", "tableau", "power bi", "spark", "hadoop",
    "airflow", "mlflow", "huggingface", "llm", "openai", "langchain",
    "data analysis", "data engineering", "etl", "feature engineering",

    # Version Control / Collaboration
    "git", "github", "gitlab", "bitbucket", "jira", "confluence", "notion",
    "agile", "scrum", "kanban",

    # Soft Skills
    "communication", "leadership", "teamwork", "problem solving",
    "critical thinking", "project management", "time management",
    "collaboration", "presentation", "mentoring",

    # Security
    "cybersecurity", "penetration testing", "owasp", "sso", "oauth",
    "jwt", "encryption", "ssl", "tls", "iam",

    # Mobile
    "android", "ios", "react native", "flutter", "xamarin",

    # Testing
    "unit testing", "integration testing", "selenium", "pytest",
    "jest", "cypress", "test automation", "qa",
}

# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------

def _normalise(text: str) -> str:
    """Lower-case and collapse whitespace."""
    return re.sub(r"\s+", " ", text.lower().strip())


def _load_spacy():
    """Load spaCy model, falling back to blank English if model not installed."""
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        # Blank model still gives us tokenisation + basic NER
        return spacy.blank("en")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_skills(text: str) -> set[str]:
    """
    Return a set of skills found in *text* using:
    1. Direct substring matching against SKILL_BANK
    2. spaCy noun-chunk extraction (catches multi-word phrases not in bank)
    """
    if not text:
        return set()

    norm_text = _normalise(text)
    found: set[str] = set()

    # --- Pass 1: hardcoded bank scan -----------------------------------------
    for skill in SKILL_BANK:
        # Match whole word / phrase boundaries
        pattern = r"(?<![a-z0-9/])" + re.escape(skill) + r"(?![a-z0-9/])"
        if re.search(pattern, norm_text):
            found.add(skill)

    # --- Pass 2: spaCy noun chunks -------------------------------------------
    nlp = _load_spacy()
    doc = nlp(norm_text[:10_000])  # cap to avoid memory spikes

    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.strip()
        if 2 <= len(chunk_text.split()) <= 4:          # 2-4 word technical phrases
            if chunk_text in SKILL_BANK:
                found.add(chunk_text)

    # Also grab single-token nouns that match the bank
    for token in doc:
        if token.pos_ in {"NOUN", "PROPN"} and token.text in SKILL_BANK:
            found.add(token.text)

    return found
