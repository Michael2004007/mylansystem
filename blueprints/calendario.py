from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from dao.calendario_dao import CalendarioDAO
from dao.campana_dao import CampanaDAO

calendario_bp = Blueprint('calendario', __name__)


@calendario_bp.route('/')
@login_required
def index():
    anio      = request.args.get('anio', type=int, default=2026)
    eventos   = CalendarioDAO.listar_anio(anio)
    destacados = CalendarioDAO.listar_destacados(anio)
    campanas  = CampanaDAO.listar()
    return render_template('calendario/index.html',
                           eventos=eventos, anio=anio,
                           campanas=campanas, destacados=destacados)


@calendario_bp.route('/mes/<int:mes>')
@login_required
def mes(mes):
    anio     = request.args.get('anio', type=int, default=2026)
    eventos  = CalendarioDAO.listar_por_mes(mes, anio)
    campanas = CampanaDAO.listar()
    return render_template('calendario/mes.html',
                           eventos=eventos, mes=mes, anio=anio, campanas=campanas)


@calendario_bp.route('/nuevo', methods=['POST'])
@login_required
def nuevo():
    fecha     = request.form.get('fecha')
    nombre    = (request.form.get('nombre') or '').strip()
    tipo      = request.form.get('tipo')
    accion    = request.form.get('accion_sugerida')
    campana   = request.form.get('campana_id') or None
    destacado = 1 if request.form.get('destacado') else 0
    color     = request.form.get('color') or None

    fecha_dt = datetime.strptime(fecha, '%Y-%m-%d')

    CalendarioDAO.insertar(
        nombre          = nombre,
        fecha           = fecha,
        tipo            = tipo,
        accion_sugerida = accion,
        campana_id      = campana,
        destacado       = destacado,
        color           = color
    )
    flash('Evento creado.', 'success')
    if destacado:
        return redirect(url_for('calendario.index', anio=fecha_dt.year))
    return redirect(url_for('calendario.mes', mes=fecha_dt.month, anio=fecha_dt.year))

@calendario_bp.route('/editar/<int:id>', methods=['POST'])
@login_required
def editar(id):
    fecha   = request.form.get('fecha')
    nombre  = (request.form.get('nombre') or '').strip()
    tipo    = request.form.get('tipo')
    accion  = request.form.get('accion_sugerida')
    campana = request.form.get('campana_id') or None

    fecha_dt = datetime.strptime(fecha, '%Y-%m-%d')

    CalendarioDAO.actualizar(
        id              = id,
        nombre          = nombre,
        fecha           = fecha,
        tipo            = tipo,
        accion_sugerida = accion,
        campana_id      = campana
    )
    flash('Evento actualizado.', 'success')
    return redirect(url_for('calendario.mes', mes=fecha_dt.month, anio=fecha_dt.year))


@calendario_bp.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    CalendarioDAO.eliminar(id)
    flash('Evento eliminado.', 'error')
    return redirect(request.referrer or url_for('calendario.index'))
    if not fecha or not nombre or not tipo:
        flash('Completá nombre, fecha y tipo del evento.', 'error')
        return redirect(request.referrer or url_for('calendario.index'))

    if not fecha or not nombre or not tipo:
        flash('Completá nombre, fecha y tipo del evento.', 'error')
        return redirect(request.referrer or url_for('calendario.index'))
