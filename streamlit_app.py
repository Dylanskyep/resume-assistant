from openai_helper import generate_bullets, critique_resume
import streamlit as st
import os
from streamlit.components.v1 import html

# Set environment key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Page config
st.set_page_config(layout="wide", page_title="Resume Assistant", page_icon="📝")

st.markdown("""
    <div id="lottie-background" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; pointer-events: none; opacity: 0.5;"></div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.0/lottie.min.js"></script>
    <script>
        console.log("⏳ Injecting Lottie...");
        const container = document.getElementById('lottie-background');
        if (!container) {
            console.error("❌ Lottie container not found!");
        } else {
            console.log("✅ Found Lottie container");
            const animation = lottie.loadAnimation({
                container: container,
                renderer: 'svg',
                loop: true,
                autoplay: true,
                path: 'https://lottie.host/090ccb00-42b0-44c2-ad52-8a15c2eca2fa/leCYtLJZo5.json'
            });

            animation.addEventListener('DOMLoaded', function () {
                console.log("🎉 Lottie animation loaded!");
            });

            animation.addEventListener('error', function (e) {
                console.error("🚨 Lottie failed to load", e);
            });
        }
    </script>
""", unsafe_allow_html=True)


st.markdown("""
    <style>
    .block-container {
        max-width: 75%;
        margin: auto;
        padding-top: 4rem;
        padding-bottom: 2rem;
    }
    h1, p, .stButton, .stTextInput, .stTextArea, .stFileUploader {
        z-index: 1;
        position: relative;
    }
    </style>
""", unsafe_allow_html=True)

# --- Page State ---
if "page" not in st.session_state:
    st.session_state.page = "welcome"

# --- Welcome Page ---
if st.session_state.page == "welcome":
    st.title("Welcome to the Resume Assistant")
    st.markdown("Create and review resumes using AI-powered tools.")
    if st.button("Continue to Main Page"):
        st.session_state.page = "main"
        st.rerun()

# --- Main App Page ---
elif st.session_state.page == "main":
    st.title("Create and Review Resumes using AI")
    tab1, tab2 = st.tabs(["Generate Bullet Points", "Critique Resume"])

    # --- Bullet Points Tab ---
    with tab1:
        st.header("Generate Resume Experience Bullet Points")
        experience = st.text_area("Enter your experience details:", height=150)
        job_title = st.text_input("Enter the job title:")
        if st.button("Generate Bullet Points"):
            if experience and job_title:
                with st.spinner("Generating bullet points..."):
                    bullets = generate_bullets(experience, job_title)
                for line in bullets:
                    if line.strip().startswith(("-", "•", "*")):
                        st.write(line.strip())
                st.download_button("Download Bullet Points", "\n".join(bullets), file_name="bullets.txt")
            else:
                st.write("Please enter both experience details and job title to generate bullet points.")

    # --- Resume Critique Tab ---
    with tab2:
        st.header("Generate Resume Critiques")
        pdf_file = st.file_uploader("Upload your resume as a PDF file", type=["pdf"])
        job_focus = st.text_input("Enter the job focus (optional but helpful):")
        if pdf_file is not None:
            if st.button("Critique Resume"):
                with st.spinner("Generating resume critiques..."):
                    critique = critique_resume(pdf_file, job_focus)
                    if critique:
                        st.subheader("Results")
                        for line in critique:
                            if line.strip():
                                if line.strip().startswith(("-", "•", "*")):
                                    st.write(line.strip())
                                else:
                                    st.markdown(f"**{line.strip()}**")
                        st.download_button("Download Critiques", "\n".join(critique), file_name="critiques.txt")
                    else:
                        st.write("Please check the PDF file format or job focus to ensure they are valid.")
        else:
            st.write("Please upload a PDF file of your resume before clicking the button.")
