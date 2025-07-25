# tools/text_tools.py

from core.utils import (
    extract_text_from_image,
    extract_text_from_pdf,
    is_image_file,
    is_pdf_file,
)


class ResumeTextExtractorTool:
    def name(self) -> str:
        return "extract_resume_text"

    def description(self) -> str:
        return "Extract text from a resume file (PDF or image)."

    def run(self, file_path: str) -> str:
        if is_image_file(file_path):
            return extract_text_from_image(file_path)
        elif is_pdf_file(file_path):
            return extract_text_from_pdf(file_path)
        else:
            return "Unsupported file type."
