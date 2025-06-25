from openai import OpenAI
import os
import fitz
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Set OpenAI API key
client = OpenAI()

def generate_bullets(experience, job_title):
    prompt = f""" You are a professional resume writer.
    Generate 3-5 bullet points for a resume based on the following experience and job title.
    Experience: {experience}
    Job Title: {job_title}
    Bullet Points:"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful and educated resume reviewer."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.7
    )
    bullet_points = response.choices[0].message['content'].strip()
    return bullet_points.split('\n') if bullet_points else []

def critique_resume(pdf_file, job_focus):
    try:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        prompt = f"""You are a professional resume reviewer.
        Critique the following resume text and provide feedback.
        Resume Text: {text}
        Job Focus: {job_focus if job_focus else "General"}
        Provide feedback on structure, content, and areas for improvement in a format
        of two bullet points for strengths, two bullet points for weaknesses, and two bullet points for suggestions per section."""
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful and educated resume reviewer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature = 0.6

        )
        critique = response.choices[0].message['content'].strip()
        return critique.split('\n') if critique else []
    
    except Exception as e:
        print(f"Error reading resume PDF file: {e}")
        return []
    



