"""
Module for generating candidate-specific interview screening questions based on
verified skills, detected skill gaps, and role domain.
"""

DOMAIN_QUESTIONS = {
    "ML_AI": [
        "How do you handle dataset class imbalance and data drift when training production models?",
        "Can you describe an end-to-end LLM or ML pipeline you built, and how you evaluated model latency vs. accuracy?",
        "When fine-tuning or deploying transformers, what quantization or optimization techniques do you apply?"
    ],
    "CLOUD_DEVOPS": [
        "Describe how you structure zero-downtime rolling deployments and automated rollbacks using Kubernetes and CI/CD.",
        "How do you enforce Infrastructure-as-Code best practices and state management using Terraform?",
        "Can you walk through a high-severity production outage you investigated, and how your monitoring (Prometheus/Grafana) helped resolve it?"
    ],
    "WEB_DEV": [
        "How do you optimize Core Web Vitals and component re-rendering in high-traffic React or Next.js applications?",
        "What patterns do you implement for robust global state management and asynchronous data caching?",
        "How do you approach cross-browser compatibility and responsive accessibility (a11y) standards?"
    ],
    "FULLSTACK": [
        "How do you architect database indexing and schema migrations when transitioning from monolith to microservices?",
        "Describe your approach to designing resilient, versioned REST/GraphQL APIs with authentication (JWT/OAuth).",
        "How do you balance server-side rendering (SSR) vs. client-side rendering (CSR) for scalability and performance?"
    ],
    "DATA_ENGINEER": [
        "How do you design scalable ETL/ELT pipelines in Spark or Kafka to handle out-of-order and duplicate streaming data?",
        "What strategies do you use for data partitioning and query optimization in data warehouses like Snowflake or BigQuery?",
        "How do you ensure data lineage, schema evolution, and automated data quality checks across pipeline DAGs?"
    ],
    "DATA_ANALYST": [
        "Can you walk through a time your data analysis or BI dashboard directly shaped a major business or product decision?",
        "What techniques do you use to detect statistical anomalies and validate dirty data before stakeholder presentation?",
        "How do you structure complex SQL queries (CTEs, Window Functions) for optimal execution performance?"
    ],
    "SOFTWARE_DEV": [
        "How do you apply SOLID principles and design patterns to keep large codebases maintainable and testable?",
        "Describe your strategy for automated unit and integration testing, and what code coverage benchmarks you target.",
        "How do you handle concurrency, race conditions, and thread safety in backend systems?"
    ]
}

def generate_interview_guide(candidate_name, domain, matched_skills, missing_skills):
    """
    Generates a structured interview screening script tailored to the candidate's profile.
    Returns:
        dict: {
            'strengths_questions': list[str],
            'gap_questions': list[str],
            'domain_questions': list[str]
        }
    """
    strengths_questions = []
    gap_questions = []

    # Generate questions based on matched skills
    for skill in matched_skills[:3]:
        strengths_questions.append(
            f"**Deep Dive on {skill}:** Can you describe a complex, production-grade project where you implemented {skill}? What architectural trade-offs or technical hurdles did you encounter?"
        )
    if not strengths_questions:
        strengths_questions.append(
            "Can you walk us through the most technically challenging project featured on your resume and your specific role in it?"
        )

    # Generate questions based on missing skills / gaps
    for skill in missing_skills[:2]:
        gap_questions.append(
            f"**Addressing {skill} Requirement:** This position heavily utilizes **{skill}**, which was not prominently featured in your profile. Have you worked with similar technologies, and how would you approach ramping up on {skill} in your first 30 days?"
        )
    if not gap_questions:
        gap_questions.append(
            "Your profile matches all detected core requirements. How do you stay current with emerging tools and technologies in your stack?"
        )

    # Domain specific questions
    domain_q = DOMAIN_QUESTIONS.get(domain, DOMAIN_QUESTIONS["SOFTWARE_DEV"])

    return {
        "candidate": candidate_name,
        "strengths_questions": strengths_questions,
        "gap_questions": gap_questions,
        "domain_questions": domain_q
    }
