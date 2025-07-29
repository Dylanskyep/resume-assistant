from openai_helper import generate_bullets, critique_resume, extract_full_resume_image
import streamlit as st
import os
import base64

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if "page" not in st.session_state:
    st.session_state.page = "welcome"

# ========== Welcome Page ==========
if st.session_state.page == "welcome":
    st.markdown("""
        <style>
        html, body, .stApp {
            margin: 0;
            padding: 0;
            height: 100%;
            overflow: hidden;
            background-color: transparent !important;
        }
        </style>
        <iframe class="lottie-bg-container" srcdoc='<!DOCTYPE html><html><body></body></html>' width="100%" height="100%" frameborder="0"></iframe>
    """, unsafe_allow_html=True)

    st.markdown("""<h1 class="welcome-title">Welcome to the Resume Assistant</h1>""", unsafe_allow_html=True)
    st.markdown("""<p class="welcome-desc">This app helps you generate impactful bullet points and get tailored critiques for your resume!</p>""", unsafe_allow_html=True)
    if st.button("→"):
        st.session_state.page = "main"
        st.rerun()

# ========== Main Page ==========
elif st.session_state.page == "main":
    st.markdown("""
        <style>
        .animated-title {
            font-size: 40px;
            font-weight: 800;
            text-align: center;
            margin-top: 2rem;
            animation: fadeInDown 1.6s ease-out forwards;
        }
        @keyframes fadeInDown {
            0% { opacity: 0; transform: translateY(-20px); }
            100% { opacity: 1; transform: translateY(0); }
        }

        .resume-container {
            display: flex;
            flex-direction: row;
            align-items: flex-start;
            justify-content: space-between;
            gap: 4rem;
            padding-top: 2rem;
        }

        .sticky-resume {
            position: sticky;
            top: 100px;
            flex: 1;
            max-width: 45%;
            height: 85vh;
            overflow: auto;
        }

        .sticky-resume img {
            width: 100%;
            height: auto;
            border-radius: 8px;
            border: 1px solid #ccc;
        }

        .critique-column {
            flex: 1;
            max-width: 50%;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="animated-title">Create and Review Resumes using AI</h1>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Generate Bullet Points", "Critique Resume"])

    # ---------- Bullet Points Tab ----------
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
                st.warning("Please enter both experience details and job title.")

    # ---------- Critique Resume Tab ----------
    with tab2:
        st.header("Generate Resume Critiques")
        pdf_file = st.file_uploader("Upload your resume as a PDF file", type=["pdf"])
        job_focus = st.text_input("Enter the job focus (optional but helpful):")

        if pdf_file is not None:
            if st.button("Critique Resume"):
                with st.spinner("Generating resume critiques..."):
                    critiques = critique_resume(pdf_file, job_focus)
                    image_path = extract_full_resume_image(pdf_file)

                    st.subheader("Results")

                    if image_path:
                        with open(image_path, "rb") as f:
                            image_bytes = f.read()
                            encoded_image = base64.b64encode(image_bytes).decode()

                        st.markdown('<div class="resume-container">', unsafe_allow_html=True)

                        # LEFT: Sticky image
                        st.markdown(f"""
                            <div class="sticky-resume">
                                <img src="data:image/png;base64,{encoded_image}" alt="Resume" />
                            </div>
                        """, unsafe_allow_html=True)

                        # RIGHT: Critique content
                        st.markdown('<div class="critique-column">', unsafe_allow_html=True)
                        for section_title, _, critique in critiques:
                            st.markdown(f"### {section_title}")
                            st.markdown(critique, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.warning("Could not generate resume image.")
