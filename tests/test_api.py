from datetime import date

from server.models import Exercise, Workout, WorkoutExercise, db


def create_exercise(client, name="Push Up"):
    response = client.post(
        "/exercises",
        json={"name": name, "category": "Strength", "equipment_needed": False},
    )
    assert response.status_code == 201
    return response.get_json()


def create_workout(client):
    response = client.post(
        "/workouts",
        json={"date": "2026-09-05", "duration_minutes": 30, "notes": "Test"},
    )
    assert response.status_code == 201
    return response.get_json()


def test_create_and_list_resources(client):
    exercise = create_exercise(client)
    workout = create_workout(client)
    response = client.post(
        f"/workouts/{workout['id']}/exercises/{exercise['id']}/workout_exercises",
        json={"sets": 3, "reps": 12},
    )
    assert response.status_code == 201
    assert response.get_json()["exercise"]["name"] == "Push Up"

    response = client.get(f"/workouts/{workout['id']}")
    assert response.status_code == 200
    assert response.get_json()["workout_exercises"][0]["reps"] == 12


def test_schema_validations_are_returned_as_bad_request(client):
    assert client.post("/workouts", json={"date": "2026-09-05", "duration_minutes": 0}).status_code == 400
    assert client.post(
        "/exercises", json={"name": "", "category": "Strength", "equipment_needed": False}
    ).status_code == 400
    assert client.post(
        "/exercises", json={"name": "   ", "category": "Strength", "equipment_needed": False}
    ).status_code == 400

    exercise = create_exercise(client)
    workout = create_workout(client)
    response = client.post(
        f"/workouts/{workout['id']}/exercises/{exercise['id']}/workout_exercises",
        json={},
    )
    assert response.status_code == 400


def test_delete_cascades_join_rows(client, app):
    exercise = create_exercise(client)
    workout = create_workout(client)
    client.post(
        f"/workouts/{workout['id']}/exercises/{exercise['id']}/workout_exercises",
        json={"duration_seconds": 60},
    )
    assert client.delete(f"/workouts/{workout['id']}").status_code == 204

    with app.app_context():
        assert db.session.get(WorkoutExercise, 1) is None
        assert db.session.get(Exercise, exercise["id"]) is not None
        assert db.session.get(Workout, workout["id"]) is None
