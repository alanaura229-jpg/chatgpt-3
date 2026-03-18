from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets

# ─── Tabla intermedia postulaciones ────────────────────────────────────────────
postulaciones = db.Table('postulaciones',
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuario.id'), primary_key=True),
    db.Column('vacante_id', db.Integer, db.ForeignKey('vacante.id'), primary_key=True),
    db.Column('fecha_postulacion', db.DateTime, default=datetime.utcnow)
)

# ─── Constantes de tipos de usuario ────────────────────────────────────────────
TIPO_ALUMNO             = 'alumno'
TIPO_EGRESADO           = 'egresado'
TIPO_PERSONA_MEXICANA   = 'persona_mexicana'
TIPO_PERSONA_EXTRANJERA = 'persona_extranjera'
TIPO_EMPRESA            = 'empresa'
TIPO_COORDINACION       = 'coordinacion'
TIPO_ADMIN              = 'admin'

TIPOS_VALIDOS = [
    TIPO_ALUMNO, TIPO_EGRESADO,
    TIPO_PERSONA_MEXICANA, TIPO_PERSONA_EXTRANJERA,
    TIPO_EMPRESA, TIPO_COORDINACION, TIPO_ADMIN,
]

# Plazo de inactividad antes de suspension automatica (dias)
PLAZO_INACTIVIDAD_DIAS = 180


# ─── Modelo principal de Usuario ───────────────────────────────────────────────
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'

    id                = db.Column(db.Integer, primary_key=True)
    clave_unica       = db.Column(db.String(50), unique=True, nullable=False)
    email             = db.Column(db.String(120), unique=True, nullable=False)
    password_hash     = db.Column(db.String(256), nullable=False)

    # Tipo de usuario
    tipo_usuario      = db.Column(db.String(30), nullable=False)

    # Datos personales
    nombre            = db.Column(db.String(100), nullable=False)
    apellido_paterno  = db.Column(db.String(50), nullable=False)
    apellido_materno  = db.Column(db.String(50))
    edad              = db.Column(db.Integer)
    sexo              = db.Column(db.String(30))
    telefono          = db.Column(db.String(30))
    nacionalidad      = db.Column(db.String(80))
    pais_origen       = db.Column(db.String(100))

    # Datos academicos
    carrera           = db.Column(db.String(100))
    semestre          = db.Column(db.Integer)
    modalidad_estudio = db.Column(db.String(30))
    facultad          = db.Column(db.String(100))
    area              = db.Column(db.String(100))
    programa_academico= db.Column(db.String(150))

    # Egresados
    anio_egreso           = db.Column(db.Integer)
    cedula_profesional    = db.Column(db.String(30))
    experiencia_laboral   = db.Column(db.Text)
    certificaciones       = db.Column(db.Text)
    especializaciones     = db.Column(db.Text)

    # CV
    cv_filename       = db.Column(db.String(255))

    # Empleadores / Empresas
    nombre_empresa    = db.Column(db.String(150))
    rfc_empresa       = db.Column(db.String(20))
    giro_empresa      = db.Column(db.String(100))
    puesto            = db.Column(db.String(100))
    antiguedad        = db.Column(db.Integer)

    # Coordinaciones
    tipo_entidad_coord = db.Column(db.String(30))
    nombre_coord      = db.Column(db.String(200))
    cargo_coord       = db.Column(db.String(100))

    # Estado de la cuenta
    activo            = db.Column(db.Boolean, default=True)
    empresa_validada  = db.Column(db.Boolean, default=False)
    fecha_registro    = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acceso     = db.Column(db.DateTime)
    aceptar_privacidad= db.Column(db.Boolean, default=False)

    # Autenticacion en dos pasos
    dos_pasos_activo  = db.Column(db.Boolean, default=False)
    dos_pasos_codigo  = db.Column(db.String(10))
    dos_pasos_expiry  = db.Column(db.DateTime)

    # Recuperacion de contrasena
    reset_token       = db.Column(db.String(100))
    reset_token_expiry= db.Column(db.DateTime)

    # Relaciones
    diagnostico = db.relationship('DiagnosticoCompetencias', backref='usuario', uselist=False)
    vacantes_postuladas = db.relationship(
        'Vacante',
        secondary=postulaciones,
        backref='postulantes',
        lazy='dynamic'
    )

    # Metodos
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def nombre_completo(self):
        partes = [self.nombre, self.apellido_paterno]
        if self.apellido_materno:
            partes.append(self.apellido_materno)
        return ' '.join(partes)

    def generar_reset_token(self):
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        return self.reset_token

    def token_reset_valido(self, token):
        return (
            self.reset_token == token
            and self.reset_token_expiry
            and datetime.utcnow() < self.reset_token_expiry
        )

    def generar_codigo_dos_pasos(self):
        import random
        codigo = str(random.randint(100000, 999999))
        self.dos_pasos_codigo = codigo
        self.dos_pasos_expiry = datetime.utcnow() + timedelta(minutes=10)
        return codigo

    def verificar_codigo_dos_pasos(self, codigo):
        return (
            self.dos_pasos_codigo == codigo
            and self.dos_pasos_expiry
            and datetime.utcnow() < self.dos_pasos_expiry
        )

    def verificar_inactividad(self):
        """Suspende la cuenta automaticamente si supera el plazo de inactividad."""
        if self.ultimo_acceso:
            limite = self.ultimo_acceso + timedelta(days=PLAZO_INACTIVIDAD_DIAS)
            if datetime.utcnow() > limite:
                self.activo = False
                return True
        return False

    def __repr__(self):
        return f'<Usuario {self.email} [{self.tipo_usuario}]>'


