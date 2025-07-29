from openai_helper import generate_bullets, critique_resume, extract_full_resume_image
import streamlit as st
import os
import base64

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# only disable scrolling on welcome page
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
            <html>
            <head>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.0/lottie.min.js"></script>
                <style>
                    html, body {
                        margin: 0;
                        padding: 0;
                        height: 100%;
                        width: 100%;
                        background: transparent;
                        overflow: hidden;
                    }
                    #lottie {
                        width: 100vw;
                        height: 100vh;
                        transform: scale(1.5); 
                        transform-origin: center;
                    }
                </style>
            </head>
            <body>
                <div id="lottie"></div>
                <script>
                    lottie.loadAnimation({
                        container: document.getElementById("lottie"),
                        renderer: "svg",
                        loop: true,
                        autoplay: true,
                        path: "https://lottie.host/090ccb00-42b0-44c2-ad52-8a15c2eca2fa/leCYtLJZo5.json"
                    });
                </script>
            </body>
            </html>
        ' width="100%" height="100%" frameborder="0"></iframe>
    """, unsafe_allow_html=True)

# Common styling
st.markdown("""
    <style>
    .block-container {
        max-width: 75%;
        margin: auto;
        padding-top: 1rem !important;
        padding-bottom: 5rem;
    }
    h1, p, .stButton, .stTextInput, .stTextArea, .stFileUploader {
        z-index: 1;
        position: relative;
        font_size: 20px;
        text-align: center;
    }
    input, textarea {
        font-size: 18px !important;
    }
    .welcome-title {
        font-size: 150px;
        font-weight: bold;
        text-align: center;
        margin-top: 2rem;
        margin-bottom: 3rem;
        animation: fadeIn 1.3s ease-out forwards;
    }
    .welcome-desc {   
        font-size: 35px;
        color: #A9A9A9;
        text-align: center;
        margin-top: 1rem;
        margin-bottom: 2rem;
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
    st.markdown("""
        <style>
        .lottie-welcome-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 2rem;
            margin-bottom: 2rem;
        }
        iframe.lottie-welcome {
            width: 400px;
            height: 400px;
            opacity: 0.7;
            border: none;
            overflow: hidden;
        }
        </style>

        <div class="lottie-welcome-container">
            <iframe class="lottie-welcome" srcdoc='
                <!DOCTYPE html>
                <html>
                <head>
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.0/lottie.min.js"></script>
                    <style>
                        html, body {
                            margin: 0;
                            padding: 0;
                            height: 100vh;
                            width: 100vw;
                            background: transparent;
                            overflow: hidden;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                        }
                        #lottie {
                            width: 100%;
                            height: 100%;
                        }
                    </style>
                </head>
                <body>
                    <div id="lottie"></div>
                    <script>
                        lottie.loadAnimation({
                            container: document.getElementById("lottie"),
                            renderer: "svg",
                            loop: true,
                            autoplay: true,
                            path: "https://lottie.host/c8f76c44-71ab-41ed-b30d-5975839c1cc7/YAwYaiesCs.json"
                        });
                    </script>
                </body>
                </html>
            '></iframe>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""<h1 class="welcome-title">Welcome to the Resume Assistant</h1>""", unsafe_allow_html=True)
    st.markdown("""<p class="welcome-desc">This app helps you generate impactful bullet points for your resume and critique existing resumes to improve its contents! 
                Click the button below to navigate to the main page.</p>""", unsafe_allow_html=True)

    if st.button("→"):
        st.session_state.page = "main"
        st.rerun()

# Main Page
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
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="animated-title">Create and Review Resumes using AI</h1>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Generate Bullet Points", "Critique Resume"])

# Bullet Points Tab
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

# Resume Critique Tab
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

                        full_html = f"""
                            <style>
                            .two-column-container {{
                                display: flex;
                                gap: 2rem;
                                margin-top: 2rem;
                            }}
                            .left-sticky {{
                                position: sticky;
                                top: 80px;
                                flex: 1;
                                max-width: 50%;
                                height: 90vh;
                                overflow-y: auto;
                            }}
                            .left-sticky img {{
                                width: 100%;
                                height: auto;
                                border: 1px solid #ccc;
                                border-radius: 8px;
                            }}
                            .right-content {{
                                flex: 1;
                                max-width: 50%;
                                overflow-wrap: break-word;
                            }}
                            .right-content h3 {{
                                margin-top: 1.5rem;
                            }}
                            </style>

                            <div class="two-column-container">
                                <div class="left-sticky">
                                    <img src="data:image/png;base64,{encoded_image}" alt="Resume" />
                                </div>
                                <div class="right-content">
                        """

                        for section_title, section_content, critique in critiques:
                            full_html += f"<h3>{section_title}</h3>{critique}"

                        full_html += "</div></div>"

                        st.markdown(full_html, unsafe_allow_html=True)
                    else:
                        st.warning("Could not generate resume image.")
