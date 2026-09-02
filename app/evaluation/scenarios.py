"""Offline evaluation scenarios covering varied profiles and searches."""

from pydantic import BaseModel, Field

from app.schemas.job import JobSearchRequest


class EvaluationScenario(BaseModel):
    name: str
    skills: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    experience: list[str] = Field(default_factory=list)
    search: JobSearchRequest


SCENARIOS = [
    EvaluationScenario(
        name="beginner_remote_ai_india",
        skills=["Python", "Git", "REST APIs"],
        projects=["Built a Python REST API for a student project"],
        education=["B.Tech Computer Science student"],
        search=JobSearchRequest(
            query="AI", location="India", remote_only=True, beginner_friendly=True
        ),
    ),
    EvaluationScenario(
        name="generative_ai_rag",
        skills=["Python", "Prompt Engineering", "Git", "RAG"],
        projects=["Built a RAG assistant with embeddings"],
        search=JobSearchRequest(query="Generative AI", beginner_friendly=True),
    ),
    EvaluationScenario(
        name="machine_learning_student",
        skills=["Python", "pandas", "scikit-learn"],
        education=["B.Sc. Statistics"],
        projects=["Trained a scikit-learn classification model"],
        search=JobSearchRequest(query="Machine Learning", location="Bengaluru"),
    ),
    EvaluationScenario(
        name="agentic_ai_builder",
        skills=["Python", "LLMs", "APIs", "LangGraph"],
        projects=["Created a LangGraph tool-using agent"],
        search=JobSearchRequest(query="Agentic AI", remote_only=True),
    ),
    EvaluationScenario(
        name="python_beginner_pune",
        skills=["Python", "OOP", "Git"],
        education=["Diploma in software development"],
        search=JobSearchRequest(query="Python AI", location="Pune", beginner_friendly=True),
    ),
    EvaluationScenario(
        name="junior_backend_ai",
        skills=["Python", "FastAPI", "SQL", "Docker"],
        experience=["One year building backend APIs"],
        projects=["Deployed a FastAPI service with Docker"],
        search=JobSearchRequest(query="Junior AI Engineer", location="Hyderabad"),
    ),
    EvaluationScenario(
        name="automation_api_intern",
        skills=["Python", "REST APIs", "Problem Solving"],
        projects=["Automated a reporting workflow with Python"],
        search=JobSearchRequest(query="AI Automation", remote_only=True, beginner_friendly=True),
    ),
    EvaluationScenario(
        name="llm_retrieval_intern",
        skills=["Python", "LLM Fundamentals", "Git", "NLP"],
        projects=["Evaluated prompts for an NLP application"],
        search=JobSearchRequest(query="LLM Engineer", remote_only=True),
    ),
    EvaluationScenario(
        name="data_science_chennai",
        skills=["Python", "pandas", "Statistics", "Data Visualization"],
        education=["B.Sc. Data Science student"],
        search=JobSearchRequest(query="Data Science", location="Chennai", beginner_friendly=True),
    ),
    EvaluationScenario(
        name="applied_ai_projects",
        skills=["Python", "Machine Learning", "Model Evaluation", "PyTorch"],
        projects=["Compared PyTorch image classifiers", "Evaluated an NLP classifier"],
        education=["Final-year computer science student"],
        search=JobSearchRequest(query="Applied AI", location="Gurugram"),
    ),
]
