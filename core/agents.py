# In core/agents.py
import os
from llama_index.llms.openrouter import OpenRouter
from llama_index.tools.tavily_research import TavilyToolSpec

from models import AnalysisState
from agents import parse_resume_agent
from models import AnalysisState

state = AnalysisState(resume_file_path="resume.pdf")
state = parse_resume_agent(state)
# --- Agent 2: The Market Researcher (using Tavily) ---
# This agent uses the parsed résumé to search for current market trends.

def research_market_agent(state: AnalysisState) -> AnalysisState:
    """
    Researches job market trends based on the parsed resume.
    Uses Tavily for real-time, high-quality web search results.
    """
    print("\n🤖 Running Agent 2: The Researcher (Tool: Tavily)")
    if not state.structured_resume:
        raise ValueError("Cannot run researcher without structured resume data.")

    # Formulate a search query based on the resume
    most_recent_role = state.structured_resume.experience[
        0].position if state.structured_resume.experience else "entry-level"
    key_skills = ", ".join([skill.name for skill in state.structured_resume.skills[:5]])
    query = f"Current job market trends, in-demand skills, and typical salary for a '{most_recent_role}' with skills in {key_skills}."

    print(f"🔎 Conducting search with query: '{query}'")

    # Initialize and use the Tavily tool
    tavily_tool = TavilyToolSpec(api_key=os.getenv("TAVILY_API_KEY"))
    # We perform a search and get back a list of results
    results = tavily_tool.search(query=query, max_results=3)

    # Consolidate results into a single string for the next agent
    research_summary = "\n\n".join([res.text for res in results])
    state.market_research = research_summary

    print("✅ Researcher finished. Market data collected.")
    return state


# --- Agent 3: The Analyst (using Gemini Pro) ---
# This agent compares the resume against the market research to find gaps.

def analyze_gaps_agent(state: AnalysisState) -> AnalysisState:
    """
    Analyzes the gap between the candidate's skills and the market demands.
    Uses Gemini Pro for its strong reasoning and analytical capabilities.
    """
    print("\n🤖 Running Agent 3: The Analyst (Model: Gemini Pro)")
    if not state.structured_resume or not state.market_research:
        raise ValueError("Cannot run analyst without resume data and market research.")

    # Initialize the LLM for this agent
    analyst_llm = OpenRouter(
        model="google/gemini-pro",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0.2,
    )

    # Create a detailed prompt for the analysis
    candidate_profile = state.structured_resume.model_dump_json(indent=2)
    prompt = f"""
    You are an expert career analyst. Your task is to perform a detailed gap analysis for a candidate based on their resume and current market research.

    **Candidate's Profile:**
    ```json
    {candidate_profile}
    ```

    **Live Market Research Summary:**
    ```
    {state.market_research}
    ```

    **Your Analysis Task:**
    Based on the two pieces of information above, provide a structured analysis in MARKDOWN format. The analysis must include:
    1.  **Top 3 Job Recommendations:** Suggest three specific job titles that are a strong match.
    2.  **Key Strengths:** List the candidate's top 3-5 skills and experiences that are highly relevant to the current market.
    3.  **Skill Gap Analysis:** Identify the top 3-5 skills that are in-demand according to the market research but are MISSING from the candidate's resume.
    4.  **Actionable Advice:** For each missing skill, provide a concrete suggestion on how the candidate can learn it (e.g., "Take a course on Coursera for 'Advanced SQL'").
    """

    print("🧠 Performing gap analysis...")
    response = analyst_llm.complete(prompt)
    state.gap_analysis = str(response)

    print("✅ Analyst finished. Gap analysis complete.")
    return state


# --- Agent 4: The Synthesizer (using DeepSeek) ---
# This agent takes the technical analysis and writes a user-friendly final report.

def synthesize_report_agent(state: AnalysisState) -> str:
    """
    Synthesizes all the information into a polished, user-friendly report.
    Uses DeepSeek for its high-quality, natural language generation.
    """
    print("\n🤖 Running Agent 4: The Synthesizer (Model: DeepSeek)")
    if not state.gap_analysis or not state.structured_resume:
        raise ValueError("Cannot synthesize report without a gap analysis.")

    # Initialize the LLM for this agent
    synthesizer_llm = OpenRouter(
        model="deepseek/deepseek-chat",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0.5,
    )

    candidate_name = state.structured_resume.full_name
    prompt = f"""
    You are a friendly and encouraging career coach. Your task is to write a final, polished report for a candidate named {candidate_name}.
    You will be given a technical gap analysis. Rewrite it into a personalized, easy-to-read, and motivational report.

    Address the candidate directly by their name. Use clear headings, bullet points, and a supportive tone.
    Do NOT just copy the input; rephrase it to be more conversational.

    **Technical Analysis to Synthesize:**
    ```markdown
    {state.gap_analysis}
    ```

    Now, please write the final, beautiful report for {candidate_name}.
    """

    print("✍️ Writing final report...")
    final_report = synthesizer_llm.complete(prompt)

    print("✅ Synthesizer finished. Report is ready.")
    return str(final_report)
