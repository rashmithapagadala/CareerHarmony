# career_harmony_app.py

import streamlit as st
import re
import pandas as pd
import docx2txt
import pdfplumber
from openai import OpenAI

# --- Load OpenAI API key ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="CareerHarmony – AI Career Coach", layout="wide")

st.title("🎯 CareerHarmony – AI Career Coach")

# --- Tabs for two main features ---
tabs = st.tabs(["Resume Analysis", "Interview & Coding Prep", "Chatbot"])

# ---------------------------
# Tab 1: Resume Analysis
# ---------------------------
with tabs[0]:
    st.header("📄 Resume vs Job Description Analyzer")

    resume_file = st.file_uploader("Upload your Resume (PDF or DOCX)", type=["pdf", "docx"])
    jd_file = st.file_uploader("Upload the Job Description (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

    def extract_text(file):
        if file.name.endswith(".pdf"):
            text = ""
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            return text
        elif file.name.endswith(".docx"):
            return docx2txt.process(file)
        elif file.name.endswith(".txt"):
            return file.read().decode("utf-8")
        return ""

    def extract_skills(text):
        words = re.findall(r'\b[A-Za-z\+\#]+\b', text)
        common_skills = ['Python', 'SQL', 'Tableau', 'Machine Learning', 'Excel', 
                         'Communication', 'Power BI', 'R', 'Data Analysis', 'Statistics']
        found_skills = [w for w in words if w in common_skills]
        return list(set(found_skills))

    if resume_file and jd_file:
        resume_text = extract_text(resume_file)
        jd_text = extract_text(jd_file)

        resume_skills = extract_skills(resume_text)
        jd_skills = extract_skills(jd_text)

        matched_skills = set(resume_skills).intersection(set(jd_skills))
        missing_skills = set(jd_skills) - set(resume_skills)
        match_score = round(len(matched_skills)/len(jd_skills)*100, 2) if jd_skills else 0

        st.write(f"📊 **Resume Match Score:** {match_score} %")
        st.write(f"✅ Matched Skills: {matched_skills}")
        st.write(f"⚡ Missing Skills to Add: {missing_skills}")

        st.write("💡 **Suggested Resume Additions:**")
        for skill in missing_skills:
            if skill == "Statistics":
                st.write("- Applied statistical methods (hypothesis testing, regression, probability) for analyzing large datasets.")
            else:
                st.write(f"- Highlight experience/projects using {skill}")

# ---------------------------
# Tab 2: Interview & Coding Prep
# ---------------------------
with tabs[1]:
    st.header("🛠 Interview / Coding Assessment Prep")

    prep_resume_file = st.file_uploader("Upload Resume for Prep (PDF/DOCX)", key="prep_resume")
    prep_jd_text = st.text_area("Paste the Job Description here for prep", height=150)

    opportunity_type = st.radio("Opportunity Type", ["AI Interview", "Human Interview", "Coding Assessment"])

    if prep_resume_file and prep_jd_text:
        prep_resume_text = extract_text(prep_resume_file)
        prep_jd_skills = extract_skills(prep_jd_text)
        prep_resume_skills = extract_skills(prep_resume_text)
        prep_missing_skills = list(set(prep_jd_skills) - set(prep_resume_skills))

        def get_ai_recommendations(missing_skills, opp_type):
            if not missing_skills:
                return "✅ Your resume covers all key skills for this opportunity!"
            prompt = f"""
            You are a career assistant. The candidate is preparing for a {opp_type}.
            Missing skills: {missing_skills}
            Provide a clear preparation strategy and recommend top online courses or resources.
            """
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=350
            )
            return response.choices[0].message["content"]

        st.subheader("Preparation Strategy & Resources")
        try:
            prep_result = get_ai_recommendations(prep_missing_skills, opportunity_type)
            st.write(prep_result)
        except Exception as e:
            st.error(f"Error fetching AI recommendations: {e}")

# ---------------------------
# Tab 3: Chatbot
# ---------------------------
with tabs[2]:
    st.header("💬 Career Chatbot")
    chat_input = st.text_area("Ask your career-related questions here:")
    if st.button("Send", key="chat"):
        if chat_input.strip():
            try:
                chat_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": chat_input}],
                    temperature=0.7,
                    max_tokens=350
                )
                st.write(chat_response.choices[0].message["content"])
            except Exception as e:
                st.error(f"Error in Chatbot: {e}")
        else:
            st.warning("Please type your question.")
