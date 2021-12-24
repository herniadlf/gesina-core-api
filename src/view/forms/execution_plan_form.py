from flask_wtf.form import FlaskForm
from wtforms.validators import DataRequired, ValidationError
from wtforms import StringField, IntegerField, DateField
from flask_wtf.file import FileField, FileRequired


class DateRangeValidator(object):
    def __call__(self, form, field):
        if form.start_date.data > form.end_date.data:
            raise ValidationError(
                'Error: "Fecha desde" debe ser menor a la "fecha hasta"'
            )


class ExecutionPlanForm(FlaskForm):
    plan_name = StringField(
        validators=[DataRequired(message="Error: Ingrese un nombre de plan")]
    )
    geometry_option = IntegerField(
        validators=[DataRequired(message="Error: Seleccione una geometría")]
    )
    flow_file = FileField(
        validators=[FileRequired(message="Error: Seleccione un archivo")]
    )
    start_date = DateField(
        format="%d/%m/%Y",
        validators=[DataRequired(message="Error: Seleccione una fecha desde")],
    )
    end_date = DateField(
        format="%d/%m/%Y",
        validators=[
            DataRequired(message="Error: Seleccione una fecha hasta"),
            DateRangeValidator(),
        ],
    )

    def get_errors(self):
        errors = []
        errors += self.plan_name.errors
        errors += self.geometry_option.errors
        errors += self.flow_file.errors
        errors += self.start_date.errors
        errors += self.end_date.errors
        return errors
