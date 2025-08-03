import uuid


def test_create_and_fetch_roundtrip(app_client):
    # Base64 for "password123"
    plain_b64 = "cGFzc3dvcmQxMjM="
    r = app_client.post("/vault/secret/create/", json={"secret": plain_b64})
    assert r.status_code == 200
    data = r.json()
    assert "secret_id" in data
    sid = data["secret_id"]

    r2 = app_client.post("/vault/secret/fetch", json={"secret_id": sid})
    assert r2.status_code == 200
    assert r2.json()["secret"] == plain_b64


def test_invalid_base64_returns_400(app_client):
    r = app_client.post("/vault/secret/create/", json={"secret": "***"})
    assert r.status_code == 400
    assert "invalid base64" in r.json()["detail"].lower()


def test_not_found_returns_404(app_client):
    bogus = str(uuid.uuid4())
    r = app_client.post("/vault/secret/fetch", json={"secret_id": bogus})
    assert r.status_code == 404
    assert r.json()["detail"] == "Secret not found"


def test_audit_written(app_client, mongo):
    # create
    r = app_client.post("/vault/secret/create/", json={"secret": "dGVzdA=="})  # "test"
    sid = r.json()["secret_id"]
    # fetch
    app_client.post("/vault/secret/fetch", json={"secret_id": sid})

    # At least two audit entries for this secret_id: create + fetch
    count = mongo["vault"]["audit_logs"].count_documents({"secret_id": sid})
    assert count >= 2
