from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import date, datetime

class PageLayoutFeatures(BaseModel):
    width: float = 0.0
    height: float = 0.0
    num_blocks: int = 0
    num_lines: int = 0
    has_header_bar: bool = False
    has_signature_line: bool = False
    has_table_structure: bool = False
    text_density: float = 0.0

class PageData(BaseModel):
    page_number: int
    raw_text: str
    cleaned_text: str
    header: Optional[str] = None
    footer: Optional[str] = None
    layout_features: PageLayoutFeatures = Field(default_factory=PageLayoutFeatures)
    text_density: float = 0.0
    page_hash: str
    is_blank: bool = False
    is_duplicate: bool = False
    duplicate_of: Optional[int] = None
    duplicate_similarity: float = 0.0
    predicted_document_type: str = "UNKNOWN"
    classification_confidence: float = 0.0
    classification_signals: List[str] = Field(default_factory=list)

class LogicalDocument(BaseModel):
    document_id: str
    document_type: str
    title: str
    facility_name: Optional[str] = None
    provider_name: Optional[str] = None
    service_date: Optional[str] = None
    start_page: int
    end_page: int
    page_count: int = 1
    page_numbers: List[int] = Field(default_factory=list)
    classification_confidence: float = 0.0
    is_historical: bool = False
    is_conflicting_patient: bool = False
    raw_text: str = ""

class ProvenanceRecord(BaseModel):
    source_document_id: str
    source_page: int
    source_text: str
    char_offset_start: Optional[int] = None
    char_offset_end: Optional[int] = None
    confidence: float = 1.0

class TerminologyMapping(BaseModel):
    original_text: str
    system: str  # e.g., "http://hl7.org/fhir/sid/icd-10-cm", "http://www.nlm.nih.gov/research/umls/rxnorm", "http://loinc.org", "http://www.ama-assn.org/go/cpt"
    code: Optional[str] = None
    display: Optional[str] = None
    mapping_confidence: float = 0.0
    unmapped_reason: Optional[str] = None

class PatientEntity(BaseModel):
    patient_id: str
    full_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    mrn: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    employer: Optional[str] = None
    is_canonical: bool = True
    provenance: List[ProvenanceRecord] = Field(default_factory=list)
    confidence: float = 1.0

class EncounterEntity(BaseModel):
    encounter_id: str
    patient_id: str
    encounter_date: str
    encounter_type: str
    facility: Optional[str] = None
    provider: Optional[str] = None
    department: Optional[str] = None
    chief_complaint: Optional[str] = None
    disposition: Optional[str] = None
    is_historical: bool = False
    provenance: List[ProvenanceRecord] = Field(default_factory=list)
    confidence: float = 1.0

class ConditionEntity(BaseModel):
    condition_id: str
    patient_id: str
    encounter_id: Optional[str] = None
    name: str
    clinical_status: str = "active"  # active, resolved, recurrence
    verification_status: str = "confirmed"
    onset_date: Optional[str] = None
    recorded_date: Optional[str] = None
    body_site: Optional[str] = None
    is_historical: bool = False
    terminology: Optional[TerminologyMapping] = None
    provenance: List[ProvenanceRecord] = Field(default_factory=list)
    confidence: float = 1.0

class SymptomEntity(BaseModel):
    symptom_id: str
    patient_id: str
    encounter_id: Optional[str] = None
    name: str
    severity: Optional[str] = None
    location: Optional[str] = None
    recorded_date: Optional[str] = None
    provenance: List[ProvenanceRecord] = Field(default_factory=list)
    confidence: float = 1.0

class MedicationEntity(BaseModel):
    medication_id: str
    patient_id: str
    encounter_id: Optional[str] = None
    name: str
    dose: Optional[str] = None
    route: Optional[str] = None
    frequency: Optional[str] = None
    status: str = "active"  # active, completed, discontinued, prn
    prescribed_date: Optional[str] = None
    dispensed_date: Optional[str] = None
    indication: Optional[str] = None
    adverse_reactions: Optional[str] = None
    terminology: Optional[TerminologyMapping] = None
    provenance: List[ProvenanceRecord] = Field(default_factory=list)
    confidence: float = 1.0

class AllergyEntity(BaseModel):
    allergy_id: str
    patient_id: str
    encounter_id: Optional[str] = None
    allergen: str
    reaction: Optional[str] = None
    certainty: str = "confirmed"
    status: str = "active"  # active, none_documented
    recorded_date: Optional[str] = None
    source: Optional[str] = None
    provenance: List[ProvenanceRecord] = Field(default_factory=list)
    confidence: float = 1.0

class ProcedureEntity(BaseModel):
    procedure_id: str
    patient_id: str
    encounter_id: Optional[str] = None
    name: str
    status: str = "completed"
    performed_date: Optional[str] = None
    performer: Optional[str] = None
    location: Optional[str] = None
    findings: Optional[str] = None
    terminology: Optional[TerminologyMapping] = None
    provenance: List[ProvenanceRecord] = Field(default_factory=list)
    confidence: float = 1.0

class ObservationEntity(BaseModel):
    observation_id: str
    patient_id: str
    encounter_id: Optional[str] = None
    category: str  # vital-signs, exam-finding, lab-result, imaging-finding
    name: str
    value_string: Optional[str] = None
    value_numeric: Optional[float] = None
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    interpretation: Optional[str] = None  # normal, abnormal, high, low, critical
    effective_date: Optional[str] = None
    terminology: Optional[TerminologyMapping] = None
    provenance: List[ProvenanceRecord] = Field(default_factory=list)
    confidence: float = 1.0

class ConflictRecord(BaseModel):
    conflict_id: str
    field: str
    candidate_values: List[str]
    source_documents: List[str]
    source_pages: List[int]
    confidence: float
    resolution: str
    resolution_reason: str
    requires_review: bool = True
    status: str = "flagged"  # flagged, resolved, rejected

class ReviewQueueItem(BaseModel):
    queue_id: str
    entity_type: str
    entity_id: str
    field: str
    current_value: str
    confidence: float
    reason: str
    source_page: int
    source_document_id: str
    status: str = "pending"  # pending, accepted, corrected, rejected
    corrected_value: Optional[str] = None
    reviewer_notes: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class PipelineResult(BaseModel):
    success: bool
    filename: str
    total_pages: int
    pages: List[PageData]
    documents: List[LogicalDocument]
    patient: PatientEntity
    encounters: List[EncounterEntity]
    conditions: List[ConditionEntity]
    symptoms: List[SymptomEntity]
    medications: List[MedicationEntity]
    allergies: List[AllergyEntity]
    procedures: List[ProcedureEntity]
    observations: List[ObservationEntity]
    conflicts: List[ConflictRecord]
    review_queue: List[ReviewQueueItem]
    fhir_bundle: Dict[str, Any]
    fhir_validation: Dict[str, Any]
    execution_time_ms: float = 0.0
