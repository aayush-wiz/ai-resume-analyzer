from typing import List, Optional

from pydantic import BaseModel, Field


# --- Sub-models for structured data ---
class Skill(BaseModel):
    name: str = Field(description="The name of the skill, software, or technology.")
    level: Optional[str] = Field(description="Candidate's proficiency, e.g., 'Advanced'.")


class Experience(BaseModel):
    position: str = Field(description="The job title or position.")
    company: str = Field(description="The name of the company.")
    duration: str = Field(description="The duration of employment.")
    summary: str = Field(description="A summary of responsibilities and achievements.")


# --- Model for Agent 1 Output ---
class StructuredResume(BaseModel):
    """Structured representation of a candidate's resume."""
    full_name: str
    summary: str
    skills: List[Skill]
    experience: List[Experience]


# --- Model for Agent 2 Output ---
class MarketResearch(BaseModel):
    """Structured summary of job market trends from web research."""
    trending_roles: List[str] = Field(description="List of job titles currently in demand.")
    required_skills: List[str] = Field(description="List of key skills and technologies sought by employers.")
    market_summary: str = Field(description="A brief summary of the job market for this profile.")


# --- Model for Agent 3 Output ---
class GapAnalysis(BaseModel):
    """Comparison of the resume against market research."""
    candidate_strengths: List[str] = Field(description="Skills and experiences the candidate has that are in demand.")
    candidate_gaps: List[str] = Field(description="Important skills the candidate is missing based on market trends.")
    improvement_suggestions: str = Field(description="Actionable advice for the candidate to bridge the gaps.")


# --- The Central State Object ---
class AnalysisState(BaseModel):
    """The central state object that holds all data for the analysis workflow."""
    resume_text: str
    structured_resume: Optional[StructuredResume] = None
    market_research: Optional[MarketResearch] = None
    gap_analysis: Optional[GapAnalysis] = None
