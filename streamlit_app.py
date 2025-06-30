from openai_helper import generate_bullets, critique_resume
import streamlit as st
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .center-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding-top: 3rem;
        text-align: center;
    }
    .stTextInput > div > input, .stTextArea > div > textarea {
        width: 600px !important;
        margin: 0 auto;
    }
    </style>
""", unsafe_allow_html=True)


#Welcome Page
if "page" not in st.session_state:
    st.session_state.page = "welcome"

if st.session_state.page == "welcome":
    st.title("Welcome to the Resume Assistant")
    st.markdown("Create and review resumes using AI-powered tools.")
    if st.button("Continue to Main Page"):
        st.session_state.page = "main"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "main":
    # Streamlit app for resume review and bullet point generation
    st.set_page_config(layout="wide")
    st.title("Create and Review Resumes using AI")
    # Custom CSS to adjust the layout   
    st.markdown("""
        <style>
        .main .block-container {
            max-width: 75%;
            padding-left: 4em;
            padding-right: 4rem;
            margin: auto;
        }
        </style>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Generate Bullet Points", "Critique Resume"])

    #Generate Bullet Points Section
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

        st.markdown('</div>', unsafe_allow_html=True)

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
            
        st.markdown('</div>', unsafe_allow_html=True)





