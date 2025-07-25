import datetime as dt
import re
from typing import List, Optional

import dateparser
import langdetect
import pdfplumber
import pymupdf as fitz
import pytesseract
from PIL import Image
from dateparser.conf import settings as dateparser_settings


# ------------------------ File Type Detection ------------------------ #

def is_image_file(filename: str) -> bool:
    return filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))


def is_pdf_file(filename: str) -> bool:
    return filename.lower().endswith('.pdf')


# ------------------------ Image & PDF Text Extraction ------------------------ #

def extract_text_from_image(image_path: str) -> str:
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text.strip()


def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    # If no text was extracted using pdfplumber, fallback to OCR
    if not text.strip():
        print("⚠️ No text found in PDF — using OCR fallback")
        text = extract_text_from_scanned_pdf(pdf_path)

    return text.strip()


def extract_text_from_scanned_pdf(pdf_path: str) -> str:
    """Converts PDF pages to images and applies OCR (Tesseract)."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            pix = page.get_pixmap(dpi=300)
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            text += pytesseract.image_to_string(img) + "\n"
    return text


# ------------------------ Date Normalization ------------------------ #

def normalise_dates(raw: Optional[str]) -> Optional[dt.date]:
    """
    Normalize raw date strings into ISO-format date objects.
    Returns None if parsing fails or input is invalid.
    """
    if not raw or raw.lower() in {"none", "null", "nan"}:
        return None

    dateparser_settings.PREFER_DAY_OF_MONTH = "first"
    parsed = dateparser.parse(raw, settings=dateparser_settings)
    return parsed.date() if parsed else None


# ------------------------ Email Extraction ------------------------ #

def extract_emails(text: str) -> List[str]:
    """
    Extract all email addresses from raw text.
    """
    return re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text)


# ------------------------ URL Extraction ------------------------ #

def extract_urls(text: str) -> List[str]:
    """
    Extract all URLs from raw text.
    """
    return re.findall(r"(https?://\S+)", text)


# ------------------------ Language Detection ------------------------ #

def detect_language(text: str) -> str:
    """
    Detect the language of the given text.
    Returns ISO 639-1 language code (e.g., 'en', 'fr').
    """
    try:
        return langdetect.detect(text)
    except Exception:
        return "unknown"
