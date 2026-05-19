import os
from collections import defaultdict
from datetime import date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from dao.configuracion_dao import ConfiguracionDAO
from dao.tarea_dao import TareaDAO
from dao.campana_dao import CampanaDAO
from dao.influencer_dao import InfluencerDAO
from decorators import requiere_permiso

inicio_bp = Blueprint('inicio', __name__)

ALLOWED = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'}


def allowed_logo(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED


@inicio_bp.route('/')
@login_required
@requiere_permiso('inicio')
def index():
    logo = ConfiguracionDAO.obtener('logo_ruta')

    # Si es admin, ve todas las tareas; si es usuario, solo las suyas
    if current_user.es_admin():
        tareas = TareaDAO.listar()
    else:
        tareas = TareaDAO.listar(usuario_id=current_user.id)

    campanas = CampanaDAO.listar()

    try:
        influencers = InfluencerDAO.listar()
        influencers_count = len(influencers)
    except Exception:
        influencers_count = 0

    pendientes = [t for t in tareas if t.estado == 'pendiente']

    # Tareas que vencen entre hoy y el domingo de esta semana
    hoy = date.today()
    fin_semana = hoy + timedelta(days=(6 - hoy.weekday()))
    tareas_semana = [
        t for t in pendientes
        if t.fecha_entrega and str(t.fecha_entrega) >= str(hoy) and str(t.fecha_entrega) <= str(fin_semana)
    ]
    tareas_semana.sort(key=lambda t: str(t.fecha_entrega))

    # Agrupar tareas de la semana por usuario
    tareas_semana_por_usuario = defaultdict(list)
    for t in tareas_semana:
        usuario = t.usuario_nombre or 'Sin asignar'
        tareas_semana_por_usuario[usuario].append(t)
    tareas_semana_por_usuario = dict(sorted(tareas_semana_por_usuario.items()))

    tareas_atrasadas = [
        t for t in pendientes
        if t.fecha_entrega and str(t.fecha_entrega) < str(hoy)
    ]
    tareas_atrasadas.sort(key=lambda t: str(t.fecha_entrega))
    tareas_atrasadas_por_usuario = defaultdict(list)
    for t in tareas_atrasadas:
        usuario = t.usuario_nombre or 'Sin asignar'
        tareas_atrasadas_por_usuario[usuario].append(t)
    tareas_atrasadas_por_usuario = dict(sorted(tareas_atrasadas_por_usuario.items()))


    return render_template(
        'inicio/index.html',
        logo=logo,
        tareas=tareas,
        campanas=campanas,
        pendientes=pendientes,
        influencers_count=influencers_count,
        tareas_semana=tareas_semana,
        tareas_semana_por_usuario=tareas_semana_por_usuario,
        tareas_semana_por_persona=tareas_semana_por_usuario,
        tareas_atrasadas=tareas_atrasadas,
        tareas_atrasadas_por_usuario=tareas_atrasadas_por_usuario
    )


@inicio_bp.route('/cambiar_logo', methods=['POST'])
@login_required
def cambiar_logo():
    if not current_user.es_admin():
        flash('No tenés permiso para cambiar el logo.', 'error')
        return redirect(url_for('inicio.index'))

    file = request.files.get('logo')
    if not file or not allowed_logo(file.filename):
        flash('Archivo no válido.', 'error')
        return redirect(url_for('inicio.index'))

    filename = secure_filename(file.filename)
    ruta_carpeta = os.path.join(current_app.root_path, 'static', 'uploads')
    os.makedirs(ruta_carpeta, exist_ok=True)
    file.save(os.path.join(ruta_carpeta, filename))
    ConfiguracionDAO.actualizar('logo_ruta', f'uploads/{filename}')
    flash('Logo actualizado correctamente.', 'success')
    return redirect(url_for('inicio.index'))
