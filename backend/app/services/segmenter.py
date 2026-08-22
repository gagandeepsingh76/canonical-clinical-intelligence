import re
from typing import List, Optional
from app.models.schemas import PageData, LogicalDocument

class DocumentSegmenterService:
    @staticmethod
    def _extract_page_metadata(page: PageData) -> dict:
        text = page.cleaned_text
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        
        facility = None
        provider = None
        service_date = None
        title = None
        
        # 1. Extract canonical title keyword from early lines (first 10 lines)
        header_text = "\n".join(lines[:10]) if lines else text
        title_patterns = [
            r"(AMBULANCE RUN REPORT|EMS REPORT)",
            r"(EMERGENCY DEPARTMENT RECORD|ED RECORD)",
            r"(EMERGENCY PHYSICIAN NOTE|PHYSICIAN NOTE|OFFICE VISIT NOTE)",
            r"(RADIOLOGY REPORT|DIAGNOSTIC IMAGING|MRI|CT|X-RAY)",
            r"(DISCHARGE SUMMARY|HOSPITAL DISCHARGE)",
            r"(PRIMARY CARE NOTE|OFFICE VISIT NOTE - PRIMARY CARE)",
            r"(PHYSICAL THERAPY INITIAL EVALUATION|PHYSICAL THERAPY EVALUATION)",
            r"(PHYSICAL THERAPY PROGRESS NOTE|DAILY PT NOTE)",
            r"(ORTHOPEDIC SPINE CONSULTATION|ORTHOPEDIC CONSULTATION)",
            r"(OPERATIVE REPORT|PROCEDURE NOTE)",
            r"(ELECTROMYOGRAPHY AND NERVE CONDUCTION STUDY|EMG REPORT)",
            r"(HISTORICAL MEDICAL RECORD|PAST MEDICAL RECORDS)",
            r"(MEDICATION RECORD|PHARMACY DISPENSING RECORD)",
            r"(BILLING STATEMENT|ITEMIZED BILLING RECORD)",
            r"(EMPLOYER WORK STATUS|WORK CAPACITY CERTIFICATE)",
            r"(RECORDS CERTIFICATION|CERTIFICATE OF CUSTODIAN OF RECORDS)"
        ]

        for t_pat in title_patterns:
            tm = re.search(t_pat, header_text, re.IGNORECASE)
            if tm:
                title = tm.group(1).strip().title()
                break

        if not title:
            title = page.predicted_document_type.replace("_", " ").title()

        # 2. Generalized Facility Extraction
        fac_match = re.search(
            r"([A-Z0-9\s\,\.\-&']+(?:HOSPITAL|EMERGENCY MEDICAL SERVICES|MEDICAL CENTER|HEALTH SYSTEM|HEALTHCARE|CLINIC|ORTHOPEDIC|REHABILITATION|INSTITUTE|URGENT CARE|PHARMACY|ASSOCIATES|SERVICES|CUSTODIAN|LOGISTICS GROUP))",
            text,
            re.IGNORECASE
        )
        if fac_match:
            facility = fac_match.group(1).strip()

        # 3. Generalized Provider Extraction
        prov_match = re.search(
            r"(?:Attending|Provider|Surgeon|Therapist|Proceduralist|Electromyographer|Prepared by|Certified by|Reported by|Physician)\s*[:\s]*([A-Z][A-Za-z\s\.\,\-]+?)(?:\n|\||Date|DOB|MRN|$)",
            text,
            re.IGNORECASE
        )
        if prov_match:
            provider = prov_match.group(1).strip()
            provider = re.sub(r"[\s\,]+$", "", provider)

        # 4. Clinical Service Date Extraction (Ignoring Line 2 watermark dates)
        body_text = "\n".join(lines[3:]) if len(lines) > 3 else text
        
        clinical_date_pats = [
            r"Date of Service\s*[:\s]*(\d{2}/\d{2}/\d{4})",
            r"Incident Date(?:\s*/\s*Time)?\s*[:\s]*(\d{2}/\d{2}/\d{4})",
            r"Arrival\s*[:\s]*(\d{2}/\d{2}/\d{4})",
            r"Date of Evaluation\s*[:\s]*(\d{2}/\d{2}/\d{4})",
            r"Date of Exam\s*[:\s]*(\d{2}/\d{2}/\d{4})",
            r"Date of Procedure\s*[:\s]*(\d{2}/\d{2}/\d{4})",
            r"Date of Study\s*[:\s]*(\d{2}/\d{2}/\d{4})",
            r"Date of Surgery\s*[:\s]*(\d{2}/\d{2}/\d{4})",
            r"Date of Discharge\s*[:\s]*(\d{2}/\d{2}/\d{4})",
            r"Discharge Date(?:\s*/\s*Time)?\s*[:\s]*(\d{2}/\d{2}/\d{4})",
            r"VISIT 1\s*-\s*(\d{2}/\d{2}/\d{4})",
            r"Date of Hire\s*[:\s]*(\d{2}/\d{2}/\d{4})",
            r"Statement Period\s*[:\s]*(\d{2}/\d{2}/\d{4})",
            r"Date of Production\s*[:\s]*(\d{2}/\d{2}/\d{4})"
        ]

        for cd_pat in clinical_date_pats:
            cd_m = re.search(cd_pat, body_text, re.IGNORECASE)
            if cd_m:
                service_date = cd_m.group(1)
                break

        if not service_date:
            any_date = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", body_text)
            if any_date:
                service_date = any_date.group(1)

        # 5. Generalized Historical Flag
        is_historical = bool(re.search(r"\b(?:historical record|prior records|subpoena|years? prior)\b", text, re.IGNORECASE))

        # 6. Generalized Per-Page Patient Name
        pat_match = re.search(r"(?:Patient Name|Patient|Employee)\s*[:\s]*([A-Z][a-z]+,\s*[A-Z][a-z]+)", text)
        page_patient_name = pat_match.group(1).strip() if pat_match else None

        return {
            "title": title,
            "facility": facility,
            "provider": provider,
            "service_date": service_date,
            "is_historical": is_historical,
            "patient_name": page_patient_name
        }

    @classmethod
    def segment_documents(cls, pages: List[PageData]) -> List[LogicalDocument]:
        if not pages:
            return []

        documents: List[LogicalDocument] = []
        current_pages: List[PageData] = []
        current_meta = None
        doc_count = 1

        for i, page in enumerate(pages):
            meta = cls._extract_page_metadata(page)
            
            is_boundary = False
            if not current_pages:
                is_boundary = True
            elif page.is_duplicate:
                is_boundary = True
            elif current_pages[-1].is_duplicate:
                is_boundary = True
            elif meta["is_historical"] != current_meta["is_historical"]:
                is_boundary = True
            elif page.predicted_document_type != current_pages[-1].predicted_document_type:
                is_boundary = True
            elif meta["patient_name"] and current_meta["patient_name"] and meta["patient_name"].lower() != current_meta["patient_name"].lower():
                is_boundary = True
            elif meta["facility"] and current_meta["facility"] and meta["facility"].lower() != current_meta["facility"].lower():
                is_boundary = True
            elif meta["service_date"] and current_meta["service_date"] and meta["service_date"] != current_meta["service_date"]:
                is_boundary = True
            else:
                if meta["title"] and current_meta["title"] and meta["title"].lower() != current_meta["title"].lower():
                    is_boundary = True

            if is_boundary and current_pages:
                start_p = current_pages[0].page_number
                end_p = current_pages[-1].page_number
                doc_id = f"doc_{doc_count:03d}"
                doc_type = current_pages[0].predicted_document_type
                avg_conf = sum(p.classification_confidence for p in current_pages) / len(current_pages)
                raw_combined = "\n\n--- PAGE BREAK ---\n\n".join(p.cleaned_text for p in current_pages)
                
                documents.append(
                    LogicalDocument(
                        document_id=doc_id,
                        document_type=doc_type,
                        title=current_meta["title"] or doc_type.replace("_", " ").title(),
                        facility_name=current_meta["facility"],
                        provider_name=current_meta["provider"],
                        service_date=current_meta["service_date"],
                        start_page=start_p,
                        end_page=end_p,
                        page_count=len(current_pages),
                        page_numbers=[p.page_number for p in current_pages],
                        classification_confidence=round(avg_conf, 3),
                        is_historical=current_meta["is_historical"],
                        is_conflicting_patient=False,
                        raw_text=raw_combined
                    )
                )
                doc_count += 1
                current_pages = [page]
                current_meta = meta
            else:
                current_pages.append(page)
                if current_meta is None:
                    current_meta = meta

        # Flush final document
        if current_pages:
            start_p = current_pages[0].page_number
            end_p = current_pages[-1].page_number
            doc_id = f"doc_{doc_count:03d}"
            doc_type = current_pages[0].predicted_document_type
            avg_conf = sum(p.classification_confidence for p in current_pages) / len(current_pages)
            raw_combined = "\n\n--- PAGE BREAK ---\n\n".join(p.cleaned_text for p in current_pages)
            
            documents.append(
                LogicalDocument(
                    document_id=doc_id,
                    document_type=doc_type,
                    title=current_meta["title"] or doc_type.replace("_", " ").title(),
                    facility_name=current_meta["facility"],
                    provider_name=current_meta["provider"],
                    service_date=current_meta["service_date"],
                    start_page=start_p,
                    end_page=end_p,
                    page_count=len(current_pages),
                    page_numbers=[p.page_number for p in current_pages],
                    classification_confidence=round(avg_conf, 3),
                    is_historical=current_meta["is_historical"],
                    is_conflicting_patient=False,
                    raw_text=raw_combined
                )
            )

        return documents
