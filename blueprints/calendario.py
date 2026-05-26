from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from dao.calendario_dao import CalendarioDAO
from dao.campana_dao import CampanaDAO

calendario_bp = Blueprint('calendario', __name__)


@calendario_bp.route('/')
@login_required
def index():
    anio = request.args.get('anio', type=int, default=2026)
    eventos = CalendarioDAO.listar_anio(anio)
    destacados = CalendarioDAO.listar_destacados(anio)
    campanas = CampanaDAO.listar()
    return render_template(
        'calendario/index.html',
        eventos=eventos,
        anio=anio,
        campanas=campanas,
        destacados=destacados,
    )


@calendario_bp.route('/mes/<int:mes>')
@login_required
def mes(mes):
    anio = request.args.get('anio', type=int, default=2026)
    eventos = CalendarioDAO.listar_por_mes(mes, anio)
    campanas = CampanaDAO.listar()
    return render_template(
        'calendario/mes.html',
        eventos=eventos,
        mes=mes,
        anio=anio,
        campanas=campanas,
    )


def _fecha_form_valida(fecha, nombre, tipo):
    if not fecha or not nombre or not tipo:
        flash('Completa nombre, fecha y tipo del evento.', 'error')
        return None
    try:
        return datetime.strptime(fecha, '%Y-%m-%d')
    except ValueError:
        flash('La fecha del evento no es valida.', 'error')
        return None


@calendario_bp.route('/nuevo', methods=['POST'])
@login_required
def nuevo():
    fecha = request.form.get('fecha')
    nombre = (request.form.get('nombre') or '').strip()
    tipo = request.form.get('tipo')
    accion = request.form.get('accion_sugerida')
    campana = request.form.get('campana_id') or None
    destacado = bool(request.form.get('destacado'))
    color = request.form.get('color') or None

    fecha_dt = _fecha_form_valida(fecha, nombre, tipo)
    if not fecha_dt:
        return redirect(request.referrer or url_for('calendario.index'))

    evento_id = CalendarioDAO.insertar(
        nombre=nombre,
        fecha=fecha,
        tipo=tipo,
        accion_sugerida=accion,
        campana_id=campana,
        destacado=destacado,
        color=color,
    )
    if evento_id is None:
        flash('No se pudo crear el evento. Revisa la conexion o la tabla cal_eventos.', 'error')
        return redirect(request.referrer or url_for('calendario.index', anio=fecha_dt.year))

    flash('Evento creado.', 'success')
    if destacado:
        return redirect(url_for('calendario.index', anio=fecha_dt.year))
    return redirect(url_for('calendario.mes', mes=fecha_dt.month, anio=fecha_dt.year))


@calendario_bp.route('/editar/<int:id>', methods=['POST'])
@login_required
def editar(id):
    fecha = request.form.get('fecha')
    nombre = (request.form.get('nombre') or '').strip()
    tipo = request.form.get('tipo')
    accion = request.form.get('accion_sugerida')
    campana = request.form.get('campana_id') or None

    fecha_dt = _fecha_form_valida(fecha, nombre, tipo)
    if not fecha_dt:
        return redirect(request.referrer or url_for('calendario.index'))

    filas = CalendarioDAO.actualizar(
        id=id,
        nombre=nombre,
        fecha=fecha,
        tipo=tipo,
        accion_sugerida=accion,
        campana_id=campana,
    )
    if not filas:
        flash('No se pudo actualizar el evento.', 'error')
        return redirect(request.referrer or url_for('calendario.mes', mes=fecha_dt.month, anio=fecha_dt.year))

    flash('Evento actualizado.', 'success')
    return redirect(url_for('calendario.mes', mes=fecha_dt.month, anio=fecha_dt.year))


@calendario_bp.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    filas = CalendarioDAO.eliminar(id)
    if not filas:
        flash('No se pudo eliminar el evento.', 'error')
        return redirect(request.referrer or url_for('calendario.index'))

    flash('Evento eliminado.', 'error')
    return redirect(request.referrer or url_for('calendario.index'))
