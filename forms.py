from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, \
    TextAreaField, IntegerField, FloatField, BooleanField, RadioField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from models import Usuario


class RegistroForm(FlaskForm):
    tipo_usuario = SelectField('Tipo de Usuario', 
        choices=[
            ('estudiante', 'Estudiante'),
            ('egresado', 'Egresado'),
            ('empleador', 'Empleador')
        ],
        validators=[DataRequired()]
    )
    
    clave_unica = StringField('Clave Única Institucional', 
        validators=[DataRequired(), Length(min=5, max=50)]
    )
    
    email = StringField('Correo Electrónico', 
        validators=[DataRequired(), Email()]
    )
    
    password = PasswordField('Contraseña', 
        validators=[DataRequired(), Length(min=8)]
    )
    
    confirm_password = PasswordField('Confirmar Contraseña', 
        validators=[DataRequired(), EqualTo('password')]
    )
    
    nombre = StringField('Nombre(s)', validators=[DataRequired()])
    apellido_paterno = StringField('Apellido Paterno', validators=[DataRequired()])
    apellido_materno = StringField('Apellido Materno')
    
    edad = IntegerField('Edad')
    sexo = SelectField('Sexo', choices=[('', 'Seleccione'), ('Hombre', 'Hombre'), ('Mujer', 'Mujer')])
    telefono = StringField('Número de Celular')
    
    carrera = StringField('Carrera')
    facultad = StringField('Facultad')
    semestre = IntegerField('Semestre')
    
    empresa = StringField('Nombre de la Empresa')
    puesto = StringField('Puesto en la Organización')
    antiguedad = IntegerField('Antigüedad (años)')
    
    aceptar_privacidad = BooleanField(
        'Acepto el aviso de privacidad y el tratamiento de mis datos',
        validators=[DataRequired()]
    )
    
    submit = SubmitField('Registrarse')
    
    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('El correo electrónico ya está registrado.')
    
    def validate_clave_unica(self, clave_unica):
        usuario = Usuario.query.filter_by(clave_unica=clave_unica.data).first()
        if usuario:
            raise ValidationError('La Clave Única ya está registrada.')


class LoginForm(FlaskForm):
    email = StringField('Correo Electrónico', 
        validators=[DataRequired(), Email()]
    )
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')


class VacanteForm(FlaskForm):
    titulo = StringField('Título de la Vacante', 
        validators=[DataRequired(), Length(max=200)]
    )
    
    descripcion = TextAreaField('Descripción', validators=[DataRequired()])
    requisitos = TextAreaField('Requisitos')
    
    carrera_requerida = StringField('Carrera Requerida')
    experiencia_anos = IntegerField('Años de Experiencia', default=0)
    
    salario_min = FloatField('Salario Mínimo')
    salario_max = FloatField('Salario Máximo')
    
    modalidad = SelectField('Modalidad',
        choices=[
            ('presencial', 'Presencial'),
            ('remoto', 'Remoto'),
            ('hibrido', 'Híbrido')
        ],
        validators=[DataRequired()]
    )
    
    ubicacion = StringField('Ubicación')
    tipo_contrato = StringField('Tipo de Contrato')
    
    submit = SubmitField('Publicar Vacante')