from marshmallow import Schema, fields, validate, validates_schema, ValidationError


positive_integer = validate.Range(min=1)


def non_blank(value):
    if not value.strip():
        raise ValidationError("Must contain at least one non-whitespace character")


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(allow_none=True, validate=positive_integer)
    sets = fields.Int(allow_none=True, validate=positive_integer)
    duration_seconds = fields.Int(allow_none=True, validate=positive_integer)
    exercise = fields.Nested(lambda: ExerciseSchema(only=("id", "name", "category")), dump_only=True)

    @validates_schema
    def validate_metric(self, data, **kwargs):
        if not any(data.get(key) is not None for key in ("reps", "sets", "duration_seconds")):
            raise ValidationError("At least one of reps, sets, or duration_seconds is required")


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=[validate.Length(min=1, max=120), non_blank])
    category = fields.Str(required=True, validate=[validate.Length(min=1, max=80), non_blank])
    equipment_needed = fields.Bool(required=True)
    workout_exercises = fields.Nested(WorkoutExerciseSchema, many=True, dump_only=True)


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True, validate=positive_integer)
    notes = fields.Str(allow_none=True, validate=validate.Length(max=2000))
    workout_exercises = fields.Nested(WorkoutExerciseSchema, many=True, dump_only=True)
