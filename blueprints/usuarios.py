from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from dao.usuario_dao import UsuarioDAO
from dao.permiso_dao import PermisoDAO
from entidades.usuario import Usuario
from decorators import solo_admin

usuarios_bp = Blueprint('usuarios', __name__)

MODULOS_DISPONIBLES = [
    {'id': 'inicio', 'nombre': 'Inicio'},
    {'id': 'tareas', 'nombre': 'Tareas'},
    {'id': 'campanas', 'nombre': 'Campanas'},
    {'id': 'ideas_campanas', 'nombre': 'Ideas de campanas'},
    {'id': 'calendario', 'nombre': 'Calendario'},
    {'id': 'influencers', 'nombre': 'Influencers'},
    {'id': 'ecommerce', 'nombre': 'Ecommerce'},
    {'id': 'reportes', 'nombre': 'Reportes'},
    {'id': 'usuarios', 'nombre': 'Usuarios'}
]


@usuarios_bp.route('/')
@login_required
@solo_admin
def index():
    return render_template('usuarios/index.html', usuarios=UsuarioDAO.listar())


@usuarios_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@solo_admin
def nuevo():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        rol = request.form.get('rol', 'usuario')
        activo = request.form.get('activo') == 'on'

        if not nombre or not email or not password:
            flash('Nombre, email y contrasena son obligatorios.', 'error')
            return redirect(url_for('usuarios.nuevo'))
        if UsuarioDAO.existe_email(email):
            flash('El email ya esta registrado.', 'error')
            return redirect(url_for('usuarios.nuevo'))
        if len(password) < 6:
            flash('La contrasena debe tener al menos 6 caracteres.', 'error')
            return redirect(url_for('usuarios.nuevo'))

        usuario_id = UsuarioDAO.insertar(
            Usuario(nombre=nombre, email=email, rol=rol, activo=activo),
            password
        )
        if not usuario_id:
            flash('Error al crear el usuario.', 'error')
            return redirect(url_for('usuarios.nuevo'))

        if rol == 'admin':
            PermisoDAO.asignar_todos_permisos(usuario_id)
        else:
            modulos = request.form.getlist('modulos')
            edita = request.form.getlist('puede_editar')
            aprueba = request.form.getlist('puede_aprobar')
            for modulo in modulos:
                PermisoDAO.asignar_permiso(
                    usuario_id, modulo, True, modulo in edita, modulo in aprueba
                )

        flash('Usuario creado exitosamente.', 'success')
        return redirect(url_for('usuarios.index'))

    return render_template('usuarios/form.html', usuario=None, modulos=MODULOS_DISPONIBLES)


@usuarios_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@solo_admin
def editar(id):
    usuario = UsuarioDAO.obtener(id)
    if not usuario:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('usuarios.index'))

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        rol = request.form.get('rol', 'usuario')
        activo = request.form.get('activo') == 'on'

        if not nombre or not email:
            flash('Nombre y email son obligatorios.', 'error')
            return redirect(url_for('usuarios.editar', id=id))
        if UsuarioDAO.existe_email(email, excluir_id=id):
            flash('El email ya esta registrado por otro usuario.', 'error')
            return redirect(url_for('usuarios.editar', id=id))
        if password and len(password) < 6:
            flash('La contrasena debe tener al menos 6 caracteres.', 'error')
            return redirect(url_for('usuarios.editar', id=id))

        usuario.nombre = nombre
        usuario.email = email
        usuario.rol = rol
        usuario.activo = activo
        UsuarioDAO.actualizar(usuario, password if password else None)

        PermisoDAO.eliminar_permisos_usuario(id)
        if rol == 'admin':
            PermisoDAO.asignar_todos_permisos(id)
        else:
            modulos = request.form.getlist('modulos')
            edita = request.form.getlist('puede_editar')
            aprueba = request.form.getlist('puede_aprobar')
            for modulo in modulos:
                PermisoDAO.asignar_permiso(
                    id, modulo, True, modulo in edita, modulo in aprueba
                )

        flash('Usuario actualizado exitosamente.', 'success')
        return redirect(url_for('usuarios.index'))

    permisos = PermisoDAO.obtener_permisos_usuario(id)
    permisos_dict = {p.modulo: p for p in permisos}
    return render_template('usuarios/form.html', usuario=usuario, modulos=MODULOS_DISPONIBLES, permisos_dict=permisos_dict)


@usuarios_bp.route('/eliminar/<int:id>')
@login_required
@solo_admin
def eliminar(id):
    if current_user.id == id:
        flash('No puedes eliminar tu propio usuario.', 'error')
        return redirect(url_for('usuarios.index'))
    UsuarioDAO.eliminar(id)
    flash('Usuario eliminado.', 'error')
    return redirect(url_for('usuarios.index'))


@usuarios_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    usuario = UsuarioDAO.obtener(current_user.id)
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        password_actual = request.form.get('password_actual', '').strip()
        password_nueva = request.form.get('password_nueva', '').strip()
        password_confirmar = request.form.get('password_confirmar', '').strip()

        if not nombre or not email:
            flash('Nombre y email son obligatorios.', 'error')
            return redirect(url_for('usuarios.perfil'))
        if UsuarioDAO.existe_email(email, excluir_id=current_user.id):
            flash('El email ya esta registrado por otro usuario.', 'error')
            return redirect(url_for('usuarios.perfil'))

        if password_nueva:
            if not password_actual or not UsuarioDAO.verificar_password(usuario, password_actual):
                flash('Contrasena actual incorrecta.', 'error')
                return redirect(url_for('usuarios.perfil'))
            if len(password_nueva) < 6 or password_nueva != password_confirmar:
                flash('Revisa la nueva contrasena.', 'error')
                return redirect(url_for('usuarios.perfil'))
            usuario.nombre = nombre
            usuario.email = email
            UsuarioDAO.actualizar(usuario, password_nueva)
            flash('Perfil y contrasena actualizados.', 'success')
        else:
            usuario.nombre = nombre
            usuario.email = email
            UsuarioDAO.actualizar(usuario)
            flash('Perfil actualizado.', 'success')
        return redirect(url_for('usuarios.perfil'))

    return render_template('usuarios/perfil.html', usuario=usuario)
