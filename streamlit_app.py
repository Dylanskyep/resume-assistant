from openai_helper import generate_bullets, critique_resume, extract_full_resume_image
import streamlit as st
import os
import base64

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Disable scrolling on welcome page only
if "page" not in st.session_state:
    st.session_state.page = "welcome"

# Shared styles
st.markdown("""
    <style>
    .block-container {
        max-width: 90%;
        margin: auto;
        padding-top: 1rem !important;
    }
    input, textarea {
        font-size: 18px !important;
    }
    .welcome-title {
        font-size: 100px;
        font-weight: bold;
        text-align: center;
        animation: fadeIn 1.3s ease-out forwards;
    }
    .welcome-desc {
        font-size: 35px;
        text-align: center;
        color: #888;
        animation: fadeIn 1.6s ease-out forwards;
    }
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(-20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    </style>
""", unsafe_allow_html=True)

# Welcome Page
if st.session_state.page == "welcome":
    st.markdown('<h1 class="welcome-title">Welcome to the Resume Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="welcome-desc">Use AI to generate bullet points and critique your resume layout/content.</p>', unsafe_allow_html=True)
    if st.button("→"):
        st.session_state.page = "main"
        st.rerun()

# Main Page
elif st.session_state.page == "main":
    st.title("Create and Review Resumes using AI")
    tab1, tab2 = st.tabs(["Generate Bullet Points", "Critique Resume"])

    with tab1:
        st.header("Generate Resume Experience Bullet Points")
        experience = st.text_area("Enter your experience details:", height=150)
        job_title = st.text_input("Enter the job title:")
        if st.button("Generate Bullet Points"):
            if experience and job_title:
                with st.spinner("Generating..."):
                    bullets = generate_bullets(experience, job_title)
                for b in bullets:
                    st.markdown(f"- {b}")
                st.download_button("Download", "\n".join(bullets), "bullets.txt")

    with tab2:
        st.header("Critique Resume")
        pdf_file = st.file_uploader("Upload PDF Resume", type=["pdf"])
        job_focus = st.text_input("Enter the job focus (optional):")

        if pdf_file and st.button("Critique Resume"):
            with st.spinner("Generating critique..."):
                critiques = critique_resume(pdf_file, job_focus)
                image_path = extract_full_resume_image(pdf_file)

            if not critiques or not image_path:
                st.warning("Could not generate results. Check that the resume was parsed correctly.")
            else:
                with open(image_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode()

                # Sticky layout styling
                st.markdown("""
                    <style>
                    .container {
                        display: flex;
                        align-items: flex-start;
                        gap: 2rem;
                        margin-top: 2rem;
                    }
                    .left-pane {
                        position: sticky;
                        top: 100px;
                        flex: 1;
                        max-width: 45%;
                        height: 85vh;
                        overflow-y: auto;
                        border: 1px solid #ccc;
                        border-radius: 8px;
                        background-color: #fff;
                    }
                    .left-pane img {
                        width: 100%;
                        height: auto;
                        display: block;
                    }
                    .right-pane {
                        flex: 1;
                        max-width: 55%;
                    }
                    </style>
                """, unsafe_allow_html=True)

                st.markdown('<div class="container">', unsafe_allow_html=True)

                # Resume Image Column
                st.markdown(f'''
                    <div class="left-pane">
                        <img src="data:image/png;base64,{encoded}" alt="Resume Image">
                    </div>
                ''', unsafe_allow_html=True)

                # Critiques Column
                st.markdown('<div class="right-pane">', unsafe_allow_html=True)
                for section_title, _, section_critique in critiques:
                    st.markdown(f"### {section_title}")
                    st.markdown(section_critique, unsafe_allow_html=True)
                st.markdown('</div></div>', unsafe_allow_html=True)
