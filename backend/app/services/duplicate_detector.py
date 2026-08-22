import re
from difflib import SequenceMatcher
from typing import List, Dict
from app.models.schemas import PageData

try:
    from rapidfuzz import fuzz
    USE_RAPIDFUZZ = True
except ImportError:
    USE_RAPIDFUZZ = False

class DuplicateDetectorService:
    @staticmethod
    def _extract_visit_key(text: str) -> str:
        # Check for facility + date of service + visit / session number (using horizontal whitespace for facility name)
        dos_match = re.search(r"Date of Service\s*[:\s]*(\d{2}/\d{2}/\d{4})", text, re.IGNORECASE)
        visit_match = re.search(r"(?:Visit Number|Session|Visit)\s*[:\s]*(\d+)", text, re.IGNORECASE)
        fac_match = re.search(
            r"([A-Z0-9\t \.\-&']+(?:REHABILITATION|HOSPITAL|PHYSICAL THERAPY|ASSOCIATES|INSTITUTE|CENTER|CLINIC|HEALTH SYSTEM))",
            text,
            re.IGNORECASE
        )

        dos = dos_match.group(1) if dos_match else ""
        visit = visit_match.group(1) if visit_match else ""
        fac = fac_match.group(1).strip().upper() if fac_match else ""

        if dos and visit and fac:
            return f"{fac}_{dos}_visit_{visit}"
        return ""

    @staticmethod
    def _calculate_similarity(text1: str, text2: str) -> float:
        # Strip generic production stamps / headers for comparison
        clean1 = re.sub(r"^.*?PRODUCED\s*\d{2}/\d{2}/\d{4}", "", text1, flags=re.IGNORECASE | re.DOTALL)
        clean2 = re.sub(r"^.*?PRODUCED\s*\d{2}/\d{2}/\d{4}", "", text2, flags=re.IGNORECASE | re.DOTALL)
        clean1 = re.sub(r"\s+", " ", clean1).strip().lower()
        clean2 = re.sub(r"\s+", " ", clean2).strip().lower()
        
        if not clean1 or not clean2:
            return 0.0
            
        if USE_RAPIDFUZZ:
            return fuzz.ratio(clean1, clean2) / 100.0
        return SequenceMatcher(None, clean1, clean2).ratio()

    @classmethod
    def detect_duplicates(cls, pages: List[PageData], similarity_threshold: float = 0.85) -> List[PageData]:
        seen_hashes = {}
        seen_visit_keys: Dict[str, int] = {}

        for i, page in enumerate(pages):
            if page.is_blank:
                continue

            # 1. Exact hash check
            if page.page_hash in seen_hashes:
                orig_page = seen_hashes[page.page_hash]
                page.is_duplicate = True
                page.duplicate_of = orig_page
                page.duplicate_similarity = 1.0
                continue
            else:
                seen_hashes[page.page_hash] = page.page_number

            # 2. Visit Key / Duplicate Draft collision check
            visit_key = cls._extract_visit_key(page.cleaned_text)
            if visit_key:
                if visit_key in seen_visit_keys:
                    orig_page = seen_visit_keys[visit_key]
                    page.is_duplicate = True
                    page.duplicate_of = orig_page
                    page.duplicate_similarity = 0.95
                    continue
                else:
                    seen_visit_keys[visit_key] = page.page_number

            # 3. Near-duplicate text similarity check against prior pages
            for prev_idx in range(i):
                prev_page = pages[prev_idx]
                if prev_page.is_blank:
                    continue
                
                if page.predicted_document_type == prev_page.predicted_document_type:
                    sim = cls._calculate_similarity(page.cleaned_text, prev_page.cleaned_text)
                    if sim >= similarity_threshold:
                        page.is_duplicate = True
                        page.duplicate_of = prev_page.page_number
                        page.duplicate_similarity = round(sim, 3)
                        break

        return pages
