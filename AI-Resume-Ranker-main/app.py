import time
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from utils.extractor import extract_text
from utils.preprocessor import preprocess_text
from utils.scorer import calculate_detailed_score
from utils.questions import generate_interview_guide

ROLE_PRESETS = {
    "Select a Role Requisition...": "",
    "Full Stack Engineer (Python & React)": """Role: Senior Full Stack Engineer (Python & React)
Requirements:
- 4+ years building full-stack web applications with Python, React, TypeScript, and Node.js.
- Strong knowledge of REST APIs, PostgreSQL, and MongoDB.
- Experience with Cloud platforms (AWS or GCP), Docker, Kubernetes, and CI/CD pipelines.
- Solid background in Microservices architecture, Git, and automated testing.
- Bonus: Experience with Machine Learning pipelines, NLP, or LLM integrations.""",
    "Machine Learning & AI Engineer": """Role: Machine Learning & Generative AI Engineer
Requirements:
- 3+ years experience with PyTorch, TensorFlow, Scikit-Learn, and Python.
- Proven expertise in NLP, LLM fine-tuning, Transformers (HuggingFace), and LangChain.
- Experience building RAG pipelines, Vector Databases (Pinecone/Milvus/Qdrant), and model quantization.
- Deployed scalable ML models into production with Docker and FastAPI.""",
    "Cloud & DevOps Architect": """Role: Cloud & DevOps Infrastructure Engineer
Requirements:
- 4+ years designing CI/CD pipelines (GitHub Actions, Jenkins) and automated deployments.
- Extensive expertise with Kubernetes, Docker, Helm, and Terraform (Infrastructure as Code).
- Production experience with AWS services (EKS, EC2, S3, RDS, CloudWatch) or Azure.
- Strong Linux systems administration, bash scripting, and Prometheus/Grafana monitoring.""",
    "Data Engineer & Pipeline Specialist": """Role: Senior Data Engineer
Requirements:
- 3+ years architecting data ingestion and ETL/ELT pipelines with Apache Spark and Kafka.
- Strong experience with workflow orchestration using Apache Airflow or Databricks.
- Advanced SQL and hands-on experience with modern cloud data warehouses (Snowflake, BigQuery).
- Experience with dbt, data lakehouse architectures, and schema management.""",
    "Data Analyst & BI Specialist": """Role: Senior Data Analyst & BI Consultant
Requirements:
- Proficient in SQL, Python (Pandas, NumPy), and advanced statistical analysis.
- Proven track record building executive dashboards in Power BI and Tableau.
- Strong expertise in data storytelling, KPI modeling, and business intelligence reporting.
- Experience working with cross-functional product and marketing teams."""
}

def get_tier_badge(score):
    if score >= 80:
        return "🟢 High Match"
    elif score >= 65:
        return "🟡 Strong Fit"
    elif score >= 50:
        return "🟠 Moderate Fit"
    else:
        return "🔴 Low Fit"

def get_tier_color(score):
    if score >= 80:
        return "#10b981"
    elif score >= 65:
        return "#f59e0b"
    elif score >= 50:
        return "#f97316"
    else:
        return "#ef4444"

