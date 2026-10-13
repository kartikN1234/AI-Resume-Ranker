import pytest
from utils.preprocessor import preprocess_text
from utils.scorer import expand_jd, detect_domain, calculate_detailed_score
from utils.extractor import extract_text_from_txt

def test_token_preservation():
    text = "Proficient in C++, Node.js, and CI/CD pipelines with .NET."
    processed = preprocess_text(text)
    # Technical mappings should be preserved
    assert "cplusplus" in processed
    assert "nodejs" in processed
    assert "cicd" in processed
    assert "dotnet" in processed

def test_domain_detection():
    ml_jd = "Looking for a Machine Learning Engineer experienced in PyTorch and LLMs."
    devops_jd = "Need a DevOps Engineer proficient in Kubernetes, Terraform, and Docker."
    web_jd = "Seeking a Frontend Developer with strong React and Next.js skills."

    assert detect_domain(ml_jd) == "ML_AI"
    assert detect_domain(devops_jd) == "CLOUD_DEVOPS"
    assert detect_domain(web_jd) == "WEB_DEV"

def test_jd_expansion():
    jd = "Hiring a MERN stack developer."
    expanded = expand_jd(jd)
    assert "MongoDB" in expanded
    assert "React.js" in expanded
    assert "Node.js" in expanded

def test_calculate_detailed_score():
    jd = "Looking for Python, React, and Docker developer with AWS knowledge."
    resume = """
    SKILLS
    Python, React, Docker, Git, REST API
    
    EXPERIENCE
    Senior Software Engineer: Developed cloud native microservices in Python and React.
    """
    result = calculate_detailed_score(jd, resume)
    
    assert "overall_score" in result
    assert 0 <= result["overall_score"] <= 100
    assert "domain" in result
    assert "matched_skills" in result
    assert "missing_skills" in result
    assert "Docker" in result["matched_skills"]
    assert "Aws" in result["missing_skills"]

def test_extract_text_from_txt():
    content = b"Candidate Name: John Doe\nSkills: Python, SQL"
    extracted = extract_text_from_txt(content)
    assert "John Doe" in extracted
    assert "Python" in extracted

def test_generate_interview_guide():
    from utils.questions import generate_interview_guide
    guide = generate_interview_guide("Jane_Doe.pdf", "CLOUD_DEVOPS", ["Docker", "Kubernetes"], ["Aws"])
    assert guide["candidate"] == "Jane_Doe.pdf"
    assert len(guide["strengths_questions"]) >= 1
    assert len(guide["gap_questions"]) >= 1
    assert any("Docker" in q for q in guide["strengths_questions"])
    assert any("Aws" in q for q in guide["gap_questions"])
