# Workout Tracking API

A Flask REST API for trainers to manage reusable exercises, workouts, and the exercise metrics attached to each workout.

## Installation

This project uses Python 3.8+ and Pipenv.

```bash
pipenv install --dev
pipenv shell
flask --app server.app:create_app db init
flask --app server.app:create_app db migrate -m "create workout tables"
flask --app server.app:create_app db upgrade
python seed.py
```

The migration commands are only needed the first time. Run `python seed.py` again whenever you want to reset the sample data.

## Run

```bash
pipenv run flask --app server.app:create_app run --debug
```

The API is available at `http://127.0.0.1:5000`.

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/` | Health check. |
| GET | `/workouts` | List all workouts, including their attached exercises and metrics. |
| GET | `/workouts/<id>` | Return one workout or `404`. |
| POST | `/workouts` | Create a workout with `date`, positive `duration_minutes`, and optional `notes`. |
| DELETE | `/workouts/<id>` | Delete a workout and its attached workout exercises. |
| GET | `/exercises` | List all reusable exercises. |
| GET | `/exercises/<id>` | Return one exercise or `404`. |
| POST | `/exercises` | Create an exercise with `name`, `category`, and `equipment_needed`. |
| DELETE | `/exercises/<id>` | Delete an exercise and its attached workout exercises. |
| POST | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Attach an exercise to a workout with at least one positive `reps`, `sets`, or `duration_seconds` value. |

Example request bodies:

```json
{"date": "2026-09-05", "duration_minutes": 50, "notes": "Upper body"}
```

```json
{"name": "Deadlift", "category": "Strength", "equipment_needed": true}
```

```json
{"sets": 3, "reps": 10}
```

## Validation and constraints

- Exercise names are required and unique.
- Workout duration must be a positive integer.
- Workout exercise metrics must be positive integers, and at least one metric is required.
- A workout can contain a given exercise only once.
- Deleting a workout or exercise cascades to its join-table rows.

## Tests

```bash
pipenv run pytest
```
