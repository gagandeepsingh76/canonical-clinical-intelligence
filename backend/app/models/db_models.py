import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class DBPatient(Base):
    __tablename__ = "patients"
    
    patient_id = Column(String, primary_key=True, index=True)
    full_name = Column(String, nullable=False, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    dob = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    mrn = Column(String, nullable=True, index=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    employer = Column(String, nullable=True)
    is_canonical = Column(Boolean, default=True)
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class DBDocument(Base):
    __tablename__ = "documents"
    
    document_id = Column(String, primary_key=True, index=True)
    document_type = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    facility_name = Column(String, nullable=True)
    provider_name = Column(String, nullable=True)
    service_date = Column(String, nullable=True, index=True)
    start_page = Column(Integer, nullable=False)
    end_page = Column(Integer, nullable=False)
    page_count = Column(Integer, default=1)
    classification_confidence = Column(Float, default=1.0)
    is_historical = Column(Boolean, default=False)
    is_conflicting_patient = Column(Boolean, default=False)
    raw_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    pages = relationship("DBDocumentPage", back_populates="document", cascade="all, delete-orphan")

class DBDocumentPage(Base):
    __tablename__ = "document_pages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String, ForeignKey("documents.document_id"), nullable=True)
    page_number = Column(Integer, nullable=False, index=True)
    raw_text = Column(Text, nullable=False)
    cleaned_text = Column(Text, nullable=False)
    header = Column(String, nullable=True)
    footer = Column(String, nullable=True)
    page_hash = Column(String, nullable=False)
    is_blank = Column(Boolean, default=False)
    is_duplicate = Column(Boolean, default=False)
    duplicate_of = Column(Integer, nullable=True)
    predicted_document_type = Column(String, nullable=False)
    classification_confidence = Column(Float, default=1.0)
    layout_features = Column(JSON, nullable=True)
    
    document = relationship("DBDocument", back_populates="pages")

class DBEncounter(Base):
    __tablename__ = "encounters"
    
    encounter_id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"), nullable=False, index=True)
    encounter_date = Column(String, nullable=False, index=True)
    encounter_type = Column(String, nullable=False)
    facility = Column(String, nullable=True)
    provider = Column(String, nullable=True)
    department = Column(String, nullable=True)
    chief_complaint = Column(Text, nullable=True)
    disposition = Column(String, nullable=True)
    is_historical = Column(Boolean, default=False)
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class DBCondition(Base):
    __tablename__ = "conditions"
    
    condition_id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"), nullable=False, index=True)
    encounter_id = Column(String, ForeignKey("encounters.encounter_id"), nullable=True)
    name = Column(String, nullable=False, index=True)
    clinical_status = Column(String, default="active")
    verification_status = Column(String, default="confirmed")
    onset_date = Column(String, nullable=True, index=True)
    recorded_date = Column(String, nullable=True)
    body_site = Column(String, nullable=True)
    is_historical = Column(Boolean, default=False)
    icd10_code = Column(String, nullable=True, index=True)
    icd10_display = Column(String, nullable=True)
    terminology_confidence = Column(Float, default=0.0)
    confidence = Column(Float, default=1.0)
    provenance = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class DBMedication(Base):
    __tablename__ = "medications"
    
    medication_id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"), nullable=False, index=True)
    encounter_id = Column(String, ForeignKey("encounters.encounter_id"), nullable=True)
    name = Column(String, nullable=False, index=True)
    dose = Column(String, nullable=True)
    route = Column(String, nullable=True)
    frequency = Column(String, nullable=True)
    status = Column(String, default="active", index=True)
    prescribed_date = Column(String, nullable=True)
    dispensed_date = Column(String, nullable=True)
    indication = Column(String, nullable=True)
    adverse_reactions = Column(String, nullable=True)
    rxnorm_code = Column(String, nullable=True, index=True)
    rxnorm_display = Column(String, nullable=True)
    terminology_confidence = Column(Float, default=0.0)
    confidence = Column(Float, default=1.0)
    provenance = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class DBAllergy(Base):
    __tablename__ = "allergies"
    
    allergy_id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"), nullable=False, index=True)
    encounter_id = Column(String, ForeignKey("encounters.encounter_id"), nullable=True)
    allergen = Column(String, nullable=False, index=True)
    reaction = Column(String, nullable=True)
    certainty = Column(String, default="confirmed")
    status = Column(String, default="active")
    recorded_date = Column(String, nullable=True)
    source = Column(String, nullable=True)
    confidence = Column(Float, default=1.0)
    provenance = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class DBProcedure(Base):
    __tablename__ = "procedures"
    
    procedure_id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"), nullable=False, index=True)
    encounter_id = Column(String, ForeignKey("encounters.encounter_id"), nullable=True)
    name = Column(String, nullable=False, index=True)
    status = Column(String, default="completed")
    performed_date = Column(String, nullable=True, index=True)
    performer = Column(String, nullable=True)
    location = Column(String, nullable=True)
    findings = Column(Text, nullable=True)
    cpt_code = Column(String, nullable=True, index=True)
    cpt_display = Column(String, nullable=True)
    terminology_confidence = Column(Float, default=0.0)
    confidence = Column(Float, default=1.0)
    provenance = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class DBObservation(Base):
    __tablename__ = "observations"
    
    observation_id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"), nullable=False, index=True)
    encounter_id = Column(String, ForeignKey("encounters.encounter_id"), nullable=True)
    category = Column(String, nullable=False, index=True)  # vital-signs, exam-finding, lab-result, imaging
    name = Column(String, nullable=False, index=True)
    value_string = Column(String, nullable=True)
    value_numeric = Column(Float, nullable=True)
    unit = Column(String, nullable=True)
    reference_range = Column(String, nullable=True)
    interpretation = Column(String, nullable=True, index=True)  # normal, abnormal, high, low
    effective_date = Column(String, nullable=True, index=True)
    loinc_code = Column(String, nullable=True, index=True)
    loinc_display = Column(String, nullable=True)
    terminology_confidence = Column(Float, default=0.0)
    confidence = Column(Float, default=1.0)
    provenance = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class DBConflict(Base):
    __tablename__ = "conflicts"
    
    conflict_id = Column(String, primary_key=True, index=True)
    field = Column(String, nullable=False, index=True)
    candidate_values = Column(JSON, nullable=False)
    source_documents = Column(JSON, nullable=False)
    source_pages = Column(JSON, nullable=False)
    confidence = Column(Float, default=1.0)
    resolution = Column(Text, nullable=False)
    resolution_reason = Column(Text, nullable=False)
    requires_review = Column(Boolean, default=True, index=True)
    status = Column(String, default="flagged", index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class DBReviewQueue(Base):
    __tablename__ = "review_queue"
    
    queue_id = Column(String, primary_key=True, index=True)
    entity_type = Column(String, nullable=False, index=True)
    entity_id = Column(String, nullable=False)
    field = Column(String, nullable=False)
    current_value = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)
    reason = Column(Text, nullable=False)
    source_page = Column(Integer, nullable=False)
    source_document_id = Column(String, nullable=False)
    status = Column(String, default="pending", index=True)
    corrected_value = Column(Text, nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
