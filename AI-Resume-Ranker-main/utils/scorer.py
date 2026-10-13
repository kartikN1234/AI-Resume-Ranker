import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Initialize model Once
model = SentenceTransformer('all-MiniLM-L6-v2')

SKILL_EXPANSIONS = {
    "mern stack": ["MongoDB", "Express.js", "React.js", "Node.js", "JavaScript", "REST API", "HTML", "CSS", "Git"],
    "mean stack": ["MongoDB", "Express.js", "Angular", "Node.js", "JavaScript", "REST API", "HTML", "CSS", "Git"],
    "full stack": ["HTML", "CSS", "JavaScript", "React.js", "Node.js", "Express.js", "MongoDB", "SQL", "Git"],
    "devops": ["Docker", "Kubernetes", "CI/CD", "Terraform", "AWS", "Linux", "Jenkins", "Git"],
    "cloud engineer": ["AWS", "Azure", "GCP", "Terraform", "Docker", "Kubernetes", "CloudFormation"],
    "data science": ["Python", "Pandas", "NumPy", "Scikit-Learn", "Machine Learning", "SQL", "Data Visualization"],
}

# Domain keyword dictionary
JOB_KEYWORDS = {
    "ML_AI": {
        'pytorch': 0.15, 'tensorflow': 0.15, 'keras': 0.1,
        'huggingface': 0.12, 'spark': 0.1, 'scikit-learn': 0.1,
        'natural language processing': 0.25, 'computer vision': 0.25,
        'llm': 0.35, 'transformer': 0.2, 'generative ai': 0.3,
        'deep learning': 0.2, 'neural network': 0.15,
        'deployed': 0.15, 'model accuracy': 0.1, 'fine-tuning': 0.2,
        'langchain': 0.2, 'rag': 0.25, 'vector database': 0.2
    },
    "CLOUD_DEVOPS": {
        'docker': 0.2, 'kubernetes': 0.25, 'terraform': 0.2,
        'aws': 0.2, 'azure': 0.15, 'gcp': 0.15, 'ci/cd': 0.2,
        'jenkins': 0.15, 'ansible': 0.15, 'linux': 0.15,
        'prometheus': 0.1, 'grafana': 0.1, 'helm': 0.15
    },
    "WEB_DEV": {
        'react': 0.2, 'node.js': 0.2, 'typescript': 0.15, 'django': 0.15,
        'express': 0.12, 'angular': 0.12, 'next.js': 0.15, 'tailwind': 0.08,
        'rest api': 0.15, 'html': 0.05, 'css': 0.05, 'graphql': 0.12
    },
    "FULLSTACK": {
        'react': 0.15, 'node.js': 0.15, 'typescript': 0.15,
        'express': 0.12, 'mongodb': 0.12, 'postgresql': 0.12,
        'graphql': 0.1, 'docker': 0.1, 'rest api': 0.12, 'sql': 0.1
    },
    "SOFTWARE_DEV": {
        'java': 0.2, 'c++': 0.2, 'python': 0.15, 'c#': 0.15,
        'spring boot': 0.18, 'microservices': 0.15, 'rest api': 0.12,
        'git': 0.08, 'sql': 0.12, 'oop': 0.1
    },
    "DATA_ENGINEER": {
        'spark': 0.2, 'hadoop': 0.15, 'kafka': 0.2,
        'airflow': 0.18, 'databricks': 0.15, 'etl': 0.15,
        'snowflake': 0.18, 'bigquery': 0.15, 'sql': 0.15, 'dbt': 0.15
    },
    "DATA_ANALYST": {
        'excel': 0.15, 'tableau': 0.2, 'power bi': 0.2,
        'sql': 0.2, 'python': 0.12, 'data visualization': 0.15,
        'statistics': 0.12, 'pandas': 0.1
    },
    "MOBILE_DEV": {
        'flutter': 0.25, 'react native': 0.25, 'swift': 0.2,
        'kotlin': 0.2, 'ios': 0.15, 'android': 0.15, 'dart': 0.15
    },
    "HR": {
        'talent acquisition': 0.2, 'recruitment': 0.2,
        'payroll': 0.15, 'employee relations': 0.15,
        'hr policies': 0.12, 'performance management': 0.15, 'onboarding': 0.1
    }
}

