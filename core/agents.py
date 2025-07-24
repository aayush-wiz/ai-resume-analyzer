import os

from models import AnalysisState


def parse_resume_agent(state: AnalysisState) -> AnalysisState:
    print("🤖 Running Agent 1: The Parser...")
    # Logic to be added here
    print("Parser finished.")
    return state


def research_market_agent(state: AnalysisState) -> AnalysisState:
    print("\n🤖 Running Agent 2: The Researcher...")
    # Logic to be added here
    print("Researcher finished.")
    return state


def analyze_gaps_agent(state: AnalysisState) -> AnalysisState:
    print("\n🤖 Running Agent 3: The Analyst...")
    # Logic to be added here
    print("Analyst finished.")
    return state


def synthesize_report_agent(state: AnalysisState) -> str:
    print("\n🤖 Running Agent 4: The Synthesizer...")
    # Logic to be added here
    final_report = "This is a placeholder for the final report."
    print("Synthesizer finished.")
    return final_report
