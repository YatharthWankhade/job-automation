"""
AI helper utilities using Google Gemini API.
Handles job matching, cover letter generation, and application assistance.
"""

import os
import json
from typing import Dict, List, Optional, Tuple
import google.generativeai as genai
from datetime import datetime


class AIHelper:
    def __init__(self, api_key: str = None, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialize AI helper with Gemini API.
        
        Args:
            api_key: Google API key (if None, reads from GEMINI_API_KEY env var)
            model_name: Gemini model to use
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)
    
    def match_job_with_resume(self, job_data: Dict, resume_data: Dict) -> Tuple[float, str, List[str]]:
        """
        Match a job posting with resume data using AI.
        
        Args:
            job_data: Job information (title, description, requirements, etc.)
            resume_data: Resume information (skills, experience, education, etc.)
        
        Returns:
            Tuple of (match_score, rationale, missing_skills)
        """
        prompt = f"""
You are an expert career advisor and recruiter. Analyze the following job posting and candidate resume to determine how well they match.

JOB POSTING:
Title: {job_data.get('title', 'N/A')}
Company: {job_data.get('company', 'N/A')}
Location: {job_data.get('location', 'N/A')}
Description: {job_data.get('description', 'N/A')}
Requirements: {job_data.get('requirements', 'N/A')}

CANDIDATE RESUME:
{json.dumps(resume_data, indent=2)}

Please provide:
1. A match score from 0-100 (where 100 is a perfect match)
2. A detailed rationale explaining the match score
3. A list of missing skills or qualifications (if any)

Consider:
- Technical skills alignment
- Experience level match
- Industry/domain fit
- Education requirements
- Soft skills and cultural fit
- Career trajectory alignment

Respond in JSON format:
{{
    "match_score": <number 0-100>,
    "rationale": "<detailed explanation>",
    "missing_skills": ["skill1", "skill2", ...],
    "strengths": ["strength1", "strength2", ...],
    "recommendation": "<apply/consider/skip>"
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
            
            return (
                result.get('match_score', 0),
                result.get('rationale', ''),
                result.get('missing_skills', [])
            )
        except Exception as e:
            print(f"Error in AI matching: {e}")
            return (0, f"Error: {str(e)}", [])
    
    def generate_cover_letter(self, job_data: Dict, resume_data: Dict, 
                             match_rationale: str = "") -> str:
        """
        Generate a customized cover letter for a job application.
        
        Args:
            job_data: Job information
            resume_data: Resume information
            match_rationale: Optional rationale from matching analysis
        
        Returns:
            Generated cover letter text
        """
        prompt = f"""
You are an expert career coach. Write a compelling, personalized cover letter for the following job application.

JOB POSTING:
Title: {job_data.get('title', 'N/A')}
Company: {job_data.get('company', 'N/A')}
Description: {job_data.get('description', 'N/A')}

CANDIDATE INFORMATION:
Name: {resume_data.get('personal_info', {}).get('name', 'Candidate')}
Summary: {resume_data.get('summary', '')}
Key Skills: {', '.join(resume_data.get('skills', {}).get('programming_languages', [])[:5])}
Recent Experience: {resume_data.get('experience', [{}])[0].get('position', 'N/A')} at {resume_data.get('experience', [{}])[0].get('company', 'N/A')}

{f"MATCH ANALYSIS: {match_rationale}" if match_rationale else ""}

Write a professional cover letter that:
1. Opens with enthusiasm for the specific role and company
2. Highlights 2-3 most relevant experiences/achievements
3. Demonstrates knowledge of the company/role
4. Shows personality while remaining professional
5. Closes with a clear call to action
6. Is concise (250-350 words)

Do NOT use generic phrases like "I am writing to apply" or "Please find my resume attached".
Be specific, authentic, and compelling.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating cover letter: {e}")
            return f"Error generating cover letter: {str(e)}"
    
    def answer_application_question(self, question: str, resume_data: Dict, 
                                   job_data: Dict) -> str:
        """
        Answer an application question using AI based on resume and job data.
        
        Args:
            question: The application question
            resume_data: Resume information
            job_data: Job information
        
        Returns:
            Generated answer
        """
        prompt = f"""
You are helping a job candidate answer an application question. Provide a concise, honest, and professional answer.

QUESTION: {question}

JOB CONTEXT:
Title: {job_data.get('title', 'N/A')}
Company: {job_data.get('company', 'N/A')}

CANDIDATE BACKGROUND:
{json.dumps(resume_data, indent=2)}

Provide a direct, professional answer that:
1. Directly addresses the question
2. Is based on the candidate's actual experience/skills
3. Is concise (2-4 sentences unless more detail is clearly needed)
4. Sounds natural and authentic
5. Aligns with the job requirements

Answer:
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error answering question: {e}")
            return "I would be happy to discuss this further in an interview."
    
    def extract_job_requirements(self, job_description: str) -> Dict:
        """
        Extract structured requirements from a job description.
        
        Args:
            job_description: Raw job description text
        
        Returns:
            Dictionary with extracted requirements
        """
        prompt = f"""
Analyze this job description and extract key information in structured format.

JOB DESCRIPTION:
{job_description}

Extract and return in JSON format:
{{
    "required_skills": ["skill1", "skill2", ...],
    "preferred_skills": ["skill1", "skill2", ...],
    "years_of_experience": <number or null>,
    "education_required": "<degree level or null>",
    "key_responsibilities": ["resp1", "resp2", ...],
    "job_type": "<full-time/part-time/contract/etc>",
    "seniority_level": "<entry/mid/senior/lead/etc>"
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
            return result
        except Exception as e:
            print(f"Error extracting requirements: {e}")
            return {}
    
    def generate_followup_email(self, job_data: Dict, resume_data: Dict, 
                               application_date: str, attempt_number: int = 1) -> Tuple[str, str]:
        """
        Generate a follow-up email for a job application.
        
        Args:
            job_data: Job information
            resume_data: Resume information
            application_date: When the application was submitted
            attempt_number: Which follow-up attempt this is
        
        Returns:
            Tuple of (subject, body)
        """
        prompt = f"""
Write a professional follow-up email for a job application.

JOB DETAILS:
Title: {job_data.get('title', 'N/A')}
Company: {job_data.get('company', 'N/A')}

CANDIDATE: {resume_data.get('personal_info', {}).get('name', 'Candidate')}
APPLICATION DATE: {application_date}
FOLLOW-UP ATTEMPT: #{attempt_number}

Write a follow-up email that:
1. Is polite and professional
2. Expresses continued interest
3. Briefly reiterates key qualifications
4. Asks about application status
5. Is concise (100-150 words)
6. Adjusts tone based on attempt number (first follow-up vs. second, etc.)

Return in JSON format:
{{
    "subject": "<email subject line>",
    "body": "<email body>"
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
            return result.get('subject', ''), result.get('body', '')
        except Exception as e:
            print(f"Error generating follow-up email: {e}")
            return (
                f"Following up on {job_data.get('title')} Application",
                f"Error generating email: {str(e)}"
            )
