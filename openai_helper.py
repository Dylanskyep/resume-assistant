import os
import re
import tempfile
import fitz
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SECTION_ALIASES = {
    "Summary": ["Summary", "Professional Summary", "Objective"],
    "Education": ["Education", "Academic Background", "Academics"],
    "Technical Skills": ["Technical Skills", "Skills", "Tech Stack", "Technical"],
    "Experience": ["Experience", "Work History", "Professional Experience"],
    "Projects": ["Projects", "Technical Projects", "Personal Projects"],
    "Involvement": ["Involvement", "Leadership", "Extracurriculars", "Activities", "Extracurricular Activities", "Extracurricular Involvement"],
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

Provide:
- 2 bullet points for strengths
- 2 bullet points for weaknesses
- 2 bullet points for suggestions

Format like this:

**{section_title}**

**Strengths**
- ...
- ...

**Weaknesses**
- ...
- ...

**Suggestions**
- ...
- ...

Use no extra text outside that structure.
"""}
        ],
        "max_tokens": 1000,
        "temperature": 0.6
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    return result["choices"][0]["message"]["content"].strip()

def extract_section_image_from_pdf(pdf_file, section_title):
    if not section_title or not isinstance(section_title, str):
        return None

    section_title = section_title.strip()
    pdf_file.seek(0)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        tmp_pdf.write(pdf_file.read())
        tmp_pdf_path = tmp_pdf.name

    doc = fitz.open(tmp_pdf_path)

    all_titles = [a.lower() for aliases in SECTION_ALIASES.values() for a in aliases]
    current_aliases = SECTION_ALIASES.get(section_title, [section_title])
    normalized_title = section_title.lower()

    for page_number, page in enumerate(doc):
        blocks = page.get_text("blocks")

        start_idx = None
        for i, block in enumerate(blocks):
            if any(alias.lower() in block[4].strip().lower() for alias in current_aliases):
                start_idx = i
                break
        if start_idx is None:
            continue

        end_idx = len(blocks)
        for j in range(start_idx + 1, len(blocks)):
            if any(alt in blocks[j][4].lower() for alt in all_titles if alt != normalized_title):
                end_idx = j
                break

        buffer = 5
        section_blocks = blocks[start_idx:end_idx + buffer]
        x0 = min(b[0] for b in section_blocks)
        y0 = min(b[1] for b in section_blocks)
        x1 = max(b[2] for b in section_blocks)
        y1 = max(b[3] for b in section_blocks) + 140  # INCREASED BUFFER

        rect = fitz.Rect(x0, y0, x1, y1)
        pix = page.get_pixmap(clip=rect, dpi=160)

        image_path = f"/tmp/section_{section_title.replace(' ', '_')}_{page_number}.png"
        pix.save(image_path)
        doc.close()
        return image_path

    doc.close()
    return None
