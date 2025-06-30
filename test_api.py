from openai_helper import generate_bullets

test_experience = "Interned at a startup where I worked on web development using HTML, CSS, and Flask."
test_job_title = "Software Engineering Intern"

print("Testing bullet point generation...")
bullets = generate_bullets(test_experience, test_job_title)

for b in bullets:
    print("-", b)
