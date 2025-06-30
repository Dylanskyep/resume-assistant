from openai_helper import generate_bullets, critique_resume
import streamlit as st
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Streamlit app for resume review and bullet point generation
st.title("Create and Review Resumes using AI")
st.markdown("""
    This app allows you to generate bullet points for a resume based on a given experience and job title,
    and to critique an existing resume PDF file.
""")
tab1, tab2 = st.tabs(["Generate Bullet Points", "Critique Resume"])

#Generate Bullet Points Section
with tab1:
    st.header("Create Resume Experience Bullet Points")
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
    st.header("Create Resume Critiques")
    pdf_file = st.file_uploader("Upload you resume as a PDF file", type=["pdf"])
    job_focus = st.text_input("Enter the job focus (optional):")
    if pdf_file is not None:
        if st.button("Critique Resume"):
            with st.spinner("Generating resume critiques..."):
                critique = critique_resume(pdf_file, job_focus)
                if critique:
                    st.subheader("Results")
                    for line in critique:
                        stripped = line.strip()
                    if stripped:
                        if stripped.startswith(("-", "•", "*")):
                            st.markdown(f"{stripped}")
                        else:
                            st.markdown(f"- {stripped}")

                    st.download_button("Download Critiques", "\n".join(critique), file_name="critiques.txt")

                else:
                    st.write("Please check the PDF file format or job focus to ensure they are valid.")
    else:
        st.write("Please upload a PDF file of your resume before clicking the button.")




