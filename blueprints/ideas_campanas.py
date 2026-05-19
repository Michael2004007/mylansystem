from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from dao.idea_campana_dao import IdeaCampanaDAO
from dao.influencer_dao import InfluencerDAO
from dao.campana_dao import CampanaDAO
from dao.colaboracion_dao import ColaboracionDAO
from dao.hito_dao import HitoDAO

from entidades.campana import Campana
from entidades.colaboracion import Colaboracion
from entidades.hito import Hito
from decorators import requiere_permiso

ideas_campanas_bp = Blueprint('ideas_campanas', __name__)


def _mes_anio(fecha_inicio):
    if fecha_inicio:
        try:
            dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            return dt.month, dt.year
        except ValueError:
            pass
    now = datetime.now()
    return now.month, now.year


@ideas_campanas_bp.route('/')
@login_required
@requiere_permiso('ideas_campanas')
def index():
    ideas = IdeaCampanaDAO.listar()
    return render_template('ideas_campanas/index.html', ideas=ideas)


@ideas_campanas_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
@requiere_permiso('ideas_campanas', requiere_editar=True)
def nueva():
    if request.method == 'POST':
        nombre = (request.form.get('nombre') or '').strip()
        descripcion = request.form.get('descripcion')
        if not nombre:
            flash('El nombre es obligatorio.', 'error')
            return redirect(url_for('ideas_campanas.nueva'))
        IdeaCampanaDAO.insertar(nombre, descripcion)
        flash('Idea creada.', 'success')
        return redirect(url_for('ideas_campanas.index'))
    return render_template('ideas_campanas/form.html', idea=None)


@ideas_campanas_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@requiere_permiso('ideas_campanas', requiere_editar=True)
def editar(id):
    idea = IdeaCampanaDAO.obtener(id)
    if not idea:
        flash('Idea no encontrada.', 'error')
        return redirect(url_for('ideas_campanas.index'))
    if request.method == 'POST':
        nombre = (request.form.get('nombre') or '').strip()
        descripcion = request.form.get('descripcion')
        if not nombre:
            flash('El nombre es obligatorio.', 'error')
            return redirect(url_for('ideas_campanas.editar', id=id))
        IdeaCampanaDAO.actualizar(id, nombre, descripcion)
        flash('Idea actualizada.', 'success')
        return redirect(url_for('ideas_campanas.index'))
    return render_template('ideas_campanas/form.html', idea=idea)


@ideas_campanas_bp.route('/eliminar/<int:id>')
@login_required
@requiere_permiso('ideas_campanas', requiere_editar=True)
def eliminar(id):
    IdeaCampanaDAO.eliminar(id)
    flash('Idea eliminada.', 'error')
    return redirect(url_for('ideas_campanas.index'))


@ideas_campanas_bp.route('/<int:id>')
@login_required
@requiere_permiso('ideas_campanas')
def detalle(id):
    idea = IdeaCampanaDAO.obtener(id)
    if not idea:
        flash('Idea no encontrada.', 'error')
        return redirect(url_for('ideas_campanas.index'))
    colaboradores = IdeaCampanaDAO.listar_colaboraciones(id)
    hitos = IdeaCampanaDAO.listar_hitos(id)
    influencers = InfluencerDAO.listar()
    return render_template(
        'ideas_campanas/detalle.html',
        idea=idea,
        colaboradores=colaboradores,
        hitos=hitos,
        influencers=influencers
    )


@ideas_campanas_bp.route('/<int:id>/colaboracion', methods=['POST'])
@login_required
@requiere_permiso('ideas_campanas', requiere_editar=True)
def agregar_colaboracion(id):
    influencer_id = request.form.get('influencer_id', type=int)
    if not influencer_id:
        flash('Seleccioná influencer.', 'error')
        return redirect(url_for('ideas_campanas.detalle', id=id))
    detalle = request.form.get('detalle')
    fecha_entrega = request.form.get('fecha_entrega') or None
    try:
        monto = float(request.form.get('monto') or 0)
    except ValueError:
        flash('Monto inválido.', 'error')
        return redirect(url_for('ideas_campanas.detalle', id=id))
    IdeaCampanaDAO.agregar_colaboracion(id, influencer_id, detalle, monto, fecha_entrega)
    flash('Influencer candidato agregado.', 'success')
    return redirect(url_for('ideas_campanas.detalle', id=id))


