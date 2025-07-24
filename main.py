import os

from dotenv import load_dotenv

from core.workflow import run_multi_agent_workflow


def main():
    # Load environment variables from .env file
    load_dotenv()
    if not os.getenv("OPENROUTER_API_KEY") or not os.getenv("TAVILY_API_KEY"):
        print("🚨 ERROR: API keys for OpenRouter and Tavily must be set in .env file.")
        return

    resume_path = "data/resumes/sample_resume.pdf"  # IMPORTANT: Add your resume file here

    if not os.path.exists(resume_path):
        print(f"🚨 ERROR: Resume file not found at '{resume_path}'.")
        print("Please add a PDF resume to the 'data/resumes/' directory.")
        return

    print(f"🚀 Starting Multi-Agent Resume Analysis for: {resume_path}\n")
    final_report = run_multi_agent_workflow(resume_path)

    print("\n\n--- ✅ FINAL REPORT ---")
    print("--------------------------------------------------")
    print(final_report)
    print("--------------------------------------------------")


if __name__ == "__main__":
    main()
