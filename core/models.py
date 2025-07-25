import datetime as dt
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

"""Core data models for the resume analysis workflow.
These models define the structure of the data used by various agents in the system.
"""


class Contact(BaseModel):
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    location: Optional[str] = None


class EducationItem(BaseModel):
    institution: str
    degree: str
    major: Optional[str] = None
    gpa: Optional[float] = None
    start_date: Optional[dt.date] = None
    end_date: Optional[dt.date] = None

    @classmethod
    def _check_dates(cls, v, values):
        start = values.data.get("start_date")
        if v and start and v < start:
            raise ValueError("end_date must be ≥ start_date")
        return v


class WorkItem(BaseModel):
    company: str
    title: str
    location: Optional[str] = None
    start_date: Optional[dt.date] = None
    end_date: Optional[dt.date] = None
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)

    @field_validator("end_date")
    def _check_dates(self, v, values):
        if v and values.get("start_date") and v < values["start_date"]:
            raise ValueError("end_date must be ≥ start_date")
        return v


class ProjectItem(BaseModel):
    name: str
    description: str
    technologies: List[str] = Field(default_factory=list)
    url: Optional[str] = None


class Certification(BaseModel):
    name: str
    issuer: str
    issue_date: Optional[dt.date] = None
    expiry_date: Optional[dt.date] = None


class SkillBucket(BaseModel):
    category: str
    skills: List[str]


class StructuredResume(BaseModel):
    contact: Contact
    summary: Optional[str] = None
    education: List[EducationItem] = Field(default_factory=list)
    work_experience: List[WorkItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    skills: List[SkillBucket] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)


class Experience(BaseModel):
    position: str = Field(description="The job title or position.")
    company: str = Field(description="The name of the company.")
    duration: str = Field(description="The duration of employment.")
    summary: str = Field(description="A summary of responsibilities and achievements.")


# --- Model for Agent 2 Output ---
class MarketResearch(BaseModel):
    """Structured summary of job market trends from web research."""

    trending_roles: List[str] = Field(
        description="List of job titles currently in demand."
    )
    required_skills: List[str] = Field(
        description="List of key skills and technologies sought by employers."
    )
    market_summary: str = Field(
        description="A brief summary of the job market for this profile."
    )


# --- Model for Agent 3 Output ---
class GapAnalysis(BaseModel):
    """Comparison of the résumé against market research."""

    candidate_strengths: List[str] = Field(
        description="Skills and experiences the candidate has that are in demand."
    )
    candidate_gaps: List[str] = Field(
        description="Important skills the candidate is missing based on market trends."
    )
    improvement_suggestions: str = Field(
        description="Actionable advice for the candidate to bridge the gaps."
    )


# --- The Central State Object ---
class AnalysisState(BaseModel):
    """
    The central state object that is passed between agents in the workflow.
    Each agent enriches this state with its findings.
    """

    raw_resume_text: str = Field(
        description="The original text extracted from the resume file."
    )
    structured_resume: Optional[StructuredResume] = Field(
        default=None,
        description="The resume parsed into a structured Pydantic model by the Parser Agent.",
    )
    market_research: Optional[str] = Field(
        default=None,
        description="A summary of market trends and required skills from the Researcher Agent.",
    )
    gap_analysis: Optional[str] = Field(
        default=None,
        description="A structured analysis of the candidate's skills vs. market demands from the Analyst Agent.",
    )