DOMAIN_LABELS = {
    "ML_AI": "AI & Machine Learning",
    "CLOUD_DEVOPS": "Cloud & DevOps",
    "WEB_DEV": "Web Development",
    "FULLSTACK": "Full Stack Engineering",
    "SOFTWARE_DEV": "Software Engineering",
    "DATA_ENGINEER": "Data Engineering",
    "DATA_ANALYST": "Data Analytics & BI",
    "MOBILE_DEV": "Mobile App Development",
    "HR": "Human Resources"
}

def expand_jd(jd_text):
    jd_lower = jd_text.lower()
    expanded_text = jd_text
    for keyword, skills in SKILL_EXPANSIONS.items():
        if re.search(rf"\b{keyword}\b", jd_lower):
            expanded_text += "\nRequired Skills: " + ", ".join(skills)
    return expanded_text

def detect_domain(jd_text: str):
    text = jd_text.lower()
    if any(w in text for w in ["machine learning", "deep learning", "llm", "nlp", "pytorch", "tensorflow", "generative ai"]):
        return "ML_AI"
    if any(w in text for w in ["devops", "kubernetes", "docker", "terraform", "ci/cd", "aws", "cloud engineer"]):
        return "CLOUD_DEVOPS"
    if any(w in text for w in ["flutter", "react native", "swift", "kotlin", "ios", "android"]):
        return "MOBILE_DEV"
    if any(w in text for w in ["full stack", "fullstack", "mern", "mean"]):
        return "FULLSTACK"
    if any(w in text for w in ["react", "angular", "vue", "frontend", "next.js"]):
        return "WEB_DEV"
    if any(w in text for w in ["spark", "kafka", "airflow", "databricks", "snowflake", "data warehouse"]):
        return "DATA_ENGINEER"
    if any(w in text for w in ["tableau", "power bi", "excel", "data analyst", "business intelligence"]):
        return "DATA_ANALYST"
    if any(w in text for w in ["recruitment", "talent acquisition", "payroll", "human resources", "hr manager"]):
        return "HR"
    return "SOFTWARE_DEV"

def extract_section(text, pattern):
    """Robust regex to extract section contents between dynamic headings."""
    try:
        # Matches heading at start of line or with bullet/colon
        match = re.search(
            fr'(?:^|\n)\s*(?:#+\s*)?(?:{pattern})[\s:]*\n(.*?)(?=\n\s*(?:#+\s*)?[A-Z][A-Z\s]{{2,}}[\s:]*\n|\Z)',
            text,
            re.DOTALL | re.IGNORECASE
        )
        if match:
            clean = match.group(1).strip()
            return clean if len(clean) > 10 else ""
        return ""
    except Exception:
        return ""

def preprocess_technical(text):
    keep_terms = {
        'nlp', 'llm', 'gan', 'bert', 'gpt', 'transformer',
        'pytorch', 'tensorflow', 'cnn', 'rnn', 'huggingface',
        'aws', 'gcp', 'azure', 'docker', 'kubernetes', 'ci/cd',
        'sql', 'nosql', 'api', 'rest', 'graphql'
    }
    text = text.lower()
    for term in keep_terms:
        text = re.sub(rf'\b{term}\b', term.upper(), text)
    return text

