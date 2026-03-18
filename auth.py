"""
auth.py — Blueprint de autenticación BTU-UASLP
Maneja: registro por tipo, login, 2FA, recuperación de contraseña, logout
"""
import os
from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, session, current_app
)
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename

from app import db, login_manager
from app.models import Usuario, TIPOS_VALIDOS

auth = Blueprint('auth', __name__, url_prefix='/auth')


# ── Loader de usuario para flask-login ────────────────────────────────────────
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


# ── Helper: extensión de archivo permitida ────────────────────────────────────
ALLOWED_CV_EXTENSIONS = {'pdf', 'doc', 'docx'}

def _cv_permitido(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_CV_EXTENSIONS


# ── Helper: guardar CV ─────────────────────────────────────────────────────────
def _guardar_cv(archivo, clave_unica):
    if archivo and _cv_permitido(archivo.filename):
        ext = archivo.filename.rsplit('.', 1)[1].lower()
        filename = secure_filename(f"cv_{clave_unica}.{ext}")
        ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        archivo.save(ruta)
        return filename
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# MODAL / SELECTOR DE TIPO DE REGISTRO  (GET /auth/registro)
# ═══════════════════════════════════════════════════════════════════════════════
@auth.route('/registro')
def registro_selector():
    """Muestra la página con las opciones de tipo de registro."""
    return render_template('auth/registro_selector.html')


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRO ALUMNO
# ═══════════════════════════════════════════════════════════════════════════════
@auth.route('/registro/alumno', methods=['GET', 'POST'])
def registro_alumno():
    if request.method == 'POST':
        datos = request.form
        error = _validar_email_clave(datos.get('email'), datos.get('clave_unica'))
        if error:
            flash(error, 'danger')
            return render_template('auth/registro_alumno.html')

        usuario = Usuario(
            tipo_usuario     = 'alumno',
            clave_unica      = datos.get('clave_unica'),
            email            = datos.get('email'),
            nombre           = datos.get('nombre'),
            apellido_paterno = datos.get('apellido_paterno'),
            apellido_materno = datos.get('apellido_materno'),
            edad             = _int(datos.get('edad')),
            sexo             = datos.get('sexo'),
            telefono         = datos.get('telefono'),
            carrera          = datos.get('carrera'),
            semestre         = _int(datos.get('semestre')),
            modalidad_estudio= datos.get('modalidad_estudio'),
            facultad         = datos.get('facultad'),
            area             = datos.get('area'),
            programa_academico = datos.get('programa_academico'),
            aceptar_privacidad = bool(datos.get('aceptar_privacidad')),
            fecha_registro   = datetime.utcnow(),
        )
        usuario.set_password(datos.get('password'))

        cv_file = request.files.get('cv')
        if cv_file:
            usuario.cv_filename = _guardar_cv(cv_file, usuario.clave_unica)

        db.session.add(usuario)
        db.session.commit()
        flash('Registro de alumno exitoso. Por favor inicia sesión.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/registro_alumno.html')


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRO EGRESADO
# ═══════════════════════════════════════════════════════════════════════════════
@auth.route('/registro/egresado', methods=['GET', 'POST'])
def registro_egresado():
    if request.method == 'POST':
        datos = request.form
        error = _validar_email_clave(datos.get('email'), datos.get('clave_unica'))
        if error:
            flash(error, 'danger')
            return render_template('auth/registro_egresado.html')

        usuario = Usuario(
            tipo_usuario      = 'egresado',
            clave_unica       = datos.get('clave_unica'),
            email             = datos.get('email'),
            nombre            = datos.get('nombre'),
            apellido_paterno  = datos.get('apellido_paterno'),
            apellido_materno  = datos.get('apellido_materno'),
            edad              = _int(datos.get('edad')),
            sexo              = datos.get('sexo'),
            telefono          = datos.get('telefono'),
            carrera           = datos.get('carrera'),
            facultad          = datos.get('facultad'),
            anio_egreso       = _int(datos.get('anio_egreso')),
            cedula_profesional= datos.get('cedula_profesional'),
            nombre_empresa    = datos.get('nombre_empresa'),
            puesto            = datos.get('puesto'),
            experiencia_laboral  = datos.get('experiencia_laboral'),
            certificaciones   = datos.get('certificaciones'),
            especializaciones = datos.get('especializaciones'),
            aceptar_privacidad= bool(datos.get('aceptar_privacidad')),
            fecha_registro    = datetime.utcnow(),
        )
        usuario.set_password(datos.get('password'))

        cv_file = request.files.get('cv')
        if cv_file:
            usuario.cv_filename = _guardar_cv(cv_file, usuario.clave_unica)

        db.session.add(usuario)
        db.session.commit()
        flash('Registro de egresado exitoso. Por favor inicia sesión.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/registro_egresado.html')


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRO PERSONA EXTERNA (Mexicana o Extranjera)
# ═══════════════════════════════════════════════════════════════════════════════
@auth.route('/registro/persona/<nacionalidad>', methods=['GET', 'POST'])
def registro_persona(nacionalidad):
    if nacionalidad not in ('mexicana', 'extranjera'):
        return redirect(url_for('auth.registro_selector'))

    tipo = 'persona_mexicana' if nacionalidad == 'mexicana' else 'persona_extranjera'

    if request.method == 'POST':
        datos = request.form
        error = _validar_email_clave(datos.get('email'), datos.get('clave_unica'))
        if error:
            flash(error, 'danger')
            return render_template('auth/registro_persona.html', nacionalidad=nacionalidad)

        usuario = Usuario(
            tipo_usuario      = tipo,
            clave_unica       = datos.get('clave_unica'),
            email             = datos.get('email'),
            nombre            = datos.get('nombre'),
            apellido_paterno  = datos.get('apellido_paterno'),
            apellido_materno  = datos.get('apellido_materno'),
            edad              = _int(datos.get('edad')),
            sexo              = datos.get('sexo'),
            telefono          = datos.get('telefono'),
            nacionalidad      = datos.get('nacionalidad_texto'),
            pais_origen       = datos.get('pais_origen'),
            aceptar_privacidad= bool(datos.get('aceptar_privacidad')),
            fecha_registro    = datetime.utcnow(),
        )
        usuario.set_password(datos.get('password'))

        db.session.add(usuario)
        db.session.commit()
        flash('Registro exitoso. Por favor inicia sesión.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/registro_persona.html', nacionalidad=nacionalidad)


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRO EMPRESA / EMPLEADOR
# ═══════════════════════════════════════════════════════════════════════════════
@auth.route('/registro/empresa', methods=['GET', 'POST'])
def registro_empresa():
    if request.method == 'POST':
        datos = request.form
        error = _validar_email_clave(datos.get('email'), datos.get('clave_unica'))
        if error:
            flash(error, 'danger')
            return render_template('auth/registro_empresa.html')

        usuario = Usuario(
            tipo_usuario      = 'empresa',
            clave_unica       = datos.get('clave_unica'),
            email             = datos.get('email'),
            nombre            = datos.get('nombre_contacto'),
            apellido_paterno  = datos.get('apellido_paterno'),
            apellido_materno  = datos.get('apellido_materno'),
            telefono          = datos.get('telefono'),
            nombre_empresa    = datos.get('nombre_empresa'),
            rfc_empresa       = datos.get('rfc_empresa'),
            giro_empresa      = datos.get('giro_empresa'),
            puesto            = datos.get('puesto'),
            empresa_validada  = False,   # requiere validacion por la universidad
            aceptar_privacidad= bool(datos.get('aceptar_privacidad')),
            fecha_registro    = datetime.utcnow(),
        )
        usuario.set_password(datos.get('password'))

        db.session.add(usuario)
        db.session.commit()
        flash('Solicitud de empresa enviada. Pendiente de validación por la UASLP.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/registro_empresa.html')


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRO COORDINACION
# ═══════════════════════════════════════════════════════════════════════════════
@auth.route('/registro/coordinacion', methods=['GET', 'POST'])
def registro_coordinacion():
    if request.method == 'POST':
        datos = request.form
        error = _validar_email_clave(datos.get('email'), datos.get('clave_unica'))
        if error:
            flash(error, 'danger')
            return render_template('auth/registro_coordinacion.html')

        usuario = Usuario(
            tipo_usuario       = 'coordinacion',
            clave_unica        = datos.get('clave_unica'),
            email              = datos.get('email'),
            nombre             = datos.get('nombre'),
            apellido_paterno   = datos.get('apellido_paterno'),
            apellido_materno   = datos.get('apellido_materno'),
            telefono           = datos.get('telefono'),
            tipo_entidad_coord = datos.get('tipo_entidad'),   # facultad | area | programa
            nombre_coord       = datos.get('nombre_coord'),
            facultad           = datos.get('facultad'),
            area               = datos.get('area'),
            programa_academico = datos.get('programa_academico'),
            cargo_coord        = datos.get('cargo'),
            aceptar_privacidad = bool(datos.get('aceptar_privacidad')),
            fecha_registro     = datetime.utcnow(),
        )
        usuario.set_password(datos.get('password'))

        db.session.add(usuario)
        db.session.commit()
        flash('Registro de coordinación exitoso. Por favor inicia sesión.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/registro_coordinacion.html')


# ═══════════════════════════════════════════════════════════════════════════════
# LOGIN
# ═══════════════════════════════════════════════════════════════════════════════
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        usuario = Usuario.query.filter_by(email=email).first()

        if not usuario or not usuario.check_password(password):
            flash('Correo o contraseña incorrectos.', 'danger')
            return render_template('auth/login.html')

        # Verificar inactividad (baja automatica)
        if usuario.verificar_inactividad():
            db.session.commit()
            flash('Tu cuenta fue suspendida por inactividad. Contacta a la coordinación.', 'warning')
            return render_template('auth/login.html')

        if not usuario.activo:
            flash('Tu cuenta está suspendida. Contacta a la coordinación.', 'warning')
            return render_template('auth/login.html')

        # ── Verificación en dos pasos ─────────────────────────────────────────
        if usuario.dos_pasos_activo:
            codigo = usuario.generar_codigo_dos_pasos()
            db.session.commit()
            # En produccion se enviaría por correo/SMS.
            # Para desarrollo: se muestra en flash (cambiar en produccion)
            flash(f'[DEV] Tu código de verificación es: {codigo}', 'info')
            session['dos_pasos_usuario_id'] = usuario.id
            return redirect(url_for('auth.verificar_dos_pasos'))

        # Login normal
        usuario.ultimo_acceso = datetime.utcnow()
        db.session.commit()
        login_user(usuario)

        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.dashboard'))

    return render_template('auth/login.html')


# ═══════════════════════════════════════════════════════════════════════════════
# VERIFICACION EN DOS PASOS
# ═══════════════════════════════════════════════════════════════════════════════
@auth.route('/verificar-dos-pasos', methods=['GET', 'POST'])
def verificar_dos_pasos():
    usuario_id = session.get('dos_pasos_usuario_id')
    if not usuario_id:
        return redirect(url_for('auth.login'))

    usuario = Usuario.query.get(usuario_id)

    if request.method == 'POST':
        codigo = request.form.get('codigo', '').strip()
        if usuario and usuario.verificar_codigo_dos_pasos(codigo):
            usuario.ultimo_acceso = datetime.utcnow()
            db.session.commit()
            session.pop('dos_pasos_usuario_id', None)
            login_user(usuario)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Código incorrecto o expirado.', 'danger')

    return render_template('auth/verificar_dos_pasos.html')


# ═══════════════════════════════════════════════════════════════════════════════
# RECUPERACION DE CONTRASENA
# ═══════════════════════════════════════════════════════════════════════════════
@auth.route('/recuperar', methods=['GET', 'POST'])
def recuperar_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario:
            token = usuario.generar_reset_token()
            db.session.commit()
            enlace = url_for('auth.reset_password', token=token, _external=True)
            # En produccion se enviaría por correo; en dev se muestra en flash.
            flash(f'[DEV] Enlace de recuperación: {enlace}', 'info')
        else:
            # Mismo mensaje para no revelar si el correo existe
            flash('Si el correo está registrado recibirás un enlace de recuperación.', 'info')

        return redirect(url_for('auth.login'))

    return render_template('auth/recuperar_password.html')


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    usuario = Usuario.query.filter_by(reset_token=token).first()

    if not usuario or not usuario.token_reset_valido(token):
        flash('El enlace de recuperación es inválido o ha expirado.', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        nueva = request.form.get('password', '')
        confirmar = request.form.get('confirm_password', '')

        if nueva != confirmar:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('auth/reset_password.html', token=token)

        if len(nueva) < 8:
            flash('La contraseña debe tener al menos 8 caracteres.', 'danger')
            return render_template('auth/reset_password.html', token=token)

        usuario.set_password(nueva)
        usuario.reset_token = None
        usuario.reset_token_expiry = None
        db.session.commit()

        flash('Contraseña actualizada correctamente. Por favor inicia sesión.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token)


# ═══════════════════════════════════════════════════════════════════════════════
# LOGOUT
# ═══════════════════════════════════════════════════════════════════════════════
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('main.index'))


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS PRIVADOS
# ═══════════════════════════════════════════════════════════════════════════════
def _validar_email_clave(email, clave):
    if Usuario.query.filter_by(email=email).first():
        return 'El correo electrónico ya está registrado.'
    if Usuario.query.filter_by(clave_unica=clave).first():
        return 'La clave única ya está registrada.'
    return None

def _int(valor):
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None
