import os, re, tempfile, fitz, requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SECTION_ALIASES = {
    "Summary": ["Summary", "Professional Summary", "Objective"],
    "Education": ["Education", "Academic Background", "Academics"],
    "Technical Skills": ["Technical Skills", "Skills", "Tech Stack", "Technical"],
    "Experience": ["Experience", "Work History", "Professional Experience"],
    "Projects": ["Projects", "Technical Projects", "Personal Projects"],
    "Involvement": ["Involvement", "Leadership", "Extracurriculars", "Activities", "Extracurricular Activities"],
}

def normalize_section_name(title):
    for key, aliases in SECTION_ALIASES.items():
        if title.strip().lower() in [a.lower() for a in aliases]:
            return key
    return title.strip().title()

def generate_bullets(experience, job_title):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are a professional resume writer."},
            {"role": "user", "content": f"Create 3–5 SMART bullet points for:\nExperience: {experience}\nJob Title: {job_title}"}
        ],
        "max_tokens": 300,
        "temperature": 0.7
    }
    res = requests.post(url, headers=headers, json=data)
    return res.json()["choices"][0]["message"]["content"].split('\n')

def critique_resume(pdf_file, job_focus):
    pdf_file.seek(0)
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    full_text = "\n".join(page.get_text() for page in doc)
    doc.close()

    all_aliases = [a for aliases in SECTION_ALIASES.values() for a in aliases]
    pattern = r"(?:^|\n)(?=\s*(" + '|'.join(re.escape(a) for a in all_aliases) + r")\s*[\n:]?)"
    chunks = re.split(pattern, full_text, flags=re.IGNORECASE)

    sections = []
    i = 1
    while i < len(chunks):
        raw_title = chunks[i]
        section_title = normalize_section_name(raw_title)
        section_content = chunks[i + 1].strip() if (i + 1) < len(chunks) else ""
        critique = critique_section(section_title, section_content, job_focus)
        sections.append((section_title, section_content, critique))
        i += 2

    return sections

def critique_section(section_title, content, job_focus):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are a helpful and educated resume reviewer."},
            {"role": "user", "content": f"""
Critique this resume section.
Section Title: {section_title}
Content: {content}
Job Focus: {job_focus or "General"}

Respond in this format only:

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
"""}
        ],
        "max_tokens": 1000,
        "temperature": 0.6
    }
    res = requests.post(url, headers=headers, json=data)
    return res.json()["choices"][0]["message"]["content"].strip()

def extract_section_image_from_pdf(pdf_file, section_title):
    section_title = section_title.strip()
    pdf_file.seek(0)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        tmp_pdf.write(pdf_file.read())
        tmp_path = tmp_pdf.name

    doc = fitz.open(tmp_path)
    all_titles = [a.lower() for aliases in SECTION_ALIASES.values() for a in aliases]
    current_aliases = SECTION_ALIASES.get(section_title, [section_title])

    for page in doc:
        blocks = page.get_text("blocks")
        start, end = None, len(blocks)
        for i, b in enumerate(blocks):
            if any(alias.lower() in b[4].strip().lower() for alias in current_aliases):
                start = i
                break
        if start is None: continue
        for j in range(start + 1, len(blocks)):
            if any(alt in blocks[j][4].lower() for alt in all_titles if alt != section_title.lower()):
                end = j
                break
        clip_blocks = blocks[start:end+5]
        x0, y0 = min(b[0] for b in clip_blocks), min(b[1] for b in clip_blocks)
        x1, y1 = max(b[2] for b in clip_blocks), max(b[3] for b in clip_blocks) + 140
        rect = fitz.Rect(x0, y0, x1, y1)
        pix = page.get_pixmap(clip=rect, dpi=160)
        path = f"/tmp/section_{section_title.replace(' ', '_')}.png"
        pix.save(path)
        doc.close()
        return path

    doc.close()
    return None
