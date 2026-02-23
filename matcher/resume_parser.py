"""
Resume parser to extract information from various resume formats.
Supports PDF, DOCX, TXT, and JSON formats.
"""

import os
import json
from typing import Dict, Optional
import PyPDF2
import docx
import re


class ResumeParser:
    def __init__(self):
        self.supported_formats = ['pdf', 'docx', 'txt', 'json']
    
    def parse_resume(self, file_path: str) -> Dict:
        """
        Parse resume from file and return structured data.
        
        Args:
            file_path: Path to resume file
        
        Returns:
            Dictionary with structured resume data
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Resume file not found: {file_path}")
        
        file_ext = file_path.split('.')[-1].lower()
        
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        if file_ext == 'json':
            return self._parse_json(file_path)
        elif file_ext == 'pdf':
            text = self._extract_pdf_text(file_path)
        elif file_ext == 'docx':
            text = self._extract_docx_text(file_path)
        elif file_ext == 'txt':
            text = self._extract_txt_text(file_path)
        else:
            raise ValueError(f"Unsupported format: {file_ext}")
        
        # Extract structured data from text
        return self._extract_structured_data(text)
    
    def _parse_json(self, file_path: str) -> Dict:
        """Parse JSON resume file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
        return text
    
    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        text = ""
        try:
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            print(f"Error extracting DOCX text: {e}")
        return text
    
    def _extract_txt_text(self, file_path: str) -> str:
        """Extract text from TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading TXT file: {e}")
            return ""
    
    def _extract_structured_data(self, text: str) -> Dict:
        """
        Extract structured data from resume text using pattern matching.
        This is a basic implementation - for better results, use NLP or AI.
        
        Args:
            text: Resume text
        
        Returns:
            Structured resume data
        """
        # This is a simplified parser - in production, you'd use NLP or AI
        data = {
            "personal_info": {},
            "summary": "",
            "skills": {},
            "experience": [],
            "education": [],
            "certifications": [],
            "projects": [],
            "preferences": {}
        }
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            data["personal_info"]["email"] = emails[0]
        
        # Extract phone
        phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            data["personal_info"]["phone"] = phones[0]
        
        # Extract LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin = re.findall(linkedin_pattern, text.lower())
        if linkedin:
            data["personal_info"]["linkedin"] = linkedin[0]
        
        # Extract GitHub
        github_pattern = r'github\.com/[\w-]+'
        github = re.findall(github_pattern, text.lower())
        if github:
            data["personal_info"]["github"] = github[0]
        
        # Common programming languages
        languages = [
            'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Ruby', 'Go', 'Rust',
            'TypeScript', 'PHP', 'Swift', 'Kotlin', 'Scala', 'R', 'SQL'
        ]
        found_languages = [lang for lang in languages if lang.lower() in text.lower()]
        data["skills"]["programming_languages"] = found_languages
        
        # Common frameworks
        frameworks = [
            'React', 'Angular', 'Vue', 'Node.js', 'Express', 'Django', 'Flask',
            'Spring', 'Spring Boot', 'Rails', 'Laravel', 'ASP.NET', 'FastAPI'
        ]
        found_frameworks = [fw for fw in frameworks if fw.lower() in text.lower()]
        data["skills"]["frameworks"] = found_frameworks
        
        # Common databases
        databases = [
            'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Oracle', 'SQL Server',
            'Cassandra', 'DynamoDB', 'Elasticsearch'
        ]
        found_databases = [db for db in databases if db.lower() in text.lower()]
        data["skills"]["databases"] = found_databases
        
        # Cloud platforms
        cloud = ['AWS', 'Azure', 'Google Cloud', 'GCP', 'Heroku', 'DigitalOcean']
        found_cloud = [c for c in cloud if c.lower() in text.lower()]
        data["skills"]["cloud_platforms"] = found_cloud
        
        # Store raw text for AI processing
        data["_raw_text"] = text
        
        return data
    
    def load_resume_data(self, json_path: str) -> Dict:
        """
        Load structured resume data from JSON file.
        
        Args:
            json_path: Path to resume_data.json
        
        Returns:
            Resume data dictionary
        """
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Resume data file not found: {json_path}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_resume_data(self, data: Dict, json_path: str):
        """
        Save structured resume data to JSON file.
        
        Args:
            data: Resume data dictionary
            json_path: Path to save JSON file
        """
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
