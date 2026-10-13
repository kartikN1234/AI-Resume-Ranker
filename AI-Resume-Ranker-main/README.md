# AI Resume Ranker 

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Framework-red)



## Project Overview
This is an **AI-powered resume ranking application** designed to help recruiters and hiring managers quickly shortlist candidates.  
It leverages **Natural Language Processing (NLP)** and **semantic similarity models** to evaluate resumes against a given job description and generate an **automated ranking**.
The tool is built to reduce **manual resume screening time**, ensure **fair and unbiased matching**, and improve overall **recruitment efficiency**.

---

## Objective
The primary goals of this project are:
- Automate the resume shortlisting process using intelligent algorithms.
- Provide a **data-driven** and **fair** evaluation of candidate profiles.
- Eliminate manual effort and accelerate the hiring process.

---

## Technologies & Tools Used
**Language:** Python  
**Frameworks & Libraries:**
- **Streamlit** – Interactive Web Dashboard
- **PyMuPDF (fitz)** & **python-docx** – Multi-format Extraction (PDF, DOCX, TXT)
- **SpaCy** – Token Preservation & NLP Preprocessing
- **Sentence Transformers (`all-MiniLM-L6-v2`)** – Deep Semantic Similarity Embeddings
- **Scikit-learn** – Cosine Similarity Vector Scoring

---

## How It Works
### 1. Multi-Format Text Extraction
- Extracts and normalizes text from **PDF**, **DOCX**, and **TXT** files.
- Cleans whitespace, ligatures, and tabular layouts.

### 2. Intelligent Preprocessing
- Protects technical terms (e.g., `C++`, `C#`, `.NET`, `Node.js`, `CI/CD`, `REST API`) from punctuation stripping.
- Lemmatizes text using **SpaCy** while stripping noise and boilerplate.

### 3. Objective Scoring Logic
- **Dynamic Section Re-weighting:** Adapts weights automatically based on detected sections (Skills, Experience, Projects, Education).
- **Domain Detection & Keyword Boost:** Identifies role category (AI/ML, DevOps, Web Dev, Full Stack, Software Engineering, Data, Mobile, HR).
- **Semantic + Keyword Hybrid Scoring:** Combines Sentence-BERT embeddings (75%) with domain keyword alignment (25%) without artificial rank distortion.

### 4. Recruiter Dashboard & Candidate Insights
- **Job Role Presets:** 1-click loading of industry requisitions (Full Stack, ML/AI, DevOps, Data Engineering, Analytics).
- **Leaderboard:** Instant candidate ranking with color-coded fit tiers.
- **Candidate Deep-Dive:** Inspect matched skills, missing skills, and section score breakdowns.
- **AI Interview Screening Guide:** Dynamically generated technical probe questions for matched skills and missing skill gaps.
- **Head-to-Head Compare:** Side-by-side candidate comparison with skill overlap analysis and tie-breaker interview questions.
- **Recruiter Shortlist Pipeline:** Hand-pick and star best-fit candidates (`⭐ Shortlist Candidate`), write internal recruiter interview notes, and review candidates in a dedicated Shortlist Dossier view.
- **Dedicated Shortlist Export:** Export only recruiter-shortlisted candidates with interview notes and matched skills for hiring managers.
- **Interactive Analytics:** Plotly horizontal ranking charts and grouped section comparisons.
- **Complete CSV Export:** Download rich ranking and skill gap reports.

---

## Setup & Running Locally
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Download SpaCy model:
   ```bash
   python -m spacy download en_core_web_sm
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```

## Running Automated Tests
```bash
pytest tests/ -v
```

## Running with Docker
```bash
docker compose up -d
```
Access the application at `http://localhost:8501`.

---

## CI/CD Pipeline
Continuous Integration is configured via **GitHub Actions** (`.github/workflows/ci.yml`) to automatically:
- Run the full pytest test suite across Python 3.11 on every commit and pull request.
- Build and verify the production Docker image.


## Responsibilities
I was responsible for:
- Designing and building the **NLP pipeline** for text extraction and preprocessing
- Implementing the **resume ranking algorithm** with semantic similarity
- Developing the **Streamlit-based web interface**
- Optimizing semantic similarity scoring for better accuracy
- Ensuring efficient handling of multiple resume files

---

## Outcomes & Impact
- Automated resume ranking for multiple job roles  
- Achieved **high accuracy** in identifying relevant resumes compared to manual shortlisting  
- Reduced recruitment time and improved HR decision-making  
- Strengthened skills in **Python, NLP, and machine learning pipelines**


---

## Author
**Sahil Kumbhar**  
- **LinkedIn:** [sahil-kumbhar242004](https://www.linkedin.com/in/sahil-kumbhar242004/?isSelfProfile=true)  
- **GitHub:** [@Sahilkumbhar24](https://github.com/Sahilkumbhar24)
