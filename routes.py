from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db
from models import Usuario, Vacante, DiagnosticoCompetencias, Postulacion
from forms import VacanteForm
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename

main = Blueprint('main', __name__)


# ── Rutas públicas ─────────────────────────────────────────────────────────────

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/vacantes')
def vacantes():
    vacantes_list = Vacante.query.filter_by(activa=True, validada=True).all()
    return render_template('vacantes.html', vacantes=vacantes_list)

@main.route('/diagnostico')
def diagnostico():
    return render_template('Diagnostico.html')

@main.route('/empresas')
def empresas():
    return render_template('Empresas.html')

@main.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')

@main.route('/estudiantes')
def estudiantes():
    return render_template('estudiantes.html')

@main.route('/egresados')
def egresados():
    return render_template('egresados.html')

@main.route('/empleadores')
def empleadores():
    return render_template('empleadores.html')

@main.route('/coordinaciones')
def coordinaciones():
    return render_template('coordinaciones.html')

@main.route('/preguntas')
def preguntas():
    return render_template('preguntas.html')


# ── Dashboard ──────────────────────────────────────────────────────────────────

@main.route('/dashboard')
@login_required
def dashboard():
    tipo = current_user.tipo_usuario

    if tipo == 'empresa':
        vacantes = Vacante.query.filter_by(empleador_id=current_user.id).all()
        return render_template('dashboard_empresa.html', vacantes=vacantes)

    elif tipo in ('alumno', 'egresado', 'persona_mexicana', 'persona_extranjera'):
        vacantes_activas = Vacante.query.filter_by(activa=True, validada=True).all()
        tiene_diagnostico = DiagnosticoCompetencias.query.filter_by(
            usuario_id=current_user.id
        ).first() is not None
        historial = Postulacion.query.filter_by(usuario_id=current_user.id).all()
        return render_template(
            'dashboard_usuario.html',
            vacantes=vacantes_activas,
            tiene_diagnostico=tiene_diagnostico,
            historial=historial,
        )

    elif tipo == 'coordinacion':
        usuarios = Usuario.query.filter(
            Usuario.tipo_usuario.in_(['alumno', 'egresado'])
        ).all()
        return render_template('dashboard_coordinacion.html', usuarios=usuarios)

    return render_template('dashboard.html')


# ── Perfil ─────────────────────────────────────────────────────────────────────

@main.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    if request.method == 'POST':
        # Actualizar campos básicos editables
        current_user.telefono = request.form.get('telefono', current_user.telefono)
        current_user.nombre_empresa = request.form.get('nombre_empresa', current_user.nombre_empresa)
        current_user.puesto = request.form.get('puesto', current_user.puesto)
        current_user.experiencia_laboral = request.form.get('experiencia_laboral', current_user.experiencia_laboral)
        current_user.certificaciones = request.form.get('certificaciones', current_user.certificaciones)
        current_user.especializaciones = request.form.get('especializaciones', current_user.especializaciones)

        # Actualizar CV
        cv_file = request.files.get('cv')
        if cv_file and cv_file.filename:
            from flask import current_app
            ext = cv_file.filename.rsplit('.', 1)[-1].lower()
            if ext in ('pdf', 'doc', 'docx'):
                filename = secure_filename(f"cv_{current_user.clave_unica}.{ext}")
                ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                cv_file.save(ruta)
                current_user.cv_filename = filename

        # Activar/desactivar 2FA
        dos_pasos = request.form.get('dos_pasos_activo')
        current_user.dos_pasos_activo = dos_pasos == 'on'

        db.session.commit()
        flash('Perfil actualizado correctamente.', 'success')
        return redirect(url_for('main.perfil'))

    return render_template('perfil.html')


# ── Postulaciones ──────────────────────────────────────────────────────────────

@main.route('/postular/<int:vacante_id>', methods=['POST'])
@login_required
def postular(vacante_id):
    if current_user.tipo_usuario not in ('alumno', 'egresado', 'persona_mexicana', 'persona_extranjera'):
        flash('Solo los candidatos pueden postularse a vacantes.', 'warning')
        return redirect(url_for('main.vacantes'))

    vacante = Vacante.query.get_or_404(vacante_id)
    ya_postulado = Postulacion.query.filter_by(
        usuario_id=current_user.id, vacante_id=vacante_id
    ).first()

    if ya_postulado:
        flash('Ya te postulaste a esta vacante.', 'info')
    else:
        p = Postulacion(usuario_id=current_user.id, vacante_id=vacante_id)
        db.session.add(p)
        db.session.commit()
        flash(f'Postulación enviada a: {vacante.titulo}', 'success')

    return redirect(url_for('main.vacantes'))


# ── Vacantes (empleadores) ─────────────────────────────────────────────────────

@main.route('/vacante/nueva', methods=['GET', 'POST'])
@login_required
def nueva_vacante():
    if current_user.tipo_usuario != 'empresa':
        flash('Solo las empresas pueden publicar vacantes.', 'warning')
        return redirect(url_for('main.index'))

    if not current_user.empresa_validada:
        flash('Tu empresa aún no ha sido validada por la UASLP.', 'warning')
        return redirect(url_for('main.dashboard'))

    form = VacanteForm()
    if form.validate_on_submit():
        vacante = Vacante(
            empleador_id=current_user.id,
            titulo=form.titulo.data,
            descripcion=form.descripcion.data,
            requisitos=form.requisitos.data,
            carrera_requerida=form.carrera_requerida.data,
            experiencia_anos=form.experiencia_anos.data,
            salario_min=form.salario_min.data,
            salario_max=form.salario_max.data,
            modalidad=form.modalidad.data,
            ubicacion=form.ubicacion.data,
            tipo_contrato=form.tipo_contrato.data,
            fecha_vencimiento=datetime.utcnow() + timedelta(days=30),
            validada=False,
        )
        db.session.add(vacante)
        db.session.commit()
        flash('Vacante enviada. Pendiente de validación.', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('vacante_nueva.html', form=form)
