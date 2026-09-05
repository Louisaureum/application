#!/usr/bin/env python3
from datetime import date

from server.app import app
from server.models import Exercise, Workout, WorkoutExercise, db


with app.app_context():
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()

    strength = Exercise(name="Barbell Squat", category="Strength", equipment_needed=True)
    cardio = Exercise(name="Running", category="Cardio", equipment_needed=False)
    mobility = Exercise(name="Plank", category="Core", equipment_needed=False)
    db.session.add_all([strength, cardio, mobility])

    workout = Workout(
        date=date.today(),
        duration_minutes=45,
        notes="Full-body training session",
    )
    db.session.add(workout)
    db.session.flush()
    db.session.add_all(
        [
            WorkoutExercise(workout=workout, exercise=strength, sets=4, reps=8),
            WorkoutExercise(workout=workout, exercise=cardio, duration_seconds=600),
            WorkoutExercise(workout=workout, exercise=mobility, duration_seconds=60),
        ]
    )
    db.session.commit()
    print("Seeded exercises, workout, and workout exercises.")
