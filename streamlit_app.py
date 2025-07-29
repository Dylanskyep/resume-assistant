from openai_helper import generate_bullets, critique_resume, extract_section_image_from_pdf
import streamlit as st
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if "page" not in st.session_state:
    st.session_state.page = "welcome"

if st.session_state.page == "welcome":
    st.markdown("""
        <style>
        html, body, .stApp, .main, .block-container {
            margin: 0;
            padding: 0;
            height: 100%;
            overflow: hidden;
            background-color: transparent !important;
        }
        .lottie-bg-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: 0;
            opacity: 0.5;
            pointer-events: none;
            border: none;
        }
        </style>

        <iframe class="lottie-bg-container" srcdoc='
            <!DOCTYPE html>
            <html><head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.0/lottie.min.js"></script>
            <style>
                html, body { margin: 0; padding: 0; height: 100%; width: 100%; background: transparent; overflow: hidden; }
                #lottie { width: 100vw; height: 100vh; transform: scale(1.5); transform-origin: center; }
            </style>
            </head>
            <body><div id="lottie"></div>
            <script>
                lottie.loadAnimation({ container: document.getElementById("lottie"), renderer: "svg", loop: true, autoplay: true,
                    path: "https://lottie.host/090ccb00-42b0-44c2-ad52-8a15c2eca2fa/leCYtLJZo5.json" });
            </script>
            </body></html>' width="100%" height="100%" frameborder="0"></iframe>
    """, unsafe_allow_html=True)

st.markdown("""
    <style>
    .block-container {
        max-width: 75%;
        margin: auto;
        padding-top: 1rem;
        padding-bottom: 5rem;
    }
    h1, p, .stButton, .stTextInput, .stTextArea, .stFileUploader {
        text-align: center;
    }
    input, textarea { font-size: 18px !important; }
    .welcome-title {
        font-size: 150px; font-weight: bold; text-align: center;
        margin-top: 2rem; margin-bottom: 3rem;
        animation: fadeIn 1.3s ease-out forwards;
    }
    .welcome-desc {
        font-size: 35px; color: #A9A9A9; text-align: center;
        margin-top: 1rem; margin-bottom: 2rem;
        animation: fadeIn 1.6s ease-out forwards;
    }
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(-20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    </style>
""", unsafe_allow_html=True)

if st.session_state.page == "welcome":
    st.markdown("""<h1 class="welcome-title">Welcome to the Resume Assistant</h1>""", unsafe_allow_html=True)
    st.markdown("""<p class="welcome-desc">This app helps you generate impactful bullet points and critiques for resumes.</p>""", unsafe_allow_html=True)
    if st.button("→"):
        st.session_state.page = "main"
        st.rerun()

elif st.session_state.page == "main":
    st.markdown("""
        <style>
        .animated-title {
            font-size: 40px; font-weight: 800;
            text-align: center; margin-top: 2rem;
            animation: fadeInDown 1.6s ease-out forwards;
        }
        @keyframes fadeInDown {
            0% { opacity: 0; transform: translateY(-20px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        </style>
    """, unsafe_allow_html=True)
    st.markdown('<h1 class="animated-title">Create and Review Resumes using AI</h1>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Generate Bullet Points", "Critique Resume"])

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

    with tab2:
        st.header("Generate Resume Critiques")
        pdf_file = st.file_uploader("Upload your resume as a PDF file", type=["pdf"])
        job_focus = st.text_input("Enter the job focus (optional):")
        if pdf_file and st.button("Critique Resume"):
            with st.spinner("Generating resume critiques..."):
                sections = critique_resume(pdf_file, job_focus)
                for section_title, content, critique in sections:
                    st.markdown(f"## {section_title}")
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        img_path = extract_section_image_from_pdf(pdf_file, section_title)
                        if img_path:
                            st.image(img_path, caption=section_title, use_container_width=True)
                        else:
                            st.warning("Section image not found.")
                    with col2:
                        st.markdown(critique, unsafe_allow_html=True)