# ─── Diagnostico de Competencias ────────────────────────────────────────────────
class DiagnosticoCompetencias(db.Model):
    __tablename__ = 'diagnostico_competencias'

    id           = db.Column(db.Integer, primary_key=True)
    usuario_id   = db.Column(db.Integer, db.ForeignKey('usuario.id'), unique=True, nullable=False)

    independencia         = db.Column(db.Float, default=0)
    estimulo              = db.Column(db.Float, default=0)
    liderazgo             = db.Column(db.Float, default=0)
    benevolencia          = db.Column(db.Float, default=0)
    animacion             = db.Column(db.Float, default=0)
    estabilidad           = db.Column(db.Float, default=0)
    inteligencia_emocional= db.Column(db.Float, default=0)
    asertividad           = db.Column(db.Float, default=0)
    trabajo_en_equipo     = db.Column(db.Float, default=0)
    atencion_normas       = db.Column(db.Float, default=0)
    creatividad           = db.Column(db.Float, default=0)
    practicidad           = db.Column(db.Float, default=0)
    facilidad_palabra     = db.Column(db.Float, default=0)
    abstraccion_ideas     = db.Column(db.Float, default=0)
    concentracion         = db.Column(db.Float, default=0)
    analisis_situacional  = db.Column(db.Float, default=0)
    solucion_problemas    = db.Column(db.Float, default=0)
    logica                = db.Column(db.Float, default=0)
    score_global          = db.Column(db.Float, default=0)
    fecha_evaluacion      = db.Column(db.DateTime, default=datetime.utcnow)
    version_cuestionario  = db.Column(db.String(10), default='1.0')

    def calcular_score_global(self):
        competencias = [
            self.liderazgo, self.trabajo_en_equipo, self.inteligencia_emocional,
            self.asertividad, self.independencia, self.creatividad,
            self.practicidad, self.analisis_situacional, self.logica
        ]
        self.score_global = round(sum(competencias) / len(competencias), 2)
        return self.score_global


# ─── Vacante ────────────────────────────────────────────────────────────────────
class Vacante(db.Model):
    __tablename__ = 'vacante'

    id              = db.Column(db.Integer, primary_key=True)
    empleador_id    = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    titulo          = db.Column(db.String(200), nullable=False)
    descripcion     = db.Column(db.Text, nullable=False)
    requisitos      = db.Column(db.Text)
    carrera_requerida    = db.Column(db.String(100))
    experiencia_anos     = db.Column(db.Integer, default=0)
    competencias_requeridas = db.Column(db.Text)
    salario_min     = db.Column(db.Float)
    salario_max     = db.Column(db.Float)
    modalidad       = db.Column(db.String(20))
    ubicacion       = db.Column(db.String(100))
    tipo_contrato   = db.Column(db.String(50))
    activa          = db.Column(db.Boolean, default=True)
    validada        = db.Column(db.Boolean, default=False)
    fecha_publicacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_vencimiento = db.Column(db.DateTime)

    empleador = db.relationship('Usuario', backref='vacantes_publicadas')

    def __repr__(self):
        return f'<Vacante {self.titulo}>'


# ─── Postulacion ─────────────────────────────────────────────────────────────
class Postulacion(db.Model):
    __tablename__ = 'postulacion'

    id          = db.Column(db.Integer, primary_key=True)
    usuario_id  = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    vacante_id  = db.Column(db.Integer, db.ForeignKey('vacante.id'), nullable=False)
    fecha_postulacion = db.Column(db.DateTime, default=datetime.utcnow)
    estado      = db.Column(db.String(20), default='pendiente')
    match_score = db.Column(db.Float)

    usuario = db.relationship('Usuario', backref='historial_postulaciones')
    vacante = db.relationship('Vacante', backref='postulaciones_recibidas')

    def __repr__(self):
        return f'<Postulacion {self.usuario_id} -> {self.vacante_id}>'
