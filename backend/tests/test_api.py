import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] in ["ok", "healthy"]

def test_api_process_record():
    res = client.post("/api/process")
    assert res.status_code == 200
    data = res.json()
    assert "patient" in data
    assert len(data["documents"]) >= 15
    assert len(data["conditions"]) >= 5

def test_api_get_patient():
    res = client.get("/api/patient")
    assert res.status_code == 200
    p = res.json()
    assert "Marcus" in p["full_name"] and "Whitfield" in p["full_name"]
    assert p["gender"] == "male"
    assert p["mrn"] == "PCG-4471902"

def test_api_get_documents():
    res = client.get("/api/documents")
    assert res.status_code == 200
    docs = res.json()
    assert len(docs) >= 15

def test_api_get_conditions():
    res = client.get("/api/conditions")
    assert res.status_code == 200
    conds = res.json()
    assert len(conds) >= 5
    assert any("radiculopathy" in c["name"].lower() for c in conds)

def test_api_get_medications():
    res = client.get("/api/medications")
    assert res.status_code == 200
    meds = res.json()
    assert len(meds) >= 5

def test_api_get_fhir_bundle():
    res = client.get("/api/fhir/bundle")
    assert res.status_code == 200
    bundle = res.json()
    assert bundle["resourceType"] == "Bundle"
    assert len(bundle["entry"]) >= 50

def test_api_get_evaluation():
    res = client.get("/api/evaluation")
    assert res.status_code == 200
    ev = res.json()
    assert ev["page_classification_accuracy"] == 1.0
    assert ev["fhir_validation_pass_rate"] == 100.0

def test_api_clinical_queries():
    res = client.post("/api/queries/run", json={"query_name": "timeline"})
    assert res.status_code == 200
    assert len(res.json()["results"]) >= 10