def main():
    st.set_page_config(
        page_title="AI Resume Ranker",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    if "shortlisted_candidates" not in st.session_state:
        st.session_state["shortlisted_candidates"] = set()
    if "candidate_notes" not in st.session_state:
        st.session_state["candidate_notes"] = {}

    # Custom styling
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            
            html, body, [class*="css"] {
                font-family: 'Inter', sans-serif;
            }
            
            .stApp {
                background: radial-gradient(circle at 15% 15%, #181926 0%, #0f1016 100%);
                color: #e2e8f0;
            }
            
            .main-header {
                text-align: center;
                padding: 1.5rem 0 1rem 0;
            }
            
            .main-title {
                font-size: 2.6rem !important;
                font-weight: 800 !important;
                background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 0.25rem !important;
            }
            
            .sub-title {
                color: #94a3b8;
                font-size: 1.1rem;
                margin-bottom: 1.5rem;
            }
            
            .metric-card {
                background: rgba(30, 41, 59, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                padding: 1rem 1.25rem;
                backdrop-filter: blur(10px);
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
            }
            
            .metric-title {
                font-size: 0.85rem;
                color: #94a3b8;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                font-weight: 600;
            }
            
            .metric-value {
                font-size: 1.8rem;
                font-weight: 700;
                color: #f8fafc;
                margin-top: 0.25rem;
            }
            
            .skill-pill-matched {
                display: inline-block;
                background: rgba(16, 185, 129, 0.15);
                color: #34d399;
                border: 1px solid rgba(16, 185, 129, 0.3);
                border-radius: 9999px;
                padding: 0.2rem 0.65rem;
                font-size: 0.78rem;
                font-weight: 500;
                margin: 0.15rem;
            }
            
            .skill-pill-missing {
                display: inline-block;
                background: rgba(244, 63, 94, 0.12);
                color: #fb7185;
                border: 1px solid rgba(244, 63, 94, 0.25);
                border-radius: 9999px;
                padding: 0.2rem 0.65rem;
                font-size: 0.78rem;
                font-weight: 500;
                margin: 0.15rem;
            }

            .skill-pill-neutral {
                display: inline-block;
                background: rgba(148, 163, 184, 0.15);
                color: #94a3b8;
                border: 1px solid rgba(148, 163, 184, 0.25);
                border-radius: 9999px;
                padding: 0.2rem 0.65rem;
                font-size: 0.78rem;
                font-weight: 500;
                margin: 0.15rem;
            }
            
            .stTextArea textarea {
                background-color: rgba(15, 23, 42, 0.7) !important;
                border: 1px solid rgba(148, 163, 184, 0.2) !important;
                border-radius: 10px !important;
                color: #f1f5f9 !important;
                font-size: 0.95rem !important;
            }
            
            .stTextArea textarea:focus {
                border-color: #38bdf8 !important;
                box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2) !important;
            }
            
            .stButton>button {
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
                color: white !important;
                font-weight: 600 !important;
                border-radius: 10px !important;
                padding: 0.65rem 1.5rem !important;
                border: none !important;
                transition: all 0.25s ease !important;
            }
            
            .stButton>button:hover {
                transform: translateY(-1px) !important;
                box-shadow: 0 8px 20px rgba(99, 102, 241, 0.35) !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Sidebar controls
    with st.sidebar:
        st.markdown("### ⚙️ Screening Configuration")
        st.caption("Customize ATS scoring sensitivity & filtering")
        
        min_score_filter = st.slider(
            "Minimum Score Cutoff (%)",
            min_value=0,
            max_value=90,
            value=40,
            step=5,
            help="Hide candidates falling below this match percentage."
        )

        st.markdown("---")
        st.markdown("### 📋 Supported Formats")
        st.markdown("""
        - 📄 **PDF** (`.pdf`)
        - 📝 **Word DOCX** (`.docx`)
        - 📃 **Plain Text** (`.txt`)
        """)

        st.markdown("---")
        st.markdown("### 🧠 AI Engine Specs")
        st.markdown("""
        - **Model:** `all-MiniLM-L6-v2`
        - **NLP Preprocessing:** SpaCy `en_core_web_sm`
        - **Pipeline:** Dynamic Section Normalization + Domain Boosting
        """)

    # Main Header
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">AI Resume Ranker </h1>
            <div class="sub-title">Semantic NLP-driven resume shortlisting, skill gap analysis, and candidate matching</div>
        </div>
    """, unsafe_allow_html=True)

    # Two column inputs
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("#### 1️⃣ Job Description & Requisition")
        
        selected_preset = st.selectbox(
            "📋 Choose Job Role Preset:",
            options=list(ROLE_PRESETS.keys()),
            index=0,
            help="Select an industry-standard role to automatically populate requirements."
        )
        if selected_preset and ROLE_PRESETS[selected_preset]:
            st.session_state["jd_input"] = ROLE_PRESETS[selected_preset]

        jd_text = st.text_area(
            "Job Description",
            value=st.session_state.get("jd_input", ""),
            height=230,
            placeholder="Paste complete job description, requirements, and responsibilities here...",
            label_visibility="collapsed"
        )
        
        if st.button("🗑️ Clear Job Description", use_container_width=True):
            st.session_state["jd_input"] = ""
            st.rerun()

    with col2:
        st.markdown("#### 2️⃣ Upload Resumes")
        uploaded_files = st.file_uploader(
            "Upload Resume Files",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            help="Select one or multiple resumes (.pdf, .docx, or .txt)"
        )
        
        if uploaded_files:
            st.success(f"📂 **{len(uploaded_files)} candidate resume(s) uploaded and ready for analysis**")
        else:
            st.info("💡 Upload one or more resumes to begin ranking against the job description.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Rank Action
    rank_btn = st.button("🚀 Rank & Evaluate Candidates", use_container_width=True)

    if rank_btn:
        if not jd_text.strip():
            st.error("⚠️ Please provide a Job Description to evaluate candidates against.")
            return

        if not uploaded_files:
            st.error("⚠️ Please upload at least one candidate resume.")
            return

        with st.spinner("🤖 Evaluating candidate resumes through semantic embedding models..."):
            start_time = time.time()
            results = []

            progress_bar = st.progress(0)
            status_text = st.empty()

            for idx, file in enumerate(uploaded_files):
                status_text.text(f"Processing candidate ({idx+1}/{len(uploaded_files)}): {file.name}")
                text = extract_text(file)
                
                if text and len(text.strip()) > 30:
                    analysis = calculate_detailed_score(jd_text, text)
                    results.append({
                        "Filename": file.name,
                        "OverallScore": analysis["overall_score"],
                        "Tier": get_tier_badge(analysis["overall_score"]),
                        "TierColor": get_tier_color(analysis["overall_score"]),
                        "Domain": analysis["domain_label"],
                        "DomainKey": analysis["domain"],
                        "MatchedSkills": analysis["matched_skills"],
                        "MissingSkills": analysis["missing_skills"],
                        "SectionScores": analysis["section_scores"],
                        "ExtractedSnippet": text[:600] + ("..." if len(text) > 600 else "")
                    })
                else:
                    results.append({
                        "Filename": file.name,
                        "OverallScore": 0.0,
                        "Tier": "🔴 Unreadable / Empty",
                        "TierColor": "#ef4444",
                        "Domain": "N/A",
                        "DomainKey": "GENERAL",
                        "MatchedSkills": [],
                        "MissingSkills": [],
                        "SectionScores": {},
                        "ExtractedSnippet": "Could not extract readable text from document."
                    })
                progress_bar.progress((idx + 1) / len(uploaded_files))

            status_text.empty()
            progress_bar.empty()
            duration = time.time() - start_time

            if not results:
                st.warning("No candidate data could be extracted from the uploaded files.")
                return

            # Sort strictly by genuine objective score
            results.sort(key=lambda x: x["OverallScore"], reverse=True)
            for idx, r in enumerate(results):
                r["Rank"] = idx + 1

            st.session_state["ranking_results"] = results
            st.session_state["ranking_duration"] = duration

    # Render results if present in session state
    if "ranking_results" in st.session_state:
        results = st.session_state["ranking_results"]
        duration = st.session_state.get("ranking_duration", 0)

        # Apply cutoff filter
        filtered_results = [r for r in results if r["OverallScore"] >= min_score_filter]

        st.markdown("---")
        st.markdown("### 📊 Candidate Shortlist Summary")

        # Top Metric Cards
        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        with mcol1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Candidates Evaluated</div>
                    <div class="metric-value">{len(results)}</div>
                </div>
            """, unsafe_allow_html=True)

        with mcol2:
            top_score = results[0]["OverallScore"] if results else 0
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Top Match Score</div>
                    <div class="metric-value">{top_score}%</div>
                </div>
            """, unsafe_allow_html=True)

        with mcol3:
            avg_score = round(sum(r["OverallScore"] for r in results) / max(len(results), 1), 1)
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Average Match</div>
                    <div class="metric-value">{avg_score}%</div>
                </div>
            """, unsafe_allow_html=True)

        with mcol4:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Analysis Time</div>
                    <div class="metric-value">{duration:.2f}s</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Tabs for presentation
        num_shortlisted = len(st.session_state["shortlisted_candidates"])
        tab_board, tab_details, tab_shortlist, tab_charts, tab_compare, tab_export = st.tabs([
            "🏆 Leaderboard", 
            "🔍 Candidate Deep-Dive", 
            f"⭐ Shortlisted ({num_shortlisted})",
            "📊 Analytics & Charts", 
            "⚖️ Head-to-Head Compare", 
            "📥 Export Data"
        ])

        with tab_board:
            if not filtered_results:
                st.warning(f"No candidates scored above the current threshold of {min_score_filter}%. Adjust the cutoff in the sidebar.")
            else:
                table_data = []
                for r in filtered_results:
                    is_sl = r["Filename"] in st.session_state["shortlisted_candidates"]
                    table_data.append({
                        "Rank": f"#{r['Rank']}",
                        "Candidate File": r["Filename"],
                        "Fit Rating": r["Tier"],
                        "Match Score": f"{r['OverallScore']}%",
                        "Role Category": r["Domain"],
                        "Status": "⭐ Shortlisted" if is_sl else "—",
                        "Matched Skills Count": len(r["MatchedSkills"])
                    })
                df_display = pd.DataFrame(table_data)
                st.dataframe(df_display, use_container_width=True, hide_index=True)

                st.markdown("##### ⭐ Quick Shortlist Manager")
                all_filenames = [r["Filename"] for r in results]
                current_sl_list = [f for f in all_filenames if f in st.session_state["shortlisted_candidates"]]
                updated_sl = st.multiselect(
                    "Manage Shortlisted Candidates:",
                    options=all_filenames,
                    default=current_sl_list,
                    help="Instantly adds or removes candidates from your recruiter shortlist."
                )
                if set(updated_sl) != st.session_state["shortlisted_candidates"]:
                    st.session_state["shortlisted_candidates"] = set(updated_sl)
                    st.rerun()

        with tab_details:
            if not filtered_results:
                st.info("No candidates match current filter.")
            else:
                for c in filtered_results:
                    is_sl = c["Filename"] in st.session_state["shortlisted_candidates"]
                    badge_prefix = "⭐ [SHORTLISTED] " if is_sl else ""
                    with st.expander(f"{badge_prefix}#{c['Rank']} — {c['Filename']} ({c['OverallScore']}% • {c['Tier']})", expanded=(c["Rank"] == 1)):
                        # Recruiter Action & Notes Bar
                        action_col1, action_col2 = st.columns([1, 2], gap="small")
                        with action_col1:
                            if is_sl:
                                if st.button("✅ Shortlisted (Click to Remove)", key=f"sl_btn_{c['Filename']}", use_container_width=True):
                                    st.session_state["shortlisted_candidates"].remove(c["Filename"])
                                    st.rerun()
                            else:
                                if st.button("⭐ Shortlist Candidate", key=f"sl_btn_{c['Filename']}", use_container_width=True):
                                    st.session_state["shortlisted_candidates"].add(c["Filename"])
                                    st.rerun()
                        with action_col2:
                            current_note = st.session_state["candidate_notes"].get(c["Filename"], "")
                            note_val = st.text_input(
                                "Recruiter Note",
                                value=current_note,
                                key=f"note_input_{c['Filename']}",
                                placeholder="Add internal recruiter feedback, next interview steps...",
                                label_visibility="collapsed"
                            )
                            if note_val != current_note:
                                st.session_state["candidate_notes"][c["Filename"]] = note_val

                        st.markdown("<hr style='margin: 8px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.06);'>", unsafe_allow_html=True)
                        
                        dcol1, dcol2 = st.columns([1, 1], gap="medium")
                        
                        with dcol1:
                            st.markdown("##### 🎯 Match Overview")
                            st.progress(c["OverallScore"] / 100.0)
                            st.markdown(f"**Detected Role Domain:** `{c['Domain']}`")
                            
                            # Section breakdowns if available
                            if c["SectionScores"]:
                                st.markdown("##### 📑 Section Score Breakdown")
                                for sec, s_score in c["SectionScores"].items():
                                    st.write(f"• **{sec.title()}:** {s_score}%")

                            with st.expander("📄 Preview Extracted Resume Snippet"):
                                st.text(c["ExtractedSnippet"])

                        with dcol2:
                            st.markdown("##### ✅ Matched Required Skills")
                            if c["MatchedSkills"]:
                                pills_html = "".join([f"<span class='skill-pill-matched'>{s}</span>" for s in c["MatchedSkills"]])
                                st.markdown(pills_html, unsafe_allow_html=True)
                            else:
                                st.caption("No explicit hard-skill matches detected.")

                            st.markdown("##### ⚠️ Missing or Unspecified Skills")
                            if c["MissingSkills"]:
                                pills_missing_html = "".join([f"<span class='skill-pill-missing'>{s}</span>" for s in c["MissingSkills"]])
                                st.markdown(pills_missing_html, unsafe_allow_html=True)
                            else:
                                st.caption("Candidate covers all core domain keywords detected in the JD.")

                        # AI Interview Screening Guide
                        st.markdown("<hr style='margin: 12px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
                        with st.expander(f"🎯 AI Interview Screening Guide for {c['Filename']}", expanded=False):
                            guide = generate_interview_guide(
                                c["Filename"],
                                c.get("DomainKey", "SOFTWARE_DEV"),
                                c["MatchedSkills"],
                                c["MissingSkills"]
                            )
                            qcol1, qcol2 = st.columns(2)
                            with qcol1:
                                st.markdown("###### 🔍 Verified Strengths — Technical Probes")
                                for q in guide["strengths_questions"]:
                                    st.markdown(f"- {q}")
                                st.markdown("###### 🧠 Domain Architecture Scenarios")
                                for q in guide["domain_questions"]:
                                    st.markdown(f"- {q}")
                            with qcol2:
                                st.markdown("###### ⚠️ Skill Gap & Adaptability Probes")
                                for q in guide["gap_questions"]:
                                    st.markdown(f"- {q}")

        with tab_shortlist:
            shortlisted_files = st.session_state["shortlisted_candidates"]
            shortlisted_candidates = [r for r in results if r["Filename"] in shortlisted_files]
            
            if not shortlisted_candidates:
                st.info("⭐ **No candidates shortlisted yet.**\n\nClick the **'⭐ Shortlist Candidate'** button on any profile or select candidates in the Leaderboard to build your shortlist pipeline.")
            else:
                # Top metrics for shortlist
                s_col1, s_col2, s_col3 = st.columns(3)
                with s_col1:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-title">Shortlisted Candidates</div>
                            <div class="metric-value">{len(shortlisted_candidates)}</div>
                        </div>
                    """, unsafe_allow_html=True)
                with s_col2:
                    sl_avg = round(sum(c["OverallScore"] for c in shortlisted_candidates) / len(shortlisted_candidates), 1)
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-title">Shortlist Average Score</div>
                            <div class="metric-value">{sl_avg}%</div>
                        </div>
                    """, unsafe_allow_html=True)
                with s_col3:
                    top_sl = max(c["OverallScore"] for c in shortlisted_candidates)
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-title">Top Shortlisted Fit</div>
                            <div class="metric-value">{top_sl}%</div>
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("##### 📋 Hand-Picked Candidates Shortlist Dossier")

                for sc in shortlisted_candidates:
                    note = st.session_state["candidate_notes"].get(sc["Filename"], "")
                    with st.container():
                        st.markdown(f"""
                            <div class="candidate-card">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <h4 style="margin: 0; color: #f8fafc;">#{sc['Rank']} — {sc['Filename']}</h4>
                                    <span style="font-size: 1.1rem; font-weight: 700; color: {sc['TierColor']};">{sc['OverallScore']}% ({sc['Tier']})</span>
                                </div>
                                <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 4px;">Role Category: {sc['Domain']}</div>
                                {"<div style='background: rgba(56, 189, 248, 0.1); border-left: 3px solid #38bdf8; padding: 8px 12px; margin-top: 10px; border-radius: 4px; font-size: 0.88rem; color: #bae6fd;'><strong>📝 Recruiter Note:</strong> " + note + "</div>" if note else ""}
                            </div>
                        """, unsafe_allow_html=True)

                # Export Shortlist
                st.markdown("##### 📥 Export Shortlisted Pipeline")
                sl_rows = []
                for sc in shortlisted_candidates:
                    sl_rows.append({
                        "Rank": sc["Rank"],
                        "Candidate File": sc["Filename"],
                        "Match Score": f"{sc['OverallScore']}%",
                        "Fit Rating": sc["Tier"],
                        "Role Category": sc["Domain"],
                        "Recruiter Internal Note": st.session_state["candidate_notes"].get(sc["Filename"], ""),
                        "Matched Skills": ", ".join(sc["MatchedSkills"]),
                        "Missing Skills": ", ".join(sc["MissingSkills"]),
                    })
                sl_df = pd.DataFrame(sl_rows)
                st.download_button(
                    label="📥 Download Shortlisted Candidates Only (.csv)",
                    data=sl_df.to_csv(index=False).encode('utf-8'),
                    file_name="shortlisted_candidates_dossier.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        with tab_charts:
            st.markdown("##### 📈 Candidate Match Score Distribution")
            chart_df = pd.DataFrame(filtered_results if filtered_results else results)
            
            if not chart_df.empty:
                # Plotly Horizontal Bar Chart
                fig = px.bar(
                    chart_df,
                    x="OverallScore",
                    y="Filename",
                    orientation="h",
                    color="OverallScore",
                    color_continuous_scale=["#ef4444", "#f59e0b", "#10b981"],
                    labels={"OverallScore": "Match Score (%)", "Filename": "Candidate"},
                    title="Candidate Match Rankings",
                    text="OverallScore"
                )
                fig.update_layout(
                    template="plotly_dark",
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(range=[0, 100]),
                    yaxis=dict(autorange="reversed"),
                    height=max(360, len(chart_df) * 45)
                )
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                st.plotly_chart(fig, use_container_width=True)

                # Section Score Comparison Chart across candidates
                st.markdown("##### 🧩 Section-by-Section Comparison")
                section_rows = []
                for r in (filtered_results[:8] if filtered_results else results[:8]):
                    for sec, sc in r["SectionScores"].items():
                        section_rows.append({
                            "Candidate": r["Filename"][:18] + "...",
                            "Section": sec.title(),
                            "Score": sc
                        })
                
                if section_rows:
                    sec_df = pd.DataFrame(section_rows)
                    fig_sec = px.bar(
                        sec_df,
                        x="Candidate",
                        y="Score",
                        color="Section",
                        barmode="group",
                        title="Section Score Breakdown (Top Candidates)",
                        labels={"Score": "Score (%)"},
                        color_discrete_sequence=["#38bdf8", "#818cf8", "#c084fc", "#f43f5e"]
                    )
                    fig_sec.update_layout(
                        template="plotly_dark",
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        yaxis=dict(range=[0, 100])
                    )
                    st.plotly_chart(fig_sec, use_container_width=True)

        with tab_compare:
            st.markdown("##### ⚖️ Head-to-Head Candidate Comparison")
            if len(results) < 2:
                st.info("Upload at least 2 candidates to enable head-to-head comparison.")
            else:
                candidate_names = [r["Filename"] for r in results]
                cmp_col1, cmp_col2 = st.columns(2)
                with cmp_col1:
                    cand_a_name = st.selectbox("Select Candidate A", candidate_names, index=0)
                with cmp_col2:
                    cand_b_name = st.selectbox("Select Candidate B", candidate_names, index=min(1, len(candidate_names) - 1))

                cand_a = next(r for r in results if r["Filename"] == cand_a_name)
                cand_b = next(r for r in results if r["Filename"] == cand_b_name)

                # Comparison Cards
                score_a_col, vs_col, score_b_col = st.columns([4, 1, 4])
                with score_a_col:
                    st.markdown(f"""
                        <div class="metric-card" style="text-align: center;">
                            <div class="metric-title">{cand_a['Filename']}</div>
                            <div class="metric-value" style="color: {cand_a['TierColor']};">{cand_a['OverallScore']}%</div>
                            <div style="margin-top: 0.5rem;">{cand_a['Tier']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with vs_col:
                    st.markdown("<h2 style='text-align: center; margin-top: 25px; color: #94a3b8;'>VS</h2>", unsafe_allow_html=True)

                with score_b_col:
                    st.markdown(f"""
                        <div class="metric-card" style="text-align: center;">
                            <div class="metric-title">{cand_b['Filename']}</div>
                            <div class="metric-value" style="color: {cand_b['TierColor']};">{cand_b['OverallScore']}%</div>
                            <div style="margin-top: 0.5rem;">{cand_b['Tier']}</div>
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Skill Overlap Analysis
                skills_a = set(cand_a["MatchedSkills"])
                skills_b = set(cand_b["MatchedSkills"])
                common_skills = skills_a.intersection(skills_b)
                unique_a = skills_a - skills_b
                unique_b = skills_b - skills_a

                ov_col1, ov_col2, ov_col3 = st.columns(3)
                with ov_col1:
                    st.markdown(f"**Unique to {cand_a['Filename'][:15]}**")
                    if unique_a:
                        pills = "".join([f"<span class='skill-pill-matched'>{s}</span>" for s in unique_a])
                        st.markdown(pills, unsafe_allow_html=True)
                    else:
                        st.caption("No unique skills")

                with ov_col2:
                    st.markdown("**🤝 Common Skills (Both)**")
                    if common_skills:
                        pills = "".join([f"<span class='skill-pill-neutral'>{s}</span>" for s in common_skills])
                        st.markdown(pills, unsafe_allow_html=True)
                    else:
                        st.caption("No overlapping skills")

                with ov_col3:
                    st.markdown(f"**Unique to {cand_b['Filename'][:15]}**")
                    if unique_b:
                        pills = "".join([f"<span class='skill-pill-matched'>{s}</span>" for s in unique_b])
                        st.markdown(pills, unsafe_allow_html=True)
                    else:
                        st.caption("No unique skills")

                st.markdown("<hr style='margin: 15px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
                with st.expander("🎯 Finalist Tie-Breaker Interview Questions", expanded=False):
                    g_a = generate_interview_guide(cand_a["Filename"], cand_a.get("DomainKey", "SOFTWARE_DEV"), cand_a["MatchedSkills"], cand_a["MissingSkills"])
                    g_b = generate_interview_guide(cand_b["Filename"], cand_b.get("DomainKey", "SOFTWARE_DEV"), cand_b["MatchedSkills"], cand_b["MissingSkills"])
                    
                    tcol1, tcol2 = st.columns(2)
                    with tcol1:
                        st.markdown(f"###### 🎙️ Targeted Questions for {cand_a['Filename']}")
                        if g_a["gap_questions"]:
                            st.markdown(f"**Skill Gap Probe:** {g_a['gap_questions'][0]}")
                        if g_a["strengths_questions"]:
                            st.markdown(f"**Strength Probe:** {g_a['strengths_questions'][0]}")
                    with tcol2:
                        st.markdown(f"###### 🎙️ Targeted Questions for {cand_b['Filename']}")
                        if g_b["gap_questions"]:
                            st.markdown(f"**Skill Gap Probe:** {g_b['gap_questions'][0]}")
                        if g_b["strengths_questions"]:
                            st.markdown(f"**Strength Probe:** {g_b['strengths_questions'][0]}")

        with tab_export:
            st.markdown("##### 📥 Export Data & Reports")
            
            exp_col1, exp_col2 = st.columns(2, gap="large")
            with exp_col1:
                st.markdown("###### 📊 Complete Evaluation Report (All Candidates)")
                st.caption("Exports ranking, match score, role domain, and skill gaps for every processed resume.")
                csv_rows = []
                for r in results:
                    is_sl = r["Filename"] in st.session_state["shortlisted_candidates"]
                    csv_rows.append({
                        "Rank": r["Rank"],
                        "Candidate File": r["Filename"],
                        "Match Score": f"{r['OverallScore']}%",
                        "Fit Rating": r["Tier"],
                        "Role Category": r["Domain"],
                        "Status": "Shortlisted" if is_sl else "Not Shortlisted",
                        "Recruiter Note": st.session_state["candidate_notes"].get(r["Filename"], ""),
                        "Matched Skills": ", ".join(r["MatchedSkills"]),
                        "Missing Skills": ", ".join(r["MissingSkills"]),
                    })
                export_df = pd.DataFrame(csv_rows)
                st.download_button(
                    label="📥 Download Complete Report (.csv)",
                    data=export_df.to_csv(index=False).encode('utf-8'),
                    file_name="complete_resume_rankings_report.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            with exp_col2:
                st.markdown("###### ⭐ Recruiter Shortlist Dossier Only")
                st.caption("Exports only the candidates explicitly shortlisted by the recruiter, including notes.")
                sl_candidates = [r for r in results if r["Filename"] in st.session_state["shortlisted_candidates"]]
                if sl_candidates:
                    sl_rows = []
                    for r in sl_candidates:
                        sl_rows.append({
                            "Rank": r["Rank"],
                            "Candidate File": r["Filename"],
                            "Match Score": f"{r['OverallScore']}%",
                            "Fit Rating": r["Tier"],
                            "Role Category": r["Domain"],
                            "Recruiter Note": st.session_state["candidate_notes"].get(r["Filename"], ""),
                            "Matched Skills": ", ".join(r["MatchedSkills"]),
                            "Missing Skills": ", ".join(r["MissingSkills"]),
                        })
                    sl_export_df = pd.DataFrame(sl_rows)
                    st.download_button(
                        label=f"⭐ Download Shortlist Only ({len(sl_candidates)} Candidates) (.csv)",
                        data=sl_export_df.to_csv(index=False).encode('utf-8'),
                        file_name="recruiter_shortlist_dossier.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.info("No candidates shortlisted yet. Shortlist candidates from the Leaderboard or Deep-Dive view to enable this download.")

    # Footer
    st.markdown("""
        <hr style="border:0; border-top: 1px solid rgba(148, 163, 184, 0.15); margin-top: 3rem;">
        <div style="text-align: center; color: #94a3b8; font-size: 0.9rem; padding: 1rem 0;">
            Developed by <strong>Kartik Nalawade</strong> | 
            <a href='https://www.linkedin.com/in/kartik-nalawade-3a663625a/' target='_blank' style='color:#38bdf8;'>LinkedIn</a> | 
            <a href='https://github.com/kartikN1234' target='_blank' style='color:#38bdf8;'>GitHub</a>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
