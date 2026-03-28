#!/usr/bin/env bash
# setup.sh  –  One-time setup for AI Resume Analyzer
# Usage: bash setup.sh

set -e

echo "═══════════════════════════════════════"
echo " AI Resume Analyzer — Setup Script"
echo "═══════════════════════════════════════"

# 1. Create & activate virtual environment
if [ ! -d ".venv" ]; then
    echo "→ Creating virtual environment…"
    python3 -m venv .venv
fi

source .venv/bin/activate

# 2. Upgrade pip silently
pip install --upgrade pip -q

# 3. Install dependencies
echo "→ Installing Python dependencies…"
pip install -r requirements.txt -q

# 4. Download spaCy English model
echo "→ Downloading spaCy en_core_web_sm model…"
python -m spacy download en_core_web_sm -q

echo ""
echo "✓ Setup complete!"
echo ""
echo "Run the app with:"
echo "  source .venv/bin/activate"
echo "  python app.py"
echo ""
echo "Then open: http://localhost:5000"
