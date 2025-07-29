from openai_helper import generate_bullets, critique_resume, extract_section_image_from_pdf
import streamlit as st
import os

st.set_page_config(layout="wide", page_title="Resume Assistant", page_icon="📝")

st.title("Resume Assistant")
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
            st.write("Please enter both experience details and job title.")

with tab2:
    st.header("Generate Resume Critiques")
    pdf_file = st.file_uploader("Upload your resume as a PDF file", type=["pdf"])
    job_focus = st.text_input("Enter the job focus (optional):")

    if pdf_file is not None:
        if st.button("Critique Resume"):
            with st.spinner("Generating resume critiques..."):
                critiques = critique_resume(pdf_file, job_focus)
                for title, content, critique in critiques:
                    st.markdown(f"## {title}")
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("Resume Section Image")
                        img_path = extract_section_image_from_pdf(pdf_file, title)
                        if img_path:
                            st.image(img_path, caption=title, use_container_width=True)
                        else:
                            st.info("Could not find section image.")

                    with col2:
                        st.subheader("Critique")
                        st.markdown(critique, unsafe_allow_html=True)
