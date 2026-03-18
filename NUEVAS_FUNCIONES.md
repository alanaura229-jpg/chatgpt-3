# BTU-UASLP — Nuevas Funciones Agregadas

## Archivos NUEVOS (no se modificó nada del proyecto original excepto lo estrictamente necesario)

### Python / Backend
| Archivo | Descripción |
|---------|-------------|
| `app/auth.py` | **Nuevo blueprint** con todos los flujos de registro y autenticación |
| `app/models.py` | Modelo `Usuario` ampliado con todos los campos nuevos |
| `app/__init__.py` | Actualizado para soportar MySQL y registrar el blueprint `auth` |
| `app/routes.py` | Actualizado con dashboards por tipo de usuario, postulaciones y perfil |
| `run.py` | Actualizado para usar el app factory |
| `requirements.txt` | Agrega `PyMySQL` para conexión MySQL |

### Templates NUEVOS
| Template | Descripción |
|----------|-------------|
| `templates/auth/base_auth.html` | Layout base con estilo BTU-UASLP para todas las páginas de auth |
| `templates/auth/login.html` | Login con enlace a recuperación y registro |
| `templates/auth/registro_selector.html` | Página de selección de tipo de registro (6 opciones) |
| `templates/auth/registro_alumno.html` | Formulario completo de registro de alumno + CV |
| `templates/auth/registro_egresado.html` | Formulario completo de egresado con perfil profesional + CV |
| `templates/auth/registro_persona.html` | Registro para personas mexicanas y extranjeras |
| `templates/auth/registro_empresa.html` | Registro de empresa con validación pendiente |
| `templates/auth/registro_coordinacion.html` | Registro de Facultad / Área / Programa Académico |
| `templates/auth/verificar_dos_pasos.html` | Verificación de código 2FA |
| `templates/auth/recuperar_password.html` | Solicitud de recuperación de contraseña |
| `templates/auth/reset_password.html` | Formulario de nueva contraseña con token |
| `templates/dashboard_usuario.html` | Panel para alumnos, egresados y personas |
| `templates/dashboard_empresa.html` | Panel para empresas (vacantes publicadas, estado de validación) |
| `templates/dashboard_coordinacion.html` | Panel para coordinaciones (directorio con filtros) |
| `templates/perfil.html` | Perfil editable con CV, 2FA y datos profesionales |
| `templates/vacante_nueva.html` | Formulario de publicación de vacantes |

### Otros archivos
| Archivo | Descripción |
|---------|-------------|
| `.env.example` | Plantilla de variables de entorno |
| `mysql_setup.sql` | Script SQL para crear la BD en MySQL |
| `static/uploads/cvs/` | Carpeta donde se almacenan los CVs subidos |

---

## Tipos de usuario implementados

| Tipo | Clave interna | Descripción |
|------|--------------|-------------|
| Alumno | `alumno` | Estudiante activo UASLP, con carrera/semestre/modalidad/CV |
| Egresado | `egresado` | Con perfil profesional ampliado, certificaciones y CV |
| Persona Mexicana | `persona_mexicana` | Ciudadano mexicano externo a la UASLP |
| Persona Extranjera | `persona_extranjera` | Ciudadano extranjero, con campos de nacionalidad/país |
| Empresa | `empresa` | Registro con RFC, giro; requiere validación de la UASLP |
| Coordinación | `coordinacion` | Facultad / Área / Programa, con filtro por tipo de entidad |
| Admin | `admin` | Reservado para administradores (alta manual) |

---

## Funcionalidades de autenticación

- **Login**: `/auth/login`
- **Registro** (selector): `/auth/registro`
- **Verificación en dos pasos**: código de 6 dígitos por correo, vigente 10 min
  - Se activa/desactiva desde el perfil del usuario
- **Recuperación de contraseña**: token seguro, vigente 1 hora
- **Baja automática**: se suspende la cuenta al superar 180 días de inactividad

---

## Perfiles de usuario

### Alumnos y personas
- Carga y actualización de CV (PDF/DOC/DOCX, máx 5 MB)
- Filtros por carrera, semestre y modalidad en el dashboard
- Postulación en línea a vacantes
- Historial de postulaciones con estado

### Egresados
- Perfil profesional con empresa actual, puesto, experiencia laboral
- Certificaciones y especializaciones editables
- Carga de CV editable

### Empresas / Empleadores
- Registro validado por la universidad (flag `empresa_validada`)
- Publicación de vacantes con autorización previa (`validada=False` hasta aprobación)
- Dashboard con conteo de postulantes por vacante

### Coordinaciones
- Directorio de alumnos y egresados con búsqueda y filtro por tipo
- Visualización de estado de cuentas (activa/suspendida)

---

## Configuración MySQL

### 1. Crear BD y usuario
```bash
mysql -u root -p < mysql_setup.sql
```

### 2. Configurar .env
```bash
cp .env.example .env
# Editar .env con tus credenciales:
MYSQL_URI=mysql+pymysql://btu_user:CambiaEstaPassword123!@localhost:3306/btu_uaslp
SECRET_KEY=una-clave-secreta-larga-y-aleatoria
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar
```bash
python run.py
```
Las tablas se crean automáticamente al arrancar la app.

---

## Rutas principales

| Ruta | Descripción |
|------|-------------|
| `/` | Página de inicio |
| `/auth/login` | Inicio de sesión |
| `/auth/registro` | Selector de tipo de registro |
| `/auth/registro/alumno` | Formulario alumno |
| `/auth/registro/egresado` | Formulario egresado |
| `/auth/registro/persona/mexicana` | Persona mexicana |
| `/auth/registro/persona/extranjera` | Persona extranjera |
| `/auth/registro/empresa` | Empresa / empleador |
| `/auth/registro/coordinacion` | Coordinación |
| `/auth/recuperar` | Recuperación de contraseña |
| `/auth/logout` | Cerrar sesión |
| `/dashboard` | Panel según tipo de usuario |
| `/perfil` | Editar perfil y CV |
| `/postular/<id>` | Postularse a una vacante |
| `/vacante/nueva` | Publicar vacante (solo empresas validadas) |
