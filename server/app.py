from pathlib import Path

from flask import Flask, jsonify, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

try:
    from .models import Exercise, Workout, WorkoutExercise, db
    from .schemas import ExerciseSchema, WorkoutExerciseSchema, WorkoutSchema
except ImportError:
    from models import Exercise, Workout, WorkoutExercise, db
    from schemas import ExerciseSchema, WorkoutExerciseSchema, WorkoutSchema


migrate = Migrate()
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
workout_exercise_schema = WorkoutExerciseSchema()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    default_database = Path(app.instance_path) / "app.db"
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{default_database}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    migrate.init_app(app, db)

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return jsonify({"errors": error.messages}), 400

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        db.session.rollback()
        return jsonify({"error": "The request violates a database constraint"}), 409

    @app.get("/workouts")
    def list_workouts():
        return jsonify(workouts_schema.dump(Workout.query.order_by(Workout.date.desc()).all()))

    @app.get("/workouts/<int:workout_id>")
    def get_workout(workout_id):
        workout = db.get_or_404(Workout, workout_id)
        return jsonify(workout_schema.dump(workout))

    @app.post("/workouts")
    def create_workout():
        workout = Workout(**workout_schema.load(request.get_json(silent=True) or {}))
        db.session.add(workout)
        db.session.commit()
        return jsonify(workout_schema.dump(workout)), 201

    @app.delete("/workouts/<int:workout_id>")
    def delete_workout(workout_id):
        workout = db.get_or_404(Workout, workout_id)
        db.session.delete(workout)
        db.session.commit()
        return "", 204

    @app.get("/exercises")
    def list_exercises():
        return jsonify(exercises_schema.dump(Exercise.query.order_by(Exercise.name).all()))

    @app.get("/exercises/<int:exercise_id>")
    def get_exercise(exercise_id):
        exercise = db.get_or_404(Exercise, exercise_id)
        return jsonify(exercise_schema.dump(exercise))

    @app.post("/exercises")
    def create_exercise():
        exercise = Exercise(**exercise_schema.load(request.get_json(silent=True) or {}))
        db.session.add(exercise)
        db.session.commit()
        return jsonify(exercise_schema.dump(exercise)), 201

    @app.delete("/exercises/<int:exercise_id>")
    def delete_exercise(exercise_id):
        exercise = db.get_or_404(Exercise, exercise_id)
        db.session.delete(exercise)
        db.session.commit()
        return "", 204

    @app.post("/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises")
    def add_exercise_to_workout(workout_id, exercise_id):
        workout = db.get_or_404(Workout, workout_id)
        exercise = db.get_or_404(Exercise, exercise_id)
        payload = workout_exercise_schema.load(request.get_json(silent=True) or {})
        link = WorkoutExercise(workout=workout, exercise=exercise, **payload)
        db.session.add(link)
        db.session.commit()
        return jsonify(workout_exercise_schema.dump(link)), 201

    @app.get("/")
    def health_check():
        return jsonify({"name": "Workout API", "status": "ok"})

    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5555, debug=True)
