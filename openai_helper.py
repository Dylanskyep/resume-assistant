import os
import requests
import fitz
from fpdf import FPDF
import re

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_bullets(experience, job_title):
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
            You are a professional resume writer.
            Generate 3-5 bullet points for a resume based on the following experience and job title using the SMART framework (Specific, Measurable, Achievable, Relevant, and Time-bound). 
            Each bullet point should describe a concrete impact or achievement from the experience below, tailored to the provided job title.
            Use action verbs, quantify results where possible, and focus on accomplishments.
            Experience: {experience}
            Job Title: {job_title}
            Bullet Points:
            """}
        ],
        "max_tokens": 300,
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=data)
    
    try:
        result = response.json()
    except Exception as e:
        print("Failed to parse JSON:", e)
        print("Raw response:", response.text)
        raise

    if "choices" not in result:
        print("Unexpected response structure:", result)
        raise ValueError("Groq API response missing 'choices' key")

    bullet_text = result["choices"][0]["message"]["content"]
    return bullet_text.strip().split('\n')

def critique_resume(pdf_file, job_focus):
    try:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()

        chunks = re.split(r'\n(?=\s*(Education|Experience|Skills|Projects|Certifications|Summary|Objective)\s*:?)', text, flags=re.IGNORECASE)
        paired_sections = []

        for i in range(1, len(chunks), 2):
            section_title = chunks[i].strip().title()
            section_content = chunks[i+1].strip()
            full_text = f"{section_title}\n{section_content}"

            critique = critique_section(section_title, section_content, job_focus)
            paired_sections.append((section_title, section_content, critique))
    except Exception as e:
        print(f"Error reading resume PDF file: {e}")
        return []

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
        return critique_text.strip().split('\n')

 
