from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from dao.tarea_dao import TareaDAO
from dao.campana_dao import CampanaDAO
from dao.usuario_dao import UsuarioDAO
from entidades.tarea import Tarea
from decorators import requiere_permiso

tareas_bp = Blueprint('tareas', __name__)


@tareas_bp.route('/')
@login_required
@requiere_permiso('tareas')
def index():
    estado = request.args.get('estado')
    busqueda = request.args.get('q', '').strip()
    filtro_usuario_id = request.args.get('usuario_id')

    # Si es admin, ve todas las tareas
    if current_user.es_admin():
        usuarios = UsuarioDAO.listar()  # Lista de usuarios para el filtro
        usuario_filtro = int(filtro_usuario_id) if filtro_usuario_id else None
        tareas = TareaDAO.listar(estado=estado, usuario_id=usuario_filtro, busqueda=busqueda if busqueda else None)
    else:
        # Si es usuario normal, solo ve sus tareas
        usuarios = []
        tareas = TareaDAO.listar(estado=estado, usuario_id=current_user.id, busqueda=busqueda if busqueda else None)

    return render_template('tareas/index.html', tareas=tareas, estado=estado, busqueda=busqueda, usuarios=usuarios)


@tareas_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
@requiere_permiso('tareas', requiere_editar=True)
def nueva():
    if request.method == 'POST':
        usuario_id = request.form.get('usuario_id')
        titulo = (request.form.get('titulo') or '').strip()
        fecha_entrega = request.form.get('fecha_entrega') or None
        if not titulo or not fecha_entrega:
            flash('TÃ­tulo y fecha de entrega son obligatorios.', 'error')
            return redirect(url_for('tareas.nueva'))

        # Si no es admin, forzar que la tarea sea para él mismo
        if not current_user.es_admin():
            usuario_id = current_user.id

        tarea = Tarea(
            id=None,
            titulo=titulo,
            descripcion=request.form.get('descripcion'),
            estado=request.form.get('estado', 'pendiente'),
            prioridad=request.form.get('prioridad', 'media'),
            fecha_entrega=fecha_entrega,
            campana_id=int(request.form['campana_id']) if request.form.get('campana_id') else None,
            usuario_id=int(usuario_id) if usuario_id else None
        )
        TareaDAO.insertar(tarea)
        flash('Tarea creada.', 'success')
        return redirect(url_for('tareas.index'))

    campanas = CampanaDAO.listar()
    usuarios = UsuarioDAO.listar() if current_user.es_admin() else []
    return render_template('tareas/form.html', tarea=None, campanas=campanas, usuarios=usuarios)


@tareas_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@requiere_permiso('tareas', requiere_editar=True)
def editar(id):
    tarea = TareaDAO.obtener(id)

    if not tarea:
        flash('Tarea no encontrada.', 'error')
        return redirect(url_for('tareas.index'))

    # Verificar que el usuario pueda editar esta tarea
    if not current_user.es_admin() and tarea.usuario_id != current_user.id:
        flash('No tienes permiso para editar esta tarea.', 'error')
        return redirect(url_for('tareas.index'))

    if request.method == 'POST':
        usuario_id = request.form.get('usuario_id')
        titulo = (request.form.get('titulo') or '').strip()
        fecha_entrega = request.form.get('fecha_entrega') or None
        if not titulo or not fecha_entrega:
            flash('TÃ­tulo y fecha de entrega son obligatorios.', 'error')
            return redirect(url_for('tareas.editar', id=id))

        # Si no es admin, mantener el usuario actual
        if not current_user.es_admin():
            usuario_id = tarea.usuario_id

        tarea.titulo = titulo
        tarea.descripcion = request.form.get('descripcion')
        tarea.estado = request.form.get('estado', 'pendiente')
        tarea.prioridad = request.form.get('prioridad', 'media')
        tarea.fecha_entrega = fecha_entrega
        tarea.campana_id = int(request.form['campana_id']) if request.form.get('campana_id') else None
        tarea.usuario_id = int(usuario_id) if usuario_id else None

        TareaDAO.actualizar(tarea)
        flash('Tarea actualizada.', 'success')
        return redirect(url_for('tareas.index'))

    campanas = CampanaDAO.listar()
    usuarios = UsuarioDAO.listar() if current_user.es_admin() else []
    return render_template('tareas/form.html', tarea=tarea, campanas=campanas, usuarios=usuarios)


@tareas_bp.route('/postergar/<int:id>', methods=['GET', 'POST'])
@login_required
@requiere_permiso('tareas', requiere_editar=True)
def postergar(id):
    tarea = TareaDAO.obtener(id)

    if not tarea:
        flash('Tarea no encontrada.', 'error')
        return redirect(url_for('tareas.index'))

    # Verificar permisos
    if not current_user.es_admin() and tarea.usuario_id != current_user.id:
        flash('No tienes permiso para postergar esta tarea.', 'error')
        return redirect(url_for('tareas.index'))

    if request.method == 'POST':
        TareaDAO.postergar(
            id=id,
            motivo=request.form['motivo'],
            nueva_fecha=request.form['nueva_fecha']
        )
        flash('Tarea postergada.', 'warning')
        return redirect(url_for('tareas.index'))

    return render_template('tareas/postergar.html', tarea=tarea)


@tareas_bp.route('/eliminar/<int:id>')
@login_required
@requiere_permiso('tareas', requiere_editar=True)
def eliminar(id):
    tarea = TareaDAO.obtener(id)

    if not tarea:
        flash('Tarea no encontrada.', 'error')
        return redirect(url_for('tareas.index'))

    # Verificar permisos
    if not current_user.es_admin() and tarea.usuario_id != current_user.id:
        flash('No tienes permiso para eliminar esta tarea.', 'error')
        return redirect(url_for('tareas.index'))

    TareaDAO.eliminar(id)
    flash('Tarea eliminada.', 'error')
    return redirect(url_for('tareas.index'))


@tareas_bp.route('/completar/<int:id>')
@login_required
@requiere_permiso('tareas', requiere_editar=True)
def completar(id):
    tarea = TareaDAO.obtener(id)

    if not tarea:
        flash('Tarea no encontrada.', 'error')
        return redirect(url_for('tareas.index'))

    # Verificar permisos
    if not current_user.es_admin() and tarea.usuario_id != current_user.id:
        flash('No tienes permiso para completar esta tarea.', 'error')
        return redirect(url_for('tareas.index'))

    TareaDAO.cambiar_estado(id, 'completada')
    flash('Tarea marcada como completada.', 'success')
    return redirect(url_for('tareas.index'))
