import os

from llama_index.core import SimpleDirectoryReader

from agents import (
    parse_resume_agent,
    research_market_agent,
    analyze_gaps_agent,
    synthesize_report_agent
)
from models import AnalysisState


def run_multi_agent_workflow(resume_path: str) -> str:
    """
    Orchestrates the full multi-agent resume analysis workflow.
    """
    print("--- Workflow Started ---")

    # Ingest resume and initialize state
    try:
        resume_text = SimpleDirectoryReader(input_files=[resume_path]).load_data()[0].text
        state = AnalysisState(resume_text=resume_text)
    except Exception as e:
        return f"Error loading resume: {e}"

    # Agent Chain
    state = parse_resume_agent(state)
    # state = research_market_agent(state) # Uncomment as you build
    # state = analyze_gaps_agent(state)    # Uncomment as you build
    final_report = synthesize_report_agent(state)  # Will use placeholder for now

    print("\n--- Workflow Finished ---")
    return final_report
