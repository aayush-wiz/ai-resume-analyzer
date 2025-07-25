"""
Agent 1: Resume Parser
Responsible for turning raw résumé text → StructuredResume
"""

import json
import os
from typing import Optional

import langdetect
from langdetect.lang_detect_exception import LangDetectException
from llama_index.llms.openrouter import OpenRouter
from loguru import logger
from pydantic import ValidationError

from core.models import StructuredResume, AnalysisState
from core.tools.text_tools import ResumeTextExtractorTool
from core.utils import normalise_dates, extract_emails

# ------------------------ Prompt Templates ------------------------ #

PARSE_PROMPT = """
You are a world-class résumé parser.
Return **only** valid JSON that conforms to the schema below.
Dates should be ISO-8601 (YYYY-MM-DD) or null if missing.

Schema:
{schema_json}

Résumé text:
{resume_text}
"""

FALLBACK_PROMPT = """
The résumé below is poorly formatted or non-English.
Think step by step and return valid JSON with these keys:
- full_name
- email, phone, linkedin, github, location
- education (list)
- work_experience (list)
- projects (list)
- certifications (list)
- skills (list of {category, skills})
- languages (list)

Résumé:
{resume_text}
"""


# ------------------------ Parsing Logic ------------------------ #

def _validate_and_retry(
        llm: OpenRouter,
        resume_text: str,
        attempt: int = 1,
) -> Optional[StructuredResume]:
    prompt = PARSE_PROMPT.format(
        resume_text=resume_text,
        schema_json=StructuredResume.model_json_schema(),
    )
    raw_json = llm.complete(prompt).text.strip()

    try:
        data = json.loads(raw_json)
        return StructuredResume(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        logger.warning(f'Validation failed (attempt {attempt}): {e}')
        if attempt >= 2:
            logger.warning("Switching to fallback prompt")
            prompt = FALLBACK_PROMPT.format(resume_text=resume_text)
            raw_json = llm.complete(prompt).text.strip()
            try:
                data = json.loads(raw_json)
                return StructuredResume(**data)
            except Exception as e2:
                logger.error(f'Fallback prompt also failed: {e2}')
                return None
        return _validate_and_retry(llm, resume_text, attempt + 1)


# ------------------------ Main Agent ------------------------ #

def parse_resume_agent(state: AnalysisState) -> AnalysisState:
    """
    Entry point for Agent 1.
    Accepts either:
      - state.raw_resume_text already filled, or
      - state.resume_file_path set and text will be extracted here.
    """
    logger.info("🤖 Running Agent 1: Resume Parser")

    # 0. Obtain raw text if not present
    if not state.raw_resume_text and state.resume_file_path:
        logger.info(f'Extracting text from {state.resume_file_path}')
        state.raw_resume_text = ResumeTextExtractorTool().run(state.resume_file_path)

    if not state.raw_resume_text:
        logger.error("❌ No résumé text available to parse.")
        return state

    # 1. LLM extraction
    llm = OpenRouter(
        model="kimi-ai/kimi-2",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0.0,
    )

    structured = _validate_and_retry(llm, state.raw_resume_text)
    if structured is None:
        logger.error("❌ Failed to parse résumé after all attempts.")
        return state

    # 2. Deterministic post-processing
    for edu in structured.education:
        edu.start_date = normalise_dates(edu.start_date)
        edu.end_date = normalise_dates(edu.end_date)

    for work in structured.work_experience:
        work.start_date = normalise_dates(work.start_date)
        work.end_date = normalise_dates(work.end_date)

    # 3. Email enrichment
    if not structured.contact.email:
        emails = extract_emails(state.raw_resume_text)
        if emails:
            structured.contact.email = emails[0]

    # 4. Language detection
    try:
        lang = langdetect.detect(state.raw_resume_text)
    except LangDetectException:
        lang = "unknown"
    structured.detected_language = lang  # non-schema attribute is OK for state

    state.structured_resume = structured
    logger.success(f'✅ Parser finished for {structured.contact.full_name}')
    return state
