"""
Script to generate a 32-page structured synthetic medical record PDF for 30+ page compliance testing.
Labeled clearly as: SYNTHETIC TEST DATA — NOT A REAL PATIENT RECORD.
"""
import fitz  # PyMuPDF
from pathlib import Path

def generate_30plus_compliance_pdf(output_path: str):
    doc = fitz.open()

    pages_data = [
        # Page 1: EMS
        {
            "header": "METRO WEST EMERGENCY MEDICAL SERVICES | PREHOSPITAL CARE REPORT",
            "title": "AMBULANCE RUN REPORT",
            "facility": "METRO WEST EMERGENCY MEDICAL SERVICES",
            "date": "Date of Service: 01/10/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
DISPATCH & INCIDENT:
Unit Medic 4 dispatched Priority 1 to collision on Highway 101. Restrained driver in rear-end collision. Airbags deployed.
Patient self-extricated prior to EMS arrival. Complaining of severe neck pain, right lumbar back pain radiating into right leg.
VITAL SIGNS:
BP: 128/82 mmHg | HR: 84 bpm | RR: 16 | SpO2: 99% on room air | Pain Score: 8/10
PHYSICAL ASSESSMENT:
Cervical spine: Tenderness along lower cervical paraspinals. Full sensation intact.
Lumbar spine: Moderate paraspinal spasm. Pain radiates down right buttock into posterolateral calf.
INTERVENTIONS:
Cervical collar applied. IV normal saline 500 mL initiated TKO. Transported to St. Jude Memorial Hospital Emergency Department.
Attending Paramedic: J. Reynolds, NRP
            """
        },
        # Page 2: ED Triage
        {
            "header": "ST. JUDE MEMORIAL HOSPITAL | EMERGENCY DEPARTMENT",
            "title": "EMERGENCY DEPARTMENT TRIAGE & NURSING RECORD",
            "facility": "ST. JUDE MEMORIAL HOSPITAL",
            "date": "Arrival: 01/10/2023 09:15",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
CHIEF COMPLAINT:
Motor vehicle collision, neck pain, severe low back pain radiating to right lower extremity.
TRIAGE VITALS:
BP: 132/84 mmHg | Pulse: 80 bpm | Resp: 18 | SpO2: 98% | Pain Level: 8/10
ALLERGIES ON FILE:
Sulfa drugs (hives, severe itching) ; NKDA otherwise
NURSING ASSESSMENT & MEDS ADMINISTERED:
Patient awake, alert, oriented x4. GCS 15. Neck in C-collar.
09:30 - Ketorolac (Toradol) 30 mg IV x1 given for acute pain.
09:45 - Methocarbamol 1000 mg IV x1 administered for severe lumbar muscle spasm.
Triage Nurse: C. Henderson, RN
            """
        },
        # Page 3: ED Physician
        {
            "header": "ST. JUDE MEMORIAL HOSPITAL | DEPARTMENT OF EMERGENCY MEDICINE",
            "title": "EMERGENCY PHYSICIAN NOTE",
            "facility": "ST. JUDE MEMORIAL HOSPITAL",
            "date": "Date of Service: 01/10/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
HISTORY OF PRESENT ILLNESS:
37-year-old female presents after motor vehicle collision. Restrained driver. Reports acute neck stiffness and sharp lower back pain with right leg radicular pain.
PHYSICAL EXAMINATION:
Neck: Paraspinal muscle tenderness. No bony step-off. Range of motion limited by pain.
Lumbar Spine: Marked tenderness L4-L5 paraspinal region.
Neurological: Sensation diminished right L5 dermatome. Straight Leg Raise Test (Right): Positive at 35 degrees. Right EHL strength 4/5. Left lower extremity 5/5.
DIAGNOSES:
1. Acute cervical strain
2. Acute right lumbar radiculopathy
3. Lumbosacral strain
Emergency Physician: Robert Alvarez, MD
            """
        },
        # Page 4: ED Radiology
        {
            "header": "ST. JUDE MEMORIAL HOSPITAL | DEPARTMENT OF RADIOLOGY",
            "title": "DIAGNOSTIC IMAGING REPORTS - CT CERVICAL SPINE",
            "facility": "ST. JUDE MEMORIAL HOSPITAL",
            "date": "Date of Exam: 01/10/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
EXAMINATION: CT CERVICAL SPINE WITHOUT CONTRAST
INDICATION: Motor vehicle collision, acute neck pain.
FINDINGS:
Cervical vertebral alignment is normal. No acute fracture or traumatic subluxation identified.
Disc spaces are well-preserved. Prevertebral soft tissues are unremarkable.
IMPRESSION:
1. No acute cervical spine fracture or dislocation.
2. Moderate cervical paraspinal soft tissue strain.
Radiologist: Brenda Foster, MD
            """
        },
        # Page 5: ED Discharge
        {
            "header": "ST. JUDE MEMORIAL HOSPITAL | EMERGENCY DEPARTMENT",
            "title": "ED DISCHARGE SUMMARY & PRESCRIPTION RECORD",
            "facility": "ST. JUDE MEMORIAL HOSPITAL",
            "date": "Discharge Date: 01/10/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
DISCHARGE DIAGNOSES:
1. Acute right lumbar radiculopathy
2. Cervical strain
DISCHARGE MEDICATIONS:
- Naproxen 500 mg PO BID with food, #30, no refills
- Methocarbamol 750 mg PO TID PRN muscle spasm, #30, no refills
- Acetaminophen / Codeine #3 300/30 mg, 1 tab PO q6h PRN severe pain, #12
DISCHARGE INSTRUCTIONS:
Follow up with primary care physician in 5-7 days. Outpatient MRI recommended if radiculopathy persists.
Attending Physician: Robert Alvarez, MD
            """
        },
        # Page 6: Primary Care
        {
            "header": "VALLEY FAMILY MEDICINE ASSOCIATES | CLINICAL RECORD",
            "title": "OFFICE VISIT NOTE - PRIMARY CARE",
            "facility": "VALLEY FAMILY MEDICINE ASSOCIATES",
            "date": "Date of Service: 01/18/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
SUBJECTIVE:
8-day post-MVC follow-up. Cervical strain improving with rest and naproxen. Low back pain and right lower extremity radiating pain persist.
Numbness on dorsum of right foot and lateral calf.
OBJECTIVE:
Vitals: BP 120/78 | HR 74 | Pain Score: 7/10
Right SLR test positive at 40 degrees. Right great toe weakness (EHL 4/5).
ASSESSMENT & PLAN:
1. Right lumbar radiculopathy - order MRI Lumbar Spine without contrast.
2. Cervical strain - improving.
3. Start Gabapentin 300 mg PO TID for radicular neuropathic pain.
4. Refer to Physical Therapy 2-3x/week.
Primary Care Physician: Laura Chen, MD
            """
        },
        # Page 7: MRI Lumbar Spine
        {
            "header": "ADVANCED DIAGNOSTIC IMAGING CENTER | RADIOLOGY REPORT",
            "title": "MRI LUMBAR SPINE WITHOUT CONTRAST",
            "facility": "ADVANCED DIAGNOSTIC IMAGING CENTER",
            "date": "Date of Exam: 01/25/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
EXAMINATION: MRI LUMBAR SPINE WITHOUT CONTRAST
TECHNIQUE: Multiplanar multi-echo sagittal and axial T1 and T2 weighted MRI.
FINDINGS:
L1-L2 through L3-L4: Normal disc height and contour. Canal and neural foramina widely patent.
L4-L5: 6 mm right paracentral disc protrusion compressing traversing right L5 nerve root. Mild facet arthropathy.
L5-S1: Mild disc bulge without nerve root impingement.
IMPRESSION:
Herniated nucleus pulposus L4-L5 with right paracentral disc protrusion causing impingement of the descending right L5 nerve root.
Radiologist: Gregory Sterling, MD
            """
        },
        # Page 8: PT Initial Eval
        {
            "header": "PINNACLE PHYSICAL THERAPY & REHABILITATION",
            "title": "PHYSICAL THERAPY INITIAL EVALUATION",
            "facility": "PINNACLE PHYSICAL THERAPY & REHABILITATION",
            "date": "Date of Evaluation: 02/01/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
EVALUATION:
Chief Complaint: Low back pain radiating into right gluteal region, lateral calf, and dorsum of right foot.
Pain Level: Current: 7/10 | Best: 5/10 | Worst: 9/10
Lumbar Flexion: Limited to 40 degrees with acute radicular reproduction.
Straight Leg Raise (Right): Positive at 35 degrees.
Right Extensor Hallucis Longus (EHL) Strength: 4/5.
PLAN OF CARE:
Therapeutic exercise, lumbar traction, core stabilization 2-3 sessions per week for 8 weeks.
Physical Therapist: Marcus Brody, PT, DPT
            """
        },
        # Page 9: PT Visit 4
        {
            "header": "PINNACLE PHYSICAL THERAPY & REHABILITATION",
            "title": "PHYSICAL THERAPY PROGRESS NOTE",
            "facility": "PINNACLE PHYSICAL THERAPY & REHABILITATION",
            "date": "Date of Service: 02/10/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
TREATMENT: Session 4 of 24.
Patient reports constant deep ache in right lower back and shooting pain down right leg.
Pain Score: 7/10 before therapy, 6/10 post-treatment.
Therapeutic exercises: Pelvic tilts, gentle hamstrings stretching, prone press-ups.
Physical Therapist: Marcus Brody, PT, DPT
            """
        },
        # Page 10: PT Visit 8
        {
            "header": "PINNACLE PHYSICAL THERAPY & REHABILITATION",
            "title": "PHYSICAL THERAPY PROGRESS NOTE",
            "facility": "PINNACLE PHYSICAL THERAPY & REHABILITATION",
            "date": "Date of Service: 02/22/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
TREATMENT: Session 8 of 24.
Subjective: Continued severe right leg pain when standing or walking > 5 minutes.
Objective: SLR positive right at 35 degrees. Right EHL weakness 4/5 persists.
Assessment: Minimal functional progression due to persistent nerve root compression.
Physical Therapist: Marcus Brody, PT, DPT
            """
        },
        # Page 11: Orthopedic Consult
        {
            "header": "SIERRA SPINE & ORTHOPEDIC INSTITUTE",
            "title": "ORTHOPEDIC SPINE CONSULTATION",
            "facility": "SIERRA SPINE & ORTHOPEDIC INSTITUTE",
            "date": "Date of Service: 03/01/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
REASON FOR VISIT:
Evaluation of severe right L5 radiculopathy recalcitrant to 6 weeks of conservative therapy and medications.
PHYSICAL EXAMINATION:
Gait: Antalgic on right side.
Neurological: Decreased sensation over right L5 dermatome. Motor strength: Right EHL 4/5. SLR positive on right at 35 degrees.
IMAGING REVIEW:
MRI Lumbar Spine confirms right L4-L5 disc protrusion compressing traversing right L5 nerve root.
RECOMMENDATION:
Recommend fluoroscopically guided Transforaminal Epidural Steroid Injection (TFESI) at right L4-L5.
Orthopedic Spine Surgeon: Arthur Vance, MD
            """
        },
        # Page 12: Injection TFESI
        {
            "header": "SIERRA SPINE INTERVENTIONAL PAIN CENTER",
            "title": "PROCEDURE NOTE - TRANSFORAMINAL EPIDURAL STEROID INJECTION",
            "facility": "SIERRA SPINE INTERVENTIONAL PAIN CENTER",
            "date": "Date of Procedure: 03/15/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
PROCEDURE: Transforaminal Epidural Steroid Injection (Right L4-L5)
PROCEDURALIST: Arthur Vance, MD
MEDICATIONS INJECTED: Dexamethasone 10 mg and Bupivacaine 0.5% (1 mL)
DESCRIPTION:
Under sterile technique and fluoroscopic guidance, a 22-gauge spinal needle was advanced to the right L4-L5 neuroforamen.
Contrast injection confirmed epidural spread without vascular uptake. Medication injected without complication.
Interventional Spine Specialist: Arthur Vance, MD
            """
        },
        # Page 13: PT Visit 12
        {
            "header": "PINNACLE PHYSICAL THERAPY & REHABILITATION",
            "title": "PHYSICAL THERAPY PROGRESS NOTE",
            "facility": "PINNACLE PHYSICAL THERAPY & REHABILITATION",
            "date": "Date of Service: 04/05/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
TREATMENT: Session 12 of 24.
Patient reports transient 40% relief for 10 days post-injection, but radicular pain has returned to 7/10 baseline.
Objective: Right EHL strength 4/5. SLR positive right at 35 degrees.
Physical Therapist: Marcus Brody, PT, DPT
            """
        },
        # Page 14: PT Visit 16 (Signed)
        {
            "header": "PINNACLE PHYSICAL THERAPY & REHABILITATION",
            "title": "PHYSICAL THERAPY PROGRESS NOTE",
            "facility": "PINNACLE PHYSICAL THERAPY & REHABILITATION",
            "date": "Date of Service: 04/20/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
TREATMENT: Session 16 of 24.
Subjective: Patient unable to tolerate progressive lumbar stabilization due to radiating pain.
Objective: Lumbar flexion restricted to 45 degrees. Straight leg raise positive right at 35 degrees.
Assessment: Conservative care plateaued. Referral back to spine surgeon indicated.
Signed Electronically by Marcus Brody, PT, DPT (04/20/2023 16:30)
            """
        },
        # Page 15: PT Visit 16 (Unsigned Draft Duplicate)
        {
            "header": "PINNACLE PHYSICAL THERAPY & REHABILITATION",
            "title": "PHYSICAL THERAPY PROGRESS NOTE",
            "facility": "PINNACLE PHYSICAL THERAPY & REHABILITATION",
            "date": "Date of Service: 04/20/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
TREATMENT: Session 16 of 24.
Subjective: Patient unable to tolerate progressive lumbar stabilization.
Objective: Straight leg raise positive right at 35 degrees.
Therapist: (not signed)
NOTE NOT ELECTRONICALLY SIGNED. Draft status at time of records production.
            """
        },
        # Page 16: Pre-Op Spine Visit
        {
            "header": "SIERRA SPINE & ORTHOPEDIC INSTITUTE",
            "title": "ORTHOPEDIC SPINE CONSULTATION",
            "facility": "SIERRA SPINE & ORTHOPEDIC INSTITUTE",
            "date": "Date of Service: 05/02/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
SUBJECTIVE:
Patient returns for surgical consultation following failure of 16 physical therapy sessions and epidural injection.
Severe right leg pain, persistent weakness in right great toe, and numbness.
OBJECTIVE:
Right EHL strength 4/5. SLR positive on right at 30 degrees.
PLAN:
Proceed with Right L4-L5 Lumbar Microdiscectomy. Obtain EMG / Nerve Conduction Study prior to surgery.
Surgeon: Arthur Vance, MD
            """
        },
        # Page 17: EMG / NCS
        {
            "header": "PACIFIC NEUROLOGICAL & ELECTRODIAGNOSTIC ASSOCIATES",
            "title": "ELECTROMYOGRAPHY AND NERVE CONDUCTION STUDY",
            "facility": "PACIFIC NEUROLOGICAL & ELECTRODIAGNOSTIC ASSOCIATES",
            "date": "Date of Study: 05/18/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
ELECTRODIAGNOSTIC CONSULTATION:
EMG findings reveal fibrillations and positive sharp waves in the right tibialis anterior and right extensor hallucis longus.
Paraspinal mapping confirms active right L5 motor root denervation.
IMPRESSION:
Electrodiagnostic evidence of an active Right L5 radiculopathy.
Electromyographer: David Kessler, MD
            """
        },
        # Page 18: Operative Report Part 1
        {
            "header": "ST. JUDE SURGICAL HOSPITAL | OPERATIVE REPORT",
            "title": "OPERATIVE REPORT",
            "facility": "ST. JUDE SURGICAL HOSPITAL",
            "date": "Date of Surgery: 06/06/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
PREOPERATIVE DIAGNOSIS: Herniated nucleus pulposus L4-L5 with intractable right L5 radiculopathy.
POSTOPERATIVE DIAGNOSIS: Herniated nucleus pulposus L4-L5 with extruded subligamentous disc fragment.
PROCEDURE PERFORMED: Right L4-L5 Lumbar Microdiscectomy with microscopic nerve root decompression.
SURGEON: Arthur Vance, MD | ANESTHESIA: General endotracheal
OPERATIVE PROCEDURE:
Patient positioned prone on Wilson frame. Midline lumbar incision made overlying L4-L5 under fluoroscopy.
Subperiosteal dissection completed. Microscope brought into surgical field.
            """
        },
        # Page 19: Operative Report Part 2
        {
            "header": "ST. JUDE SURGICAL HOSPITAL | OPERATIVE REPORT",
            "title": "OPERATIVE REPORT",
            "facility": "ST. JUDE SURGICAL HOSPITAL",
            "date": "Date of Surgery: 06/06/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
OPERATIVE PROCEDURE (CONTINUED):
Hemilaminotomy performed at right L4. Flavectomy performed to expose the thecal sac and exiting right L5 root.
Right L5 root was noted to be severely compressed by a large extruded subligamentous disc fragment.
Free fragment cleanly excised. Nerve root fully mobilized and relaxed with excellent pulsatile decompression.
Hemostasis achieved. Layered closure performed. Estimated blood loss: 35 mL. No complications.
Surgeon: Arthur Vance, MD
            """
        },
        # Page 20: PACU Nursing Note
        {
            "header": "ST. JUDE SURGICAL HOSPITAL | PACU RECORD",
            "title": "PHYSICIAN NOTE",
            "facility": "ST. JUDE SURGICAL HOSPITAL",
            "date": "Date of Service: 06/06/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
PACU POST-OP PROGRESS NOTE:
Patient transferred to recovery room. Alert and oriented.
Incisional pain rated 4/10. Radicular right leg pain completely resolved.
Vitals: BP 124/76 | HR 72 | SpO2 99% | Motor strength: Right EHL 4+/5.
Medications: Oxycodone / Acetaminophen 5/325 mg PO administered for post-op surgical pain.
PACU Nurse: Diane Watson, RN
            """
        },
        # Page 21: Hospital Discharge Summary
        {
            "header": "ST. JUDE SURGICAL HOSPITAL | DISCHARGE SUMMARY",
            "title": "DISCHARGE SUMMARY",
            "facility": "ST. JUDE SURGICAL HOSPITAL",
            "date": "Discharge Date: 06/07/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
HOSPITAL COURSE:
Patient tolerated Right L4-L5 Microdiscectomy well. Ambulating independently with physical therapy.
Voiding spontaneously. Surgical dressing clean and dry.
DISCHARGE MEDICATIONS:
- Oxycodone / Acetaminophen 5/325 mg tab, 1 tab q4-6h PRN pain, #20
- Methocarbamol 750 mg tab, 1 tab TID PRN muscle spasm, #40
- Naproxen 500 mg tab, 1 tab BID with food, #60
Attending Surgeon: Arthur Vance, MD
            """
        },
        # Page 22: Post-Op 2-Week Visit
        {
            "header": "SIERRA SPINE & ORTHOPEDIC INSTITUTE",
            "title": "PHYSICIAN NOTE",
            "facility": "SIERRA SPINE & ORTHOPEDIC INSTITUTE",
            "date": "Date of Service: 06/20/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
2-WEEK POST-OPERATIVE VISIT:
Subjective: Patient reports 90% improvement in pre-operative symptoms. Zero radiating leg pain. Incision healing well.
Objective: Incision well-approximated, sutures removed. Right EHL strength improved to 5/5. SLR negative bilaterally.
Pain Score: 1/10. Discontinue narcotic medication.
Surgeon: Arthur Vance, MD
            """
        },
        # Page 23: Post-Op 6-Week Visit
        {
            "header": "SIERRA SPINE & ORTHOPEDIC INSTITUTE",
            "title": "PHYSICIAN NOTE",
            "facility": "SIERRA SPINE & ORTHOPEDIC INSTITUTE",
            "date": "Date of Service: 07/18/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
6-WEEK POST-OPERATIVE VISIT:
Subjective: Patient walking 2 miles daily. No back pain, no radicular symptoms.
Objective: Full lumbar range of motion. Motor strength 5/5 throughout. SLR negative. Pain Score: 0/10.
Assessment: Right lumbar radiculopathy resolved following microdiscectomy.
Plan: Refer to physical therapy for post-surgical conditioning.
Surgeon: Arthur Vance, MD
            """
        },
        # Page 24: Post-Surgical PT Eval
        {
            "header": "PINNACLE PHYSICAL THERAPY & REHABILITATION",
            "title": "PHYSICAL THERAPY INITIAL EVALUATION",
            "facility": "PINNACLE PHYSICAL THERAPY & REHABILITATION",
            "date": "Date of Evaluation: 08/01/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
POST-SURGICAL PHYSICAL THERAPY EVALUATION:
Subjective: Patient 8 weeks post Right L4-L5 microdiscectomy. Goal: return to full occupational duties.
Objective: Lumbar flexion 70 degrees. Core strength 4/5. SLR negative bilaterally.
Plan: 6-8 weeks of functional restoration and conditioning.
Physical Therapist: Marcus Brody, PT, DPT
            """
        },
        # Page 25: Post-Op PT Progress
        {
            "header": "PINNACLE PHYSICAL THERAPY & REHABILITATION",
            "title": "PHYSICAL THERAPY PROGRESS NOTE",
            "facility": "PINNACLE PHYSICAL THERAPY & REHABILITATION",
            "date": "Date of Service: 08/25/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
TREATMENT: Session 6 of 12 (Post-Surgical).
Patient demonstrates good core endurance and lumbar stabilization without pain.
Pain Score: 0/10. Lifting 25 lbs safely with proper body mechanics.
Physical Therapist: Marcus Brody, PT, DPT
            """
        },
        # Page 26: PT Discharge Summary
        {
            "header": "PINNACLE PHYSICAL THERAPY & REHABILITATION",
            "title": "DISCHARGE SUMMARY",
            "facility": "PINNACLE PHYSICAL THERAPY & REHABILITATION",
            "date": "Date of Discharge: 09/20/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
PHYSICAL THERAPY DISCHARGE SUMMARY:
Goals Met: 100% of functional goals achieved. Pain-free active lumbar range of motion.
Discharge Status: Discharged to independent home exercise program. Cleared for full work duties.
Physical Therapist: Marcus Brody, PT, DPT
            """
        },
        # Page 27: Mismatched Patient Conflict (Arthur Vance)
        {
            "header": "RIVERSIDE ORTHOPEDIC CLINIC | PATIENT RECORD",
            "title": "DISCHARGE SUMMARY",
            "facility": "RIVERSIDE ORTHOPEDIC CLINIC",
            "date": "Date of Discharge: 04/12/2023",
            "patient": "Patient Name: Vance, Arthur | DOB: 11/14/1978 | Sex: Male | MRN: RIV-992144",
            "body": """
PATIENT IDENTIFICATION CONFLICT RECORD:
Patient: Vance, Arthur | DOB: 11/14/1978
Diagnosis: Left knee sprain with medial collateral ligament tenderness following sporting injury.
Treatment: Knee brace and ice therapy.
NOTE: Erroneously produced chart for non-target patient.
Attending Physician: Karen Taylor, MD
            """
        },
        # Page 28: Historical Urgent Care (2018)
        {
            "header": "RIVERBEND URGENT CARE | HISTORICAL MEDICAL ARCHIVE",
            "title": "HISTORICAL MEDICAL RECORD",
            "facility": "RIVERBEND URGENT CARE",
            "date": "Date of Service: 05/14/2018",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
HISTORICAL MEDICAL RECORD (PRIOR RECORDS OBTAINED BY SUBPOENA):
Date of Service: 05/14/2018 (5 years prior to 2023 motor vehicle collision).
Subjective: Patient reports mild lower back soreness after heavy lifting during household move. No radiating leg pain.
Assessment: Mild lumbosacral strain. Degenerative disc disease noted on plain radiographs.
Attending: Marcus Brody, MD
            """
        },
        # Page 29: Pharmacy Dispensing Record
        {
            "header": "GREENLEAF COMMUNITY PHARMACY | DISPENSING HISTORY",
            "title": "MEDICATION RECORD",
            "facility": "GREENLEAF COMMUNITY PHARMACY",
            "date": "Date of Service: 01/10/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
DISPENSING HISTORY (01/10/2023 - 09/20/2023):
01/10/2023: Naproxen 500 mg tab, qty 30, Rx by Alvarez R MD
01/10/2023: Methocarbamol 750 mg tab, qty 30, Rx by Alvarez R MD
01/18/2023: Gabapentin 300 mg cap, qty 90, Rx by Chen L MD
06/07/2023: Oxycodone / Acetaminophen 5/325 mg tab, qty 20, Rx by Vance A MD
06/07/2023: Methocarbamol 750 mg tab, qty 40, Rx by Vance A MD
Pharmacist: Sandra Patel, PharmD
            """
        },
        # Page 30: Billing Summary
        {
            "header": "SIERRA HEALTH SYSTEM | PATIENT FINANCIAL SERVICES",
            "title": "BILLING RECORD",
            "facility": "SIERRA HEALTH SYSTEM",
            "date": "Date of Service: 01/10/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
STATEMENT OF CHARGES & ITEMIZED ACCOUNTING:
Statement Period: 01/10/2023 through 09/20/2023
01/10/2023: ED Level 4 Facility & Physician Charges: $1,850.00
01/25/2023: MRI Lumbar Spine without contrast: $2,400.00
03/15/2023: Fluoroscopic Epidural Steroid Injection: $1,950.00
06/06/2023: Surgical Suite & Microdiscectomy: $14,200.00
08/01/2023 - 09/20/2023: Physical Therapy (24 Sessions): $3,600.00
TOTAL CHARGES: $24,000.00 | PAID BY INSURANCE: $21,500.00 | PATIENT BALANCE: $0.00
            """
        },
        # Page 31: Employer Work Status
        {
            "header": "SUMMIT LOGISTICS CORP | OCCUPATIONAL HEALTH & HUMAN RESOURCES",
            "title": "EMPLOYER WORK STATUS",
            "facility": "SUMMIT LOGISTICS CORP",
            "date": "Date of Service: 10/01/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
OCCUPATIONAL HEALTH WORK STATUS & RETURN TO WORK CERTIFICATE:
Employee: Eleanor M. Vance | Position: Operations & Logistics Manager | Date of Hire: 03/15/2019
Medical Leave Period: 01/10/2023 through 09/30/2023
WORK CAPACITY EVALUATION:
Patient examined following successful lumbar microdiscectomy and rehabilitation.
Full clearance for regular full-time duty without physical restrictions effective 10/01/2023.
Medical Director: Thomas Craig, MD
            """
        },
        # Page 32: Records Certification
        {
            "header": "OFFICE OF THE RECORDS CUSTODIAN | LEGAL PRODUCTION",
            "title": "RECORDS CERTIFICATION",
            "facility": "OFFICE OF THE RECORDS CUSTODIAN",
            "date": "Date of Production: 10/15/2023",
            "patient": "Patient Name: Vance, Eleanor M. | DOB: 06/18/1985 | Sex: Female | MRN: MWH-882910",
            "body": """
AFFIDAVIT OF CUSTODIAN OF MEDICAL RECORDS:
I, Rebecca Hall, certify that I am the duly authorized Custodian of Records for Sierra Health System.
I certify that the attached 32 pages of medical, radiological, surgical, pharmacy, and billing records
pertaining to Eleanor M. Vance are true, authentic, and complete copies maintained in the ordinary course of business.
SYNTHETIC TEST DATA — NOT A REAL PATIENT RECORD.
Signed and Notarized: 10/15/2023
            """
        }
    ]

    for p_info in pages_data:
        page = doc.new_page(width=612, height=792)  # Standard Letter 8.5 x 11 inches
        
        # Draw legal / compliance header watermark
        rect_header = fitz.Rect(36, 20, 576, 50)
        page.draw_rect(rect_header, color=(0.85, 0.85, 0.85), fill=(0.95, 0.95, 0.95))
        page.insert_text(fitz.Point(45, 35), "SYNTHETIC TEST DATA — NOT A REAL PATIENT RECORD", fontsize=8, color=(0.5, 0.5, 0.5))
        page.insert_text(fitz.Point(45, 45), f"{p_info['header']} | PRODUCED 10/15/2023", fontsize=7, color=(0.3, 0.3, 0.3))
        
        # Document Title
        page.insert_text(fitz.Point(45, 80), p_info["title"], fontsize=14, color=(0.1, 0.1, 0.3))
        page.insert_text(fitz.Point(45, 98), p_info["facility"], fontsize=10, color=(0.2, 0.2, 0.2))
        
        # Metadata block
        meta_rect = fitz.Rect(36, 110, 576, 145)
        page.draw_rect(meta_rect, color=(0.7, 0.7, 0.9), fill=(0.96, 0.96, 1.0))
        page.insert_text(fitz.Point(45, 125), p_info["patient"], fontsize=8.5, color=(0.1, 0.1, 0.1))
        page.insert_text(fitz.Point(45, 138), p_info["date"], fontsize=8.5, color=(0.1, 0.1, 0.1))
        
        # Body text
        body_rect = fitz.Rect(45, 160, 567, 720)
        page.insert_textbox(body_rect, p_info["body"].strip(), fontsize=9, color=(0.1, 0.1, 0.1), lineheight=1.3)
        
        # Footer
        page.insert_text(fitz.Point(45, 765), f"Page {doc.page_count} of {len(pages_data)} — Confidential Synthetic Record", fontsize=8, color=(0.5, 0.5, 0.5))

    doc.save(output_path)
    doc.close()
    print(f"Successfully generated {len(pages_data)}-page synthetic compliance PDF at: {output_path}")

if __name__ == "__main__":
    out_file = Path("data/synthetic_30plus_compliance_record.pdf")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    generate_30plus_compliance_pdf(str(out_file))
