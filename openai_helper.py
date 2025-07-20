import os
import re
import tempfile
import fitz
import requests
from fpdf import FPDF

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SECTION_ALIASES = {
    "Summary": ["Summary", "Professional Summary", "Objective"],
    "Education": ["Education", "Academic Background"],
    "Technical Skills": ["Technical Skills", "Skills", "Tech Stack"],
    "Experience": ["Experience", "Work History", "Professional Experience"],
    "Projects": ["Projects", "Technical Projects", "Personal Projects"],
    "Involvement": ["Involvement", "Leadership", "Extracurriculars", "Activities"]
}

def normalize_section_name(title):
    for key, aliases in SECTION_ALIASES.items():
        if title.strip().lower() in [a.lower() for a in aliases]:
            return key
    return title.strip().title()

def generate_bullets(experience, job_title):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are a professional resume writer."},
            {"role": "user", "content": f"""
Generate 3–5 resume bullet points using the SMART framework for:
Experience: {experience}
Job Title: {job_title}
"""}
        ],
        "max_tokens": 300,
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    return result["choices"][0]["message"]["content"].strip().split('\n')

def critique_resume(pdf_file, job_focus):
    pdf_file.seek(0)
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()

    # Dynamic section splitting
    all_aliases = [a for aliases in SECTION_ALIASES.values() for a in aliases]
    section_regex = r'\n(?=\s*(' + '|'.join(re.escape(a) for a in all_aliases) + r')\s*:?)'
    chunks = re.split(section_regex, text, flags=re.IGNORECASE)

    paired_sections = []
    for i in range(1, len(chunks), 2):
        raw_title = chunks[i]
        section_title = normalize_section_name(raw_title)
        section_content = chunks[i + 1].strip()
        critique = critique_section(section_title, section_content, job_focus)
        paired_sections.append((section_title, section_content, critique))

    return paired_sections

def critique_section(section_title, section_content, job_focus):
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": "You are a helpful and educated resume reviewer."},
                {"role": "user", "content": f"""
                Critique the following resume text and provide feedback.
                Section Title: {section_title}
                Resume Text: {section_content}
                Job Focus: {job_focus if job_focus else "General"}
                Provide feedback on structure, content, and areas for improvement in a format
                of two bullet points for
                 strengths, two bullet points for weaknesses, and two bullet points for suggestions per section.
                Organize your feedback clearly using labeled sections like:
                In bold, write the section title with slightly larger font, followed by bullet points for each category.
                In a font slightly smaller than the section title, write the strengths, weaknesses, and suggestions headings.
                Then, list the bullet points after each corresponding heading.
                Example:
                Title of Section in Bold and slightly larger font
                Strengths
                - ...
                - ...

                Weaknesses
                - ...
                - ...

                Suggestions
                - ...
                - ...

                Make sure each section is adequately separated by each section with enough spacing to differentiate them.
                """}
            ],
            "max_tokens": 1000,
            "temperature": 0.6
        }

        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        if "choices" not in result:
            print("Unexpected response structure:", result)
            raise ValueError("Groq API response missing 'choices' key")

        critique_text = result["choices"][0]["message"]["content"]
        return critique_text.strip()

def extract_section_image_from_pdf(pdf_file, section_title):
    pdf_file.seek(0)  
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        tmp_pdf.write(pdf_file.read())
        tmp_pdf.flush()

    doc = fitz.open(tmp_pdf.name)
    section_img_paths = []

    for page in doc:
        text_instances = page.search_for(section_title, hit_max=1)
        if text_instances:
            rect = text_instances[0]
            rect.y1 += 200  
            pix = page.get_pixmap(clip=rect, dpi=150)
            image_path = f"/tmp/section_{section_title}.png"
            pix.save(image_path)
            section_img_paths.append(image_path)
            break 

    doc.close()
    return section_img_paths[0] if section_img_paths else None
