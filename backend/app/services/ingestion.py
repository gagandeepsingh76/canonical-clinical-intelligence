import re
import hashlib
from typing import List, Tuple
import pymupdf
from app.models.schemas import PageData, PageLayoutFeatures

class PDFIngestionService:
    @staticmethod
    def extract_pdf(pdf_path: str) -> List[PageData]:
        doc = pymupdf.open(pdf_path)
        pages_data = []

        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_num = page_idx + 1
            raw_text = page.get_text()
            
            # Extract basic layout features
            rect = page.rect
            width = float(rect.width)
            height = float(rect.height)
            
            blocks = page.get_text("blocks")
            num_blocks = len(blocks)
            
            lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
            num_lines = len(lines)
            
            # Clean text
            cleaned_text = re.sub(r"[ \t]+", " ", raw_text).strip()
            text_density = len(cleaned_text) / (width * height) if (width * height) > 0 else 0.0
            
            # Header and Footer heuristics
            header = None
            footer = None
            if len(lines) >= 2:
                header = " | ".join(lines[:3])
                footer = " | ".join(lines[-2:])
                
            # Layout heuristics
            has_signature_line = any(
                keyword in raw_text.lower() 
                for keyword in ["electronically signed", "signature", "signed by", "reported by", "certified by", "therapist"]
            )
            has_header_bar = bool(re.search(r"claim\s*pi|dob\s*\d{2}/\d{2}/\d{4}|produced\s*\d{2}/\d{2}/\d{4}", raw_text, re.IGNORECASE))
            has_table_structure = any(
                keyword in raw_text.lower()
                for keyword in ["statement period", "itemized charges", "accession", "dos", "cpt", "amount", "balance"]
            )
            
            layout_features = PageLayoutFeatures(
                width=width,
                height=height,
                num_blocks=num_blocks,
                num_lines=num_lines,
                has_header_bar=has_header_bar,
                has_signature_line=has_signature_line,
                has_table_structure=has_table_structure,
                text_density=text_density
            )
            
            # Hash for duplicate detection (normalized)
            norm_content = re.sub(r"\s+", "", cleaned_text.lower())
            page_hash = hashlib.sha256(norm_content.encode("utf-8")).hexdigest()
            
            is_blank = len(cleaned_text) < 30
            
            pages_data.append(
                PageData(
                    page_number=page_num,
                    raw_text=raw_text,
                    cleaned_text=cleaned_text,
                    header=header,
                    footer=footer,
                    layout_features=layout_features,
                    text_density=text_density,
                    page_hash=page_hash,
                    is_blank=is_blank
                )
            )

        return pages_data
