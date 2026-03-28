# ResumeIQ — AI Resume Analyzer & Job Matcher

A clean, production-ready web application that parses resumes, extracts skills via NLP, computes ATS-style match scores, and generates improvement suggestions.

---

## Project Structure

```
ai_resume_analyzer/
├── app.py                    # Flask backend & API routes
├── requirements.txt          # Python dependencies
├── setup.sh                  # One-command setup script
├── modules/
│   ├── __init__.py
│   ├── resume_parser.py      # PDF & text extraction (pdfplumber)
│   ├── skill_extractor.py    # Hybrid NLP skill detection (spaCy + keyword bank)
│   ├── similarity_scorer.py  # TF-IDF cosine similarity + ATS breakdown
│   └── suggestions.py        # Rule-based improvement tips & bullet templates
└── templates/
    └── index.html            # Full-stack UI (no separate JS framework needed)
```

---

## Tech Stack

| Layer       | Library                |
| ----------- | ---------------------- |
| Backend     | Flask 3.x              |
| PDF Parsing | pdfplumber             |
| NLP         | spaCy (en_core_web_sm) |
| ML Scoring  | scikit-learn (TF-IDF)  |
| Frontend    | Vanilla HTML/CSS/JS    |

---

## Installation & Running

### Prerequisites

- Python 3.10 or higher
- pip

### Option A — One-command setup (Linux/macOS)

```bash
cd ai_resume_analyzer
bash setup.sh
source .venv/bin/activate
python app.py
```

### Option B — Manual steps (Windows / any OS)

```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate it
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download spaCy model
python -m spacy download en_core_web_sm

# 5. Run the app
python app.py
```

### Open in browser

```
http://localhost:5000
```

---

## How It Works (ATS Scoring Explained)

### Score Composition

The **Overall Score (0–100%)** is a 50/50 weighted blend:

| Component           | Weight | Description                               |
| ------------------- | ------ | ----------------------------------------- |
| Semantic Similarity | 50%    | TF-IDF cosine similarity across full text |
| Keyword Coverage    | 50%    | % of JD skills found in resume            |

### Processing Pipeline

1. **Resume parsed** — PDF text extracted via pdfplumber or raw text accepted
2. **Skills extracted** — Hybrid: regex scan over 100-skill bank + spaCy noun-chunk NLP
3. **TF-IDF vectors** built from bigrams, stop-words removed, sublinear TF
4. **Cosine similarity** computed between resume and JD vectors
5. **Skill overlap** — matched/missing/extra skills computed from both skill sets
6. **Suggestions** — rule-based tips + ready-to-use bullet templates generated

---

## Example Test Input

### Sample Resume Text

```
Sahil Khan | sahil@example.com | github.com/sahil

SUMMARY
Python developer with 3 years of experience building RESTful APIs and data pipelines.

SKILLS
Python, Flask, SQL, PostgreSQL, Docker, Git, AWS, Pandas, Data Analysis, Agile

EXPERIENCE
Backend Engineer — Acme Corp (2021–2024)
• Developed Python microservices processing 50k events/day
• Designed RESTful APIs consumed by 3 frontend teams
• Automated ETL pipelines reducing manual effort by 40%
• Deployed services on AWS EC2 with Docker containers

EDUCATION
B.Tech Computer Science — IIT Mumbai, 2025
```

### Sample Job Description Text

```
We are looking for a Senior Python Engineer to join our ML platform team.

Requirements:
- 3+ years Python experience
- Strong knowledge of machine learning and scikit-learn
- Experience with Flask or FastAPI
- Proficiency in SQL and PostgreSQL
- Familiarity with Docker and Kubernetes
- AWS or GCP cloud experience
- Experience with NLP or deep learning is a plus
- Git, CI/CD, Agile development practices
```

### Expected Output

- **Overall Score**: ~62–70%
- **Missing Skills**: machine learning, scikit-learn, kubernetes, nlp, deep learning
- **Matched Skills**: python, flask, sql, postgresql, docker, aws, git, agile, data analysis

---

## Customisation

### Add more skills to the taxonomy

Edit `SKILL_BANK` in `modules/skill_extractor.py` — just add lowercase strings.

### Add bullet templates for more skills

Edit `BULLET_TEMPLATES` dict in `modules/suggestions.py`.

### Change scoring weights

Edit `ats_breakdown()` in `modules/similarity_scorer.py` — adjust the 0.5/0.5 blend.

---

## API Endpoints

| Method | Endpoint       | Description                                  |
| ------ | -------------- | -------------------------------------------- |
| POST   | `/api/analyze` | Submit resume and JD for matching & analysis |
| GET    | `/`            | Serve the web interface                      |

### POST /api/analyze

**Request Body:**

```json
{
  "resume_text": "...",
  "job_description": "..."
}
```

**Response:**

```json
{
  "overall_score": 72,
  "semantic_similarity": 0.68,
  "keyword_coverage": 0.76,
  "matched_skills": ["python", "flask", "sql"],
  "missing_skills": ["kubernetes", "deep learning"],
  "extra_skills": ["docker"],
  "suggestions": [...]
}
```

---

## Features

✅ **Multi-format Resume Support** — PDF, TXT, DOCX  
✅ **Smart Skill Extraction** — Hybrid NLP + keyword bank approach  
✅ **ATS-Score Calculation** — Semantic + keyword-based matching  
✅ **Actionable Suggestions** — Improvement tips with bullet templates  
✅ **Clean Web Interface** — Responsive, no JS framework bloat  
✅ **Fast Processing** — Scores generated in <2 seconds

---

## Limitations & Known Issues

- Scanned/image PDFs are not supported (text PDFs only)
- Skill extraction is English-only
- Bullet suggestions are templates — always customise with real numbers
- Large resumes (>50 pages) may have reduced accuracy

---

## Contributing

Contributions are welcome! Here's how to help:

1. **Fork** the repository
2. **Create a feature branch**: `git checkout -b feature/your-feature`
3. **Commit changes**: `git commit -m 'Add your feature'`
4. **Push to branch**: `git push origin feature/your-feature`
5. **Open a Pull Request**

---

## Feedback & Support

Have questions or found a bug? Open an issue on [GitHub Issues](https://github.com/Developer-sahil21/ai-resume-analyzer/issues).

**Maintained by:** [Mohammad Sahil Khan](https://github.com/Developer-sahil21)  
**Last Updated:** March 2026