@ideas_campanas_bp.route('/<int:id>/hito', methods=['POST'])
@login_required
@requiere_permiso('ideas_campanas', requiere_editar=True)
def agregar_hito(id):
    titulo = (request.form.get('titulo') or '').strip()
    fecha_hora = request.form.get('fecha_hora')
    if not titulo or not fecha_hora:
        flash('Completá título y fecha del hito.', 'error')
        return redirect(url_for('ideas_campanas.detalle', id=id))
    IdeaCampanaDAO.agregar_hito(
        id,
        titulo=titulo,
        descripcion=request.form.get('descripcion'),
        lugar=request.form.get('lugar'),
        fecha_hora=fecha_hora
    )
    flash('Idea de hito agregada.', 'success')
    return redirect(url_for('ideas_campanas.detalle', id=id))


@ideas_campanas_bp.route('/<int:id>/activar', methods=['POST'])
@login_required
@requiere_permiso('ideas_campanas', requiere_aprobar=True)
def activar(id):
    idea = IdeaCampanaDAO.obtener(id)
    if not idea:
        flash('Idea no encontrada.', 'error')
        return redirect(url_for('ideas_campanas.index'))

    fecha_inicio = request.form.get('fecha_inicio') or None
    fecha_fin = request.form.get('fecha_fin') or None
    try:
        presupuesto = float(request.form.get('presupuesto') or 0)
    except ValueError:
        flash('Presupuesto inválido.', 'error')
        return redirect(url_for('ideas_campanas.detalle', id=id))

    mes, anio = _mes_anio(fecha_inicio)
    campana = Campana(
        id=None,
        nombre=idea['nombre'],
        mes=mes,
        anio=anio,
        presupuesto=presupuesto,
        gastado=0,
        descripcion=idea.get('descripcion'),
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        status='activa'
    )
    campana_id = CampanaDAO.insertar(campana)
    if not campana_id:
        flash('No se pudo activar la idea.', 'error')
        return redirect(url_for('ideas_campanas.detalle', id=id))

    colab_aprobadas = request.form.getlist('colab_ids')
    for row in IdeaCampanaDAO.listar_colaboraciones(id):
        if str(row['id']) not in colab_aprobadas:
            continue
        colab = Colaboracion(
            id=None,
            influencer_id=row['influencer_id'],
            campana_id=campana_id,
            tipo='normal',
            monto=float(row.get('monto') or 0),
            pct_comision=0,
            detalle=row.get('detalle'),
            permuta_tag=None,
            fecha_entrega=row.get('fecha_entrega'),
            codigo_promo=None,
            pct_descuento=None,
            estado='pendiente'
        )
        ColaboracionDAO.insertar(colab)
        if colab.monto:
            CampanaDAO.actualizar_gasto(campana_id, colab.monto)

    hitos_aprobados = request.form.getlist('hito_ids')
    for row in IdeaCampanaDAO.listar_hitos(id):
        if str(row['id']) not in hitos_aprobados:
            continue
        hito = Hito(
            id=None,
            campana_id=campana_id,
            titulo=row['titulo'],
            descripcion=row.get('descripcion'),
            lugar=row.get('lugar'),
            fecha_hora=row['fecha_hora'],
            estado='pendiente'
        )
        HitoDAO.insertar(hito)

    IdeaCampanaDAO.marcar_activada(id, campana_id)
    flash('Idea activada como campaña.', 'success')
    return redirect(url_for('campanas.detalle', id=campana_id))
