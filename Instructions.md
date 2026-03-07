Building a "Career Co-Pilot" that handles everything from LinkedIn scraping to tailored resumes and visa-status communication is a high-value use case.

Below is a structured instructions.md file you can provide to an AI coding agent (like Cursor, Windsurf, or GitHub Copilot) to kickstart development.

🛠 Project Instructions: AI Resume & Outreach Architect
Project Overview
Build a web-based application that automates the job application process. The app will scrape LinkedIn job postings, analyze requirements, and rewrite an existing resume and cover letter to align with the role. It will also generate outreach templates (Email/LinkedIn) and handle international relocation context.

1. Tech Stack Requirements
Frontend: Next.js or React with Tailwind CSS (Simple, modern, lean UI). Must be responsive for Web, iOS, and Android views.

Backend: FastAPI (Python).

Orchestration: LangChain or LangGraph for LLM workflows.

LLM: Google Gemini API (via Google Generative AI SDK).

Database: Use a Repository Pattern to ensure loose coupling. Initial implementation: SQLite (local). Future-proof for DynamoDB/PostgreSQL.

File Handling: Support .docx parsing and generation.

2. Core Features & Logic
A. Profile & Resume Management
User must upload a "Base Resume" (.docx) before any generation starts.

Store resume data and user preferences locally.

Security: Ensure .docx files and API keys are strictly excluded via .gitignore.

B. Job Analysis Engine
Input: LinkedIn Job URL.

Action: Scrape job description (JD).

Logic: * Extract key skills and "must-haves."

Compare JD against the Base Resume.

Identify "hidden matches" (where the user has a similar skill that isn't explicitly worded like the JD).

C. The "Alignment" Workflow
Resume Tailoring: Rewrite bullet points to emphasize JD-relevant skills.

International Logic: If the job is outside India:

Check for "Onsite/International" experience in the resume and move it to a prominent position.

Insert a skillful section/statement regarding visa sponsorship willingness and relocation readiness.

Output: A downloadable, formatted .docx file.

D. Outreach Suite
Cover Letter: Contextualized based on the JD and tailored resume.

Email Write-up: If an email is found in the JD, generate a professional cold email with a mailto: link trigger.

LinkedIn DM: If an HR/Poster name is identified, generate a concise "InMail" style message.

3. Implementation Tasks
Project Setup: Initialize FastAPI and Next.js. Setup a .env template for GOOGLE_API_KEY.

Scraper Module: Create a robust utility to extract text from LinkedIn URLs (consider using playwright or selenium if simple requests are blocked).

LLM Chain: Build a LangChain prompt template for "Resume Alignment" that accepts JD_Text, Base_Resume, and Is_International flag.

UI Development: * Dashboard showing "Current Base Resume."

Input field for URL.

Review screen with "Before" and "After" comparisons.

Action buttons for "Download Doc," "Copy Email," and "Copy LinkedIn DM."

4. Safety & Standards
Environment Variables: Never hardcode keys. Use a .env file.

Git Ignore: Ensure *.docx, __pycache__, .env, and *.db are ignored.

Error Handling: Gracefully handle cases where the LinkedIn URL is private or requires a login.