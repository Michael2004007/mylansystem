from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user
from dao.permiso_dao import PermisoDAO


def requiere_permiso(modulo, requiere_editar=False, requiere_aprobar=False):
    """
    Decorator para verificar permisos de usuario en un módulo.

    Uso:
    @requiere_permiso('tareas')  # Solo ver
    @requiere_permiso('tareas', requiere_editar=True)  # Ver y editar
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Debes iniciar sesión.', 'error')
                return redirect(url_for('auth.login'))

            # Los admins tienen acceso total
            if current_user.es_admin():
                return func(*args, **kwargs)

            # Verificar permiso específico
            tiene_acceso = PermisoDAO.tiene_permiso(
                current_user.id,
                modulo,
                requiere_editar=requiere_editar,
                requiere_aprobar=requiere_aprobar
            )

            if not tiene_acceso:
                flash('No tienes permisos para acceder a este módulo.', 'error')
                return redirect(url_for('inicio.index'))

            return func(*args, **kwargs)

        return wrapper

    return decorator


def solo_admin(func):
    """
    Decorator para rutas que solo pueden acceder administradores.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Debes iniciar sesión.', 'error')
            return redirect(url_for('auth.login'))

        if not current_user.es_admin():
            flash('Solo los administradores pueden acceder a esta sección.', 'error')
            return redirect(url_for('inicio.index'))

        return func(*args, **kwargs)

    return wrapper
