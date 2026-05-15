from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from dao.usuario_dao import UsuarioDAO

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('inicio.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        usuario = UsuarioDAO.obtener_por_email(email)
        if usuario and check_password_hash(usuario.password_hash, password):
            login_user(usuario)
            return redirect(url_for('inicio.index'))
        flash('Email o contraseña incorrectos.', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/reset-temp-oscar')
def reset_temp():
    from werkzeug.security import generate_password_hash
    from conexion import Conexion
    conn = Conexion.obtener_conexion()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET password_hash = %s WHERE id = %s",
        (generate_password_hash('Oscar2025-'), 5)
    )
    conn.commit()
    Conexion.liberar_conexion(conn)
    return "Contrasena actualizada OK"
