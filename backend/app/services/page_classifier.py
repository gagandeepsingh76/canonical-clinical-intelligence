import re
from typing import Tuple, List
from app.models.schemas import PageData

class PageClassifierService:
    @classmethod
    def classify_page(cls, page: PageData) -> Tuple[str, float, List[str]]:
        if page.is_blank:
            return "BLANK", 1.0, ["Empty page detected"]
        
        text = page.cleaned_text
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        
        # Candidate header lines: first 15 lines, filtering out production watermark lines
        header_lines = []
        for l in lines[:15]:
            l_up = l.upper()
            if "PRODUCED " in l_up and "CLAIM " in l_up:
                continue
            header_lines.append(l_up)

        header_block = " ".join(header_lines)
        full_text_lower = text.lower()

        # 1. Check direct Header Block / Document Title matches
        if any("AMBULANCE RUN REPORT" in hl or "PREHOSPITAL CARE REPORT" in hl or "EMS REPORT" in hl for hl in header_lines):
            return "EMS_REPORT", 0.99, ["Ambulance / Prehospital Care Report title match"]

        if any("EMERGENCY DEPARTMENT TRIAGE" in hl or "TRIAGE & NURSING RECORD" in hl or "EMERGENCY DEPARTMENT RECORD" in hl for hl in header_lines):
            return "EMERGENCY_DEPARTMENT_RECORD", 0.99, ["ED Triage & Nursing Record title match"]

        if any("EMERGENCY PHYSICIAN NOTE" in hl for hl in header_lines):
            return "PHYSICIAN_NOTE", 0.99, ["Emergency Physician Note title match"]

        if any("DIAGNOSTIC IMAGING REPORTS" in hl or "MRI LUMBAR SPINE" in hl or "CT CERVICAL SPINE" in hl or "LUMBAR SPINE RADIOGRAPHS" in hl for hl in header_lines):
            return "RADIOLOGY_REPORT", 0.99, ["Diagnostic Imaging / Radiology title match"]

        if any("ED DISCHARGE SUMMARY" in hl or "DISCHARGE SUMMARY & PRESCRIPTION RECORD" in hl or "DISCHARGE SUMMARY" in hl for hl in header_lines):
            return "DISCHARGE_SUMMARY", 0.99, ["Discharge Summary title match"]

        if any("OFFICE VISIT NOTE - PRIMARY CARE" in hl or "PRIMARY CARE" in hl for hl in header_lines):
            return "PRIMARY_CARE_NOTE", 0.99, ["Primary Care Office Visit title match"]

        if any("PHYSICAL THERAPY INITIAL EVALUATION" in hl or "PHYSICAL THERAPY EVALUATION" in hl for hl in header_lines):
            return "PHYSICAL_THERAPY_EVALUATION", 0.99, ["Physical Therapy Initial Evaluation title match"]

        if any("PHYSICAL THERAPY PROGRESS NOTE" in hl for hl in header_lines):
            return "PHYSICAL_THERAPY_PROGRESS_NOTE", 0.99, ["Physical Therapy Progress Note title match"]

        if any("PROCEDURE NOTE - TRANSFORAMINAL" in hl or "PROCEDURE NOTE" in hl for hl in header_lines):
            return "OPERATIVE_REPORT", 0.99, ["Procedure Note / Interventional Injection title match"]

        if any("OPERATIVE REPORT" in hl for hl in header_lines):
            return "OPERATIVE_REPORT", 0.99, ["Department of Surgery Operative Report title match"]

        if any("ORTHOPEDIC SPINE CONSULTATION" in hl or "ORTHOPEDIC FOLLOW-UP VISIT" in hl or "ORTHOPEDIC CONSULTATION" in hl for hl in header_lines):
            return "ORTHOPEDIC_SPINE_CONSULTATION", 0.99, ["Orthopedic Spine Consultation title match"]

        if any("EMG / NERVE CONDUCTION STUDY REPORT" in hl or "ELECTROMYOGRAPHY AND NERVE CONDUCTION" in hl for hl in header_lines):
            return "RADIOLOGY_REPORT", 0.98, ["EMG / NCS Diagnostic Study title match"]

        if any("PHYSICAL THERAPY DISCHARGE SUMMARY" in hl for hl in header_lines):
            return "DISCHARGE_SUMMARY", 0.98, ["Physical Therapy Discharge Summary title match"]

        if any("POST-OPERATIVE OFFICE VISIT NOTES" in hl or "POST-OPERATIVE FOLLOW-UP" in hl for hl in header_lines):
            return "PHYSICIAN_NOTE", 0.98, ["Post-Operative Office Visit Notes title match"]

        if any("URGENT CARE VISIT NOTE (HISTORICAL RECORD)" in hl or "PRIOR RECORDS OBTAINED BY SUBPOENA" in hl or "HISTORICAL MEDICAL RECORD" in hl for hl in header_lines):
            return "HISTORICAL_MEDICAL_RECORD", 0.99, ["Historical Subpoenaed Urgent Care Record match"]

        if any("PHARMACY DISPENSING RECORD" in hl or "PATIENT MEDICATION HISTORY" in hl or "MEDICATION RECORD" in hl for hl in header_lines):
            return "MEDICATION_RECORD", 0.99, ["Pharmacy Dispensing Record title match"]

        if any("ITEMIZED BILLING SUMMARY" in hl or "STATEMENT OF CHARGES" in hl or "BILLING RECORD" in hl for hl in header_lines):
            return "BILLING_RECORD", 0.99, ["Itemized Billing Summary title match"]

        if any("EMPLOYER WORK STATUS AND WAGE RECORD" in hl or "OCCUPATIONAL HEALTH & WORK STATUS" in hl or "EMPLOYER WORK STATUS" in hl for hl in header_lines):
            return "EMPLOYER_WORK_STATUS", 0.99, ["Employer Work Status and Wage Record title match"]

        if any("RECORDS PRODUCTION CERTIFICATION" in hl or "CERTIFICATION AND PRODUCTION LOG" in hl or "RECORDS CERTIFICATION" in hl for hl in header_lines):
            return "RECORDS_CERTIFICATION", 0.99, ["Records Custodian Certification title match"]

        # Fallback keyword scanning
        if "prehospital care" in full_text_lower or "ambulance" in full_text_lower:
            return "EMS_REPORT", 0.85, ["Prehospital care keywords"]
        if "itemized charges" in full_text_lower or "balance due" in full_text_lower:
            return "BILLING_RECORD", 0.85, ["Billing charges keywords"]
        if "dispensing history" in full_text_lower:
            return "MEDICATION_RECORD", 0.85, ["Pharmacy dispensing keywords"]

        return "UNKNOWN", 0.30, ["No specific clinical header matched"]
