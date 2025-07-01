from openai_helper import generate_bullets, critique_resume
import streamlit as st
import os
import streamlit.components.v1 as components

# Environment key (if needed)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Set page config
st.set_page_config(layout="wide", page_title="Resume Assistant", page_icon="📝")

# Inject Lottie animation as background
components.html(
    """
    <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; overflow: hidden;">
        <script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
        <lottie-player
            src="https://lottie.host/2b7567f6-52b5-408e-8932-9b339f4b3201/F8zKtZW4Bi.json"
            background="transparent"
            speed="1"
            loop
            autoplay
            style="width: 100%; height: 100%;">
        </lottie-player>
    </div>
    """,
    height=0,
)

# Center content and control z-index
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

# Page state setup
if "page" not in st.session_state:
    st.session_state.page = "welcome"

# Welcome Page
if st.session_state.page == "welcome":
    st.title("Welcome to the Resume Assistant")
    st.markdown("Create and review resumes using AI-powered tools.")
    if st.button("Continue to Main Page"):
        st.session_state.page = "main"
        st.rerun()

# Main Page
elif st.session_state.page == "main":
    st.title("Create and Review Resumes using AI")

    tab1, tab2 = st.tabs(["Generate Bullet Points", "Critique Resume"])

    # Generate Bullet Points Section
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

    # Critique Resume Section
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
