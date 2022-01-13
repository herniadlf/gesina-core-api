from flask_wtf.form import FlaskForm
from wtforms import StringField, IntegerField, validators
from flask_wtf.file import FileField, FileRequired


class GeometryForm(FlaskForm):
    description = StringField(
        validators=[
            validators.Length(
                min=1,
                max=256,
                message="La descripción debe tener entre 1 y 256 caracteres.",
            ),
            validators.DataRequired(message="Error: Ingrese una descripción"),
        ]
    )
    file = FileField(validators=[FileRequired(message="Error: Seleccione un archivo")])
    user_id = IntegerField()

    def get_errors(self):
        errors = []
        errors += self.description.errors
        errors += self.file.errors
        return errors