def calculate_detailed_score(jd_text, resume_text):
    """
    Computes an objective, calibrated match analysis between Job Description and Resume.
    Returns:
        dict: {
            'overall_score': float (0-100),
            'domain': str,
            'domain_label': str,
            'matched_skills': list[str],
            'missing_skills': list[str],
            'section_scores': dict[str, float]
        }
    """
    try:
        expanded_jd = expand_jd(jd_text)
        domain = detect_domain(expanded_jd)
        keyword_dict = JOB_KEYWORDS.get(domain, JOB_KEYWORDS["SOFTWARE_DEV"])

        # Check section texts
        headerized_resume = "\n" + resume_text + "\n"
        sections = {
            'skills': extract_section(headerized_resume, r'SKILLS|TECHNICAL SKILLS|TECH STACK|COMPETENCIES|CORE COMPETENCIES'),
            'experience': extract_section(headerized_resume, r'EXPERIENCE|WORK EXPERIENCE|EMPLOYMENT|WORK HISTORY|PROFESSIONAL EXPERIENCE'),
            'projects': extract_section(headerized_resume, r'PROJECTS|PERSONAL PROJECTS|KEY PROJECTS|RESEARCH PROJECTS|ACADEMIC PROJECTS'),
            'education': extract_section(headerized_resume, r'EDUCATION|ACADEMIC BACKGROUND|QUALIFICATIONS')
        }

        # Calculate overall and section embeddings
        jd_emb = model.encode([expanded_jd])
        
        # Base section weights
        base_weights = {'skills': 0.45, 'experience': 0.30, 'projects': 0.15, 'education': 0.10}
        
        # Determine available sections and dynamically re-normalize weights
        available_sections = {k: v for k, v in sections.items() if v and len(v.strip()) > 15}
        section_scores = {}

        if available_sections:
            total_active_weight = sum(base_weights[k] for k in available_sections.keys())
            normalized_weights = {k: base_weights[k] / total_active_weight for k in available_sections.keys()}

            for section_name, section_content in available_sections.items():
                processed_sec = preprocess_technical(section_content)
                sec_emb = model.encode([processed_sec])
                sim = float(cosine_similarity(jd_emb, sec_emb)[0][0])
                sim = max(0.0, min(1.0, sim))
                section_scores[section_name] = round(sim * 100, 1)

            # Weighted semantic score
            semantic_score = sum(section_scores[k] * normalized_weights[k] for k in available_sections.keys())
        else:
            # Fallback if no specific section headers matched: evaluate full resume
            full_emb = model.encode([resume_text])
            sim = float(cosine_similarity(jd_emb, full_emb)[0][0])
            sim = max(0.0, min(1.0, sim))
            semantic_score = sim * 100
            section_scores['overall'] = round(semantic_score, 1)

        # Keyword & Hard-Skill analysis
        resume_lower = resume_text.lower()
        jd_lower = expanded_jd.lower()

        matched_skills = []
        missing_skills = []
        keyword_bonus_score = 0.0

        for keyword, weight in keyword_dict.items():
            in_jd = bool(re.search(rf'\b{re.escape(keyword)}\b', jd_lower))
            in_resume = bool(re.search(rf'\b{re.escape(keyword)}\b', resume_lower))

            if in_jd:
                if in_resume:
                    matched_skills.append(keyword.title())
                    keyword_bonus_score += (weight * 25.0)  # contribute up to bonus
                else:
                    missing_skills.append(keyword.title())

        # Calibrated final score
        # Base semantic similarity forms 75% of score, keyword overlap forms 25%
        keyword_factor = min(25.0, keyword_bonus_score)
        calibrated_score = (semantic_score * 0.75) + keyword_factor

        # Confine between 0% and 100%
        final_score = round(max(5.0, min(99.5, calibrated_score)), 1)

        return {
            'overall_score': final_score,
            'domain': domain,
            'domain_label': DOMAIN_LABELS.get(domain, domain),
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'section_scores': section_scores
        }

    except Exception as e:
        print(f"Scoring error: {str(e)}")
        return {
            'overall_score': 0.0,
            'domain': 'GENERAL',
            'domain_label': 'General',
            'matched_skills': [],
            'missing_skills': [],
            'section_scores': {}
        }

def calculate_score(jd_text, resume_text):
    """Backward-compatible helper returning a float score."""
    result = calculate_detailed_score(jd_text, resume_text)
    return result['overall_score']

