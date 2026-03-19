from fastapi.testclient import TestClient
from app.main import app
import builtins

client = TestClient(app)
successes = 0
failures = 0

def assert_msg(condition, msg):
    global successes, failures
    if condition:
        successes += 1
        print(f"[OK] {msg}")
    else:
        failures += 1
        print(f"[FAIL] {msg}")

def test_read_main():
    response = client.get("/")
    assert_msg(response.status_code == 200, "Frontend serving")
    assert_msg("text/html" in response.headers["content-type"], "Frontend content-type")

def test_api_validation_error():
    response = client.post("/api/v1/cases/create", json={})
    assert_msg(response.status_code == 422, "Validation 422 returns correctly")
    
    data = response.json()
    assert_msg(data.get("success") is False, "Validation includes success=False")
    assert_msg("errors" in data.get("data", {}), "Validation includes data.errors")

def test_api_prefix():
    response = client.post("/cases/create", json={}) # Should be 404 because without /api/v1
    assert_msg(response.status_code == 404, "Old routes are 404")

if __name__ == "__main__":
    test_read_main()
    test_api_prefix()
    test_api_validation_error()
    print(f"\nResults: {successes} Passed, {failures} Failed")
    if failures > 0:
        exit(1)
