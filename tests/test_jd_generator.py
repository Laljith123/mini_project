import pytest
from unittest.mock import MagicMock, patch
from src.models.schemas import GeneratedJobDescription
from src.generate.jd_generator import JobDescriptionGenerator
from src.generate.prompts import JD_GENERATION_SYSTEM_PROMPT, JD_GENERATION_USER_PROMPT


def test_generated_job_description_schema():
    jd = GeneratedJobDescription(
        title="AI Engineer",
        department="AI & Data",
        experience_level="Senior (5-8 yrs)",
        role_overview="Build cutting-edge generative AI models.",
        key_responsibilities=["Develop RAG systems", "Optimize latency"],
        must_have_skills=["Python", "PyTorch", "Gemini API"],
        nice_to_have_skills=["Docker", "Kubernetes"],
        experience_requirements="5+ years in ML engineering",
        performance_metrics=["Deploy 2 pipelines in Q1"],
        evaluation_rubric=["System design depth", "Python coding"],
        compensation_and_benefits="Competitive salary + equity",
    )
    assert jd.title == "AI Engineer"
    assert len(jd.key_responsibilities) == 2
    assert len(jd.must_have_skills) == 3


def test_job_description_generator_prompt_assembly():
    generator = JobDescriptionGenerator(api_key="fake-test-key")

    mock_client = MagicMock()
    mock_response = MagicMock()
    sample_json = """{
        "title": "Machine Learning Engineer",
        "department": "Engineering",
        "experience_level": "Mid-Level",
        "role_overview": "Develop and deploy scalable ML services.",
        "key_responsibilities": ["Train models", "Monitor inference"],
        "must_have_skills": ["Python", "TensorFlow"],
        "nice_to_have_skills": ["Docker"],
        "experience_requirements": "3+ years",
        "performance_metrics": ["Achieve 99% uptime"],
        "evaluation_rubric": ["Model evaluation expertise"],
        "compensation_and_benefits": "Full healthcare and 401k",
        "raw_markdown": ""
    }"""
    mock_response.text = sample_json
    mock_client.models.generate_content.return_value = mock_response

    with patch("src.generate.jd_generator.get_gemini_client", return_value=mock_client):
        result = generator.generate(
            job_title="Machine Learning Engineer",
            department="Engineering",
            experience_level="Mid-Level",
            required_skills=["Python", "TensorFlow"],
            preferred_skills=["Docker"],
            responsibilities="Train models and monitor inference.",
        )

        assert result.title == "Machine Learning Engineer"
        assert "Python" in result.must_have_skills
        assert "## 🎯 Key Responsibilities" in result.raw_markdown
        assert "Machine Learning Engineer" in result.raw_markdown
