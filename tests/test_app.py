from urllib.parse import quote


def activity_path(activity_name):
    return quote(activity_name, safe="")


def participant_path(email):
    return quote(email, safe="")


def test_root_redirects_to_frontend(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_available_activities(client):
    response = client.get("/activities")

    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert "participants" in activities["Chess Club"]


def test_signup_adds_participant(client):
    activity = "Basketball Club"
    email = "student@example.com"

    response = client.post(
        f"/activities/{activity_path(activity)}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email in client.get("/activities").json()[activity]["participants"]


def test_duplicate_signup_returns_bad_request(client):
    activity = "Basketball Club"
    email = "student@example.com"
    endpoint = f"/activities/{activity_path(activity)}/signup"

    client.post(endpoint, params={"email": email})
    response = client.post(endpoint, params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_for_unknown_activity_returns_not_found(client):
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    activity = "Basketball Club"
    email = "student@example.com"
    signup_endpoint = f"/activities/{activity_path(activity)}/signup"
    delete_endpoint = (
        f"/activities/{activity_path(activity)}/participants/"
        f"{participant_path(email)}"
    )

    client.post(signup_endpoint, params={"email": email})
    response = client.delete(delete_endpoint)

    assert response.status_code == 200
    assert email not in client.get("/activities").json()[activity]["participants"]


def test_unregister_unknown_participant_returns_not_found(client):
    activity = "Basketball Club"
    endpoint = (
        f"/activities/{activity_path(activity)}/participants/"
        f"{participant_path('missing@example.com')}"
    )

    response = client.delete(endpoint)

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_from_unknown_activity_returns_not_found(client):
    endpoint = (
        "/activities/Unknown%20Club/participants/"
        f"{participant_path('student@example.com')}"
    )

    response = client.delete(endpoint)

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
