"""
AI-Powered Job Description Generator.
Synthesizes customized, enterprise-ready Job Descriptions based on role requirements,
candidate skills, experience levels, and business objectives using Google GenAI SDK.
"""

import json
import logging
from typing import Optional, Union, List
from google.genai import types

from src.config import settings, get_gemini_client
from src.models.schemas import GeneratedJobDescription
from src.generate.prompts import (
    JD_GENERATION_SYSTEM_PROMPT,
    JD_GENERATION_USER_PROMPT,
)

logger = logging.getLogger(__name__)


class JobDescriptionGenerator:
    """Generates structured, customized job descriptions tailored to role requirements and skills."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY

    def generate(
        self,
        job_title: str,
        department: str = "Engineering",
        experience_level: str = "Mid-Level",
        required_skills: Union[List[str], str] = "",
        preferred_skills: Union[List[str], str] = "",
        responsibilities: str = "",
        work_arrangement: str = "Hybrid",
        company_context: str = "High-growth technology team building modern intelligent systems.",
        model_name: Optional[str] = None,
    ) -> GeneratedJobDescription:
        """
        Generate a comprehensive, customized job description based on criteria.
        """
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required for Job Description generation.")

        req_skills_str = (
            ", ".join(required_skills)
            if isinstance(required_skills, list)
            else str(required_skills).strip()
        )
        pref_skills_str = (
            ", ".join(preferred_skills)
            if isinstance(preferred_skills, list)
            else str(preferred_skills).strip()
        )

        user_prompt = JD_GENERATION_USER_PROMPT.format(
            job_title=job_title or "Software Engineer",
            department=department or "Engineering",
            experience_level=experience_level or "Mid-Level",
            required_skills=req_skills_str or "Core domain proficiency and problem-solving",
            preferred_skills=pref_skills_str or "Modern cloud, automated testing, GenAI familiarity",
            responsibilities=responsibilities or "Design, develop, and maintain high-reliability services.",
            work_arrangement=work_arrangement or "Hybrid",
            company_context=company_context or "Collaborative agile environment delivering customer value.",
        )

        client = get_gemini_client(api_key=self.api_key)
        target_model = model_name or settings.GEMINI_MODEL

        config = types.GenerateContentConfig(
            system_instruction=JD_GENERATION_SYSTEM_PROMPT,
            temperature=0.3,
            response_mime_type="application/json",
            response_json_schema=GeneratedJobDescription.model_json_schema(),
        )

        response = client.models.generate_content(
            model=target_model,
            contents=user_prompt,
            config=config,
        )

        raw_text = response.text or "{}"
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        result = GeneratedJobDescription.model_validate_json(cleaned)

        # Assemble clean, professional markdown representation
        md_lines = [
            f"# {result.title}",
            f"**Department:** {result.department}  |  **Level:** {result.experience_level}  |  **Workplace:** {work_arrangement}",
            "",
            "## 📌 Role Overview & Business Impact",
            result.role_overview,
            "",
            "## 🎯 Key Responsibilities",
        ]
        for resp in result.key_responsibilities:
            md_lines.append(f"- {resp}")

        md_lines.extend(["", "## 🛠 Must-Have Skills & Qualifications"])
        if result.experience_requirements:
            md_lines.append(f"**Experience:** {result.experience_requirements}")
        for skill in result.must_have_skills:
            md_lines.append(f"- {skill}")

        if result.nice_to_have_skills:
            md_lines.extend(["", "## ⭐ Preferred / Nice-to-Have Skills"])
            for skill in result.nice_to_have_skills:
                md_lines.append(f"- {skill}")

        if result.performance_metrics:
            md_lines.extend(["", "## 📈 Key Milestones & Success Metrics (First 90-180 Days)"])
            for metric in result.performance_metrics:
                md_lines.append(f"- {metric}")

        if result.evaluation_rubric:
            md_lines.extend(["", "## 📋 Candidate Assessment Rubric"])
            for rubric in result.evaluation_rubric:
                md_lines.append(f"- {rubric}")

        if result.compensation_and_benefits:
            md_lines.extend(["", "## 💼 Compensation & Workplace Benefits", result.compensation_and_benefits])

        result.raw_markdown = "\n".join(md_lines)
        return result
