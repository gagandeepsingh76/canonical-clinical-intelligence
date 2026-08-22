# FAILURES.md — Engineering Failure Analysis & Learnings

This document records the specific architectural and edge-case failure modes encountered during the development and final independent audit of the **Canonical Medical Record Structuring Pipeline**, how they were detected through rigorous testing, and the precise solutions implemented.

---

## 1. Demographic Hardcoding & Multiline Cross-Line Regex Bleed

### The Failure
During audit inspection, `extractor.py` had static demographic fallbacks (`Marcus Whitfield`, `1987-03-14`, `555-019-4821`). When refactored to generic regex parsing, a pattern `(?:Patient Name|Patient)\s*[:\s]*([A-Z][a-z]+,\s*[A-Z][a-z]+(?:\s+[A-Z]\.?)?)` caused `\s+` to cross over the newline `\n` into the next line `DOB: 05/12/1992`, matching `Sarah D` as the middle initial.

### Root Cause
In Python regular expressions, `\s` matches whitespace characters including `\n` and `\r`. When `DOB:` immediately followed the patient name on the next line, `\s+` traversed across lines and captured the first letter of `DOB` as an initial.

### Detection & Test
Caught during the Phase 3 Generalization Audit test (`backend/tests/test_generalization.py::test_generalization_on_arbitrary_record`) with synthetic patient records (`Jenkins, Sarah`).

### Resolution
Updated the regex in `extractor.py` and `conflict_resolver.py` to use boundary-delimited horizontal whitespace matching `r"(?:Patient Name|Patient|Employee Name|Employee)\s*[:\s]*([A-Z][A-Za-z\-]+,\s*[A-Z][A-Za-z\-]+(?:\s+[A-Z]\b\.?)?)"` and dynamic multi-document consensus voting.

---

## 2. Claim Number / Production Header Collision over Clinical MRN

### The Failure
When extracting patient MRN dynamically, `mrn_match` captured `PI-2024-8871` (the legal claim identifier from line 2 of the production stamp) instead of the actual clinical hospital Medical Record Number `PCG-4471902`.

### Root Cause
The production watermark `CLAIM PI-2024-8871` appeared before the clinical body text, and a generic regex matching `(?:MRN|Claim)` grabbed the first instance on every page.

### Detection & Test
Caught by `backend/tests/test_extractor.py::test_entity_extractor` asserting canonical MRN extraction.

### Resolution
Updated the regex to prioritize `\bMRN\s*[:\s#]*([A-Za-z0-9\-]+)` before secondary identifiers (`Account`, `Member`), successfully extracting `PCG-4471902`.

---

## 3. Production Watermark Collision on Service Date Extraction

### The Failure
During initial document segmentation and encounter date extraction, encounters were incorrectly assigned the date `01/22/2025`.

### Root Cause
Every page of the legal/medical production PDF contains a production header stamp on line 2: `PRODUCED 01/22/2025`. The initial regex scanner checked for `Produced \d{2}/\d{2}/\d{4}` before clinical service date keywords, causing the watermark date to overwrite true clinical encounter dates.

### Detection & Test
Caught by automated test `backend/tests/test_queries.py::test_all_clinical_queries`, which asserted that the initial MVC encounter date `02/11/2024` was present in the longitudinal timeline.

### Resolution
Updated `DocumentSegmenterService._extract_page_metadata` to exclude header line 2 production watermarks and prioritize clinical service date keywords (`Date of Service`, `Incident Date`, `Arrival`, `Date of Evaluation`, `Date of Surgery`, `Date of Exam`, etc.) in the document body.

---

## 4. Title Keyword Overreach in Multi-Page Document Grouping

### The Failure
When segmenting multi-page continuous documents (such as multi-page operative notes), pages were being split into distinct 1-page documents if different sections had slight body variations.

### Root Cause
The segmenter was treating the entire candidate line (up to 100 characters) as the document title string, so `Part 1: Incision` and `Part 2: Closure` produced non-identical titles.

### Resolution
Updated `DocumentSegmenterService` to match canonical title keywords (`OPERATIVE REPORT`, `DISCHARGE SUMMARY`, `PHYSICIAN NOTE`, etc.) rather than free-form text lines, allowing continuous multi-page documents to merge seamlessly.

---

## 5. HL7 FHIR R4 Identifier Regex Pattern Violations

### The Failure
Initial FHIR resource construction produced Pydantic validation errors:
`String should match pattern '^[A-Za-z0-9\-.]+$' [input_value='pat_001']`
resulting in a 0.0% validation pass rate.

### Root Cause
Internal database primary keys used underscore conventions (`pat_001`, `enc_001`, `cond_001`), whereas the HL7 FHIR R4/R5 specification strictly forbids underscores in resource `id` fields.

### Resolution
Implemented `FHIRBuilderService._clean_id()` which converts all internal IDs into compliant dash-separated strings (`pat-001`, `enc-001`, `cond-001`, `obs-001`), achieving a 100.0% validation pass rate.

---

## 6. Static HTML Placeholders in UI

### The Failure
Initial UI inspection revealed that before the API response was received, `index.html` contained static placeholder numbers (`22 pages`, `15 sub-documents`, `Marcus Whitfield`).

### Resolution
Removed all static demonstration placeholders from `frontend/index.html` and replaced them with dynamic loading indicators (`-`) that populate exclusively from live API responses.
