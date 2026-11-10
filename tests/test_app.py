ACTIVITY = "Chess Club"
NEW_EMAIL = "newstudent@mergington.edu"


def participants(client, name=ACTIVITY):
    return client.get("/activities").json()[name]["participants"]


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_structure(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert ACTIVITY in data
    for details in data.values():
        assert {"description", "schedule", "max_participants", "participants"} <= details.keys()
        assert isinstance(details["participants"], list)


def test_signup_adds_participant(client):
    response = client.post(f"/activities/{ACTIVITY}/signup", params={"email": NEW_EMAIL})
    assert response.status_code == 200
    assert NEW_EMAIL in response.json()["message"]
    assert NEW_EMAIL in participants(client)


def test_signup_unknown_activity_returns_404(client):
    response = client.post("/activities/Nope/signup", params={"email": NEW_EMAIL})
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_returns_400(client):
    existing = participants(client)[0]
    response = client.post(f"/activities/{ACTIVITY}/signup", params={"email": existing})
    assert response.status_code == 400
    assert participants(client).count(existing) == 1


def test_unregister_removes_participant(client):
    existing = participants(client)[0]
    response = client.delete(f"/activities/{ACTIVITY}/participants", params={"email": existing})
    assert response.status_code == 200
    assert existing not in participants(client)


def test_unregister_unknown_activity_returns_404(client):
    response = client.delete("/activities/Nope/participants", params={"email": NEW_EMAIL})
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_not_signed_up_returns_404(client):
    response = client.delete(f"/activities/{ACTIVITY}/participants", params={"email": NEW_EMAIL})
    assert response.status_code == 404


def test_signup_then_unregister_round_trip(client):
    original = participants(client)
    client.post(f"/activities/{ACTIVITY}/signup", params={"email": NEW_EMAIL})
    client.delete(f"/activities/{ACTIVITY}/participants", params={"email": NEW_EMAIL})
    assert participants(client) == original


def test_state_is_isolated_between_tests(client):
    assert NEW_EMAIL not in participants(client)
