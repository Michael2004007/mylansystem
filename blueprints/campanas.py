from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from dao.campana_dao import CampanaDAO
from dao.colaboracion_dao import ColaboracionDAO
from dao.influencer_dao import InfluencerDAO
from dao.hito_dao import HitoDAO

from entidades.campana import Campana
from entidades.colaboracion import Colaboracion
from entidades.influencer import Influencer
from entidades.hito import Hito
from decorators import requiere_permiso

campanas_bp = Blueprint('campanas', __name__)


def _mes_anio_desde_fechas(fecha_inicio, fecha_fin):
    fuente = fecha_inicio or fecha_fin
    if fuente:
        try:
            dt = datetime.strptime(fuente, '%Y-%m-%d')
            return dt.month, dt.year
        except ValueError:
            pass
    now = datetime.now()
    return now.month, now.year


@campanas_bp.route('/')
@login_required
def index():
    campanas = CampanaDAO.listar()
    return render_template('campanas/index.html', campanas=campanas)


@campanas_bp.route('/<int:id>')
@login_required
def detalle(id):
    campana = CampanaDAO.obtener(id)
    if not campana:
        flash('Campaña no encontrada.', 'error')
        return redirect(url_for('campanas.index'))
    colaboraciones = ColaboracionDAO.listar_por_campana(id)
    hitos = HitoDAO.listar_por_campana(id)
    influencers = InfluencerDAO.listar()
    return render_template(
        'campanas/detalle.html',
        campana=campana,
        colaboraciones=colaboraciones,
        hitos=hitos,
        influencers=influencers
    )


@campanas_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva():
    if request.method == 'POST':
        fecha_inicio = request.form.get('fecha_inicio') or None
        fecha_fin    = request.form.get('fecha_fin') or None
        mes, anio    = _mes_anio_desde_fechas(fecha_inicio, fecha_fin)
        c = Campana(
            id=None,
            nombre=request.form['nombre'],
            mes=mes,
            anio=anio,
            presupuesto=float(request.form.get('presupuesto') or 0),
            gastado=0,
            descripcion=request.form.get('descripcion'),
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            status='activa'
        )
        CampanaDAO.insertar(c)
        flash('Campaña creada.', 'success')
        return redirect(url_for('campanas.index'))
    return render_template('campanas/form.html', campana=None)


@campanas_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    campana = CampanaDAO.obtener(id)
    if request.method == 'POST':
        fecha_inicio = request.form.get('fecha_inicio') or None
        fecha_fin    = request.form.get('fecha_fin') or None
        mes, anio    = _mes_anio_desde_fechas(fecha_inicio, fecha_fin)
        campana.nombre       = request.form['nombre']
        campana.mes          = mes
        campana.anio         = anio
        campana.presupuesto  = float(request.form.get('presupuesto') or 0)
        campana.descripcion  = request.form.get('descripcion')
        campana.fecha_inicio = fecha_inicio
        campana.fecha_fin    = fecha_fin
        campana.status       = request.form.get('status', campana.status)
        CampanaDAO.actualizar(campana)
        flash('Campaña actualizada.', 'success')
        return redirect(url_for('campanas.index'))
    return render_template('campanas/form.html', campana=campana)


@campanas_bp.route('/completar/<int:id>')
@login_required
@requiere_permiso('campanas', requiere_aprobar=True)
def completar(id):
    CampanaDAO.completar(id)
    flash('Campaña marcada como completada.', 'success')
    return redirect(url_for('campanas.index'))


@campanas_bp.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    CampanaDAO.eliminar(id)
    flash('Campaña eliminada.', 'error')
    return redirect(url_for('campanas.index'))


@campanas_bp.route('/<int:campana_id>/colaborar', methods=['POST'])
@login_required
def agregar_colaboracion(campana_id):
    influencer_id = request.form.get('influencer_id')
    if not influencer_id:
        flash('Seleccioná un influencer.', 'error')
        return redirect(url_for('campanas.detalle', id=campana_id))

    if influencer_id == '__nuevo__':
        nuevo_nombre = request.form.get('nuevo_nombre', '').strip()
        if not nuevo_nombre:
            flash('Ingresá el nombre del nuevo influencer.', 'error')
            return redirect(url_for('campanas.detalle', id=campana_id))
        inf = Influencer(
            id=None,
            nombre=nuevo_nombre,
            handle=request.form.get('nuevo_handle', ''),
            url_ig=request.form.get('nuevo_ig', ''),
            whatsapp=request.form.get('nuevo_wa', ''),
            estado=request.form.get('nuevo_estado', 'nuevo'),
            notas=None
        )
        influencer_id = InfluencerDAO.insertar(inf)
        if not influencer_id:
            flash('No se pudo crear el influencer.', 'error')
            return redirect(url_for('campanas.detalle', id=campana_id))

    tipo_pago = request.form.get('tipo_pago', 'efectivo')
    permuta_tag = request.form.get('permuta_tag', '').strip() if tipo_pago == 'permuta' else None
    try:
        monto = 0.0 if tipo_pago == 'permuta' else float(request.form.get('monto') or 0)
    except ValueError:
        flash('Monto inválido.', 'error')
        return redirect(url_for('campanas.detalle', id=campana_id))

    try:
        influencer_id = int(influencer_id)
    except (TypeError, ValueError):
        flash('Influencer inválido.', 'error')
        return redirect(url_for('campanas.detalle', id=campana_id))

    colab = Colaboracion(
        id=None,
        influencer_id=influencer_id,
        campana_id=campana_id,
        tipo='normal',
        monto=monto,
        pct_comision=0,
        detalle=request.form.get('detalle'),
        permuta_tag=permuta_tag,
        fecha_entrega=request.form.get('fecha_entrega') or None,
        codigo_promo=None
    )
    nuevo_id = ColaboracionDAO.insertar(colab)
    if not nuevo_id:
        flash('No se pudo guardar la colaboración. Revisá los datos e intentá de nuevo.', 'error')
        return redirect(url_for('campanas.detalle', id=campana_id))

    if colab.monto:
        CampanaDAO.actualizar_gasto(campana_id, colab.monto)

    flash('Colaboración agregada.', 'success')
    return redirect(url_for('campanas.detalle', id=campana_id))


@campanas_bp.route('/colaboracion/<int:colab_id>/editar', methods=['POST'])
@login_required
def editar_colaboracion(colab_id):
    colab          = ColaboracionDAO.obtener(colab_id)
    if not colab:
        flash('Colaboración no encontrada.', 'error')
        return redirect(url_for('campanas.index'))
    monto_anterior = colab.monto or 0

    tipo_pago        = request.form.get('tipo_pago', 'efectivo')
    colab.tipo       = 'normal'
    try:
        colab.monto = 0.0 if tipo_pago == 'permuta' else float(request.form.get('monto') or 0)
    except ValueError:
        flash('Monto inválido.', 'error')
        return redirect(url_for('campanas.detalle', id=colab.campana_id))
    colab.permuta_tag = request.form.get('permuta_tag', '').strip() if tipo_pago == 'permuta' else None
    colab.detalle    = request.form.get('detalle')
    colab.fecha_entrega = request.form.get('fecha_entrega') or None
    colab.pct_comision  = 0
    colab.codigo_promo  = None

    ColaboracionDAO.actualizar(colab)

    diferencia = colab.monto - monto_anterior
    if diferencia != 0:
        CampanaDAO.actualizar_gasto(colab.campana_id, diferencia)

    flash('Colaboración actualizada.', 'success')
    return redirect(url_for('campanas.detalle', id=colab.campana_id))


@campanas_bp.route('/colaboracion/<int:colab_id>/eliminar')
@login_required
def eliminar_colaboracion(colab_id):
    colab      = ColaboracionDAO.obtener(colab_id)
    if not colab:
        flash('Colaboración no encontrada.', 'error')
        return redirect(url_for('campanas.index'))
    campana_id = colab.campana_id
    if colab.monto:
        CampanaDAO.actualizar_gasto(campana_id, -colab.monto)
    ColaboracionDAO.eliminar(colab_id)
    flash('Colaboración eliminada.', 'error')
    return redirect(url_for('campanas.detalle', id=campana_id))


@campanas_bp.route('/<int:campana_id>/hito/nuevo', methods=['POST'])
@login_required
def agregar_hito(campana_id):
    titulo = (request.form.get('titulo') or '').strip()
    fecha_hora = (request.form.get('fecha_hora') or '').strip().replace('T', ' ')
    if not titulo or not fecha_hora:
        flash('Completá título y fecha del hito.', 'error')
        return redirect(url_for('campanas.detalle', id=campana_id))

    hito = Hito(
        id=None,
        campana_id=campana_id,
        titulo=titulo,
        descripcion=request.form.get('descripcion'),
        lugar=request.form.get('lugar'),
        fecha_hora=fecha_hora,
        estado='pendiente'
    )
    nuevo_id = HitoDAO.insertar(hito)
    if not nuevo_id:
        flash('No se pudo guardar el hito. Verificá fecha y datos.', 'error')
        return redirect(url_for('campanas.detalle', id=campana_id))
    flash('Hito agregado.', 'success')
    return redirect(url_for('campanas.detalle', id=campana_id))


@campanas_bp.route('/hito/<int:hito_id>/hecho')
@login_required
def hito_hecho(hito_id):
    hito = HitoDAO.obtener(hito_id)
    if not hito:
        flash('Hito no encontrado.', 'error')
        return redirect(url_for('campanas.index'))
    HitoDAO.marcar_hecho(hito_id)
    flash('Hito marcado como hecho.', 'success')
    return redirect(url_for('campanas.detalle', id=hito.campana_id))


@campanas_bp.route('/hito/<int:hito_id>/postergar', methods=['POST'])
@login_required
def hito_postergar(hito_id):
    hito       = HitoDAO.obtener(hito_id)
    if not hito:
        flash('Hito no encontrado.', 'error')
        return redirect(url_for('campanas.index'))
    nueva_fecha = (request.form['nueva_fecha'] or '').strip().replace('T', ' ')
    motivo     = request.form['motivo']
    HitoDAO.postergar(hito_id, nueva_fecha, motivo)
    flash('Hito postergado.', 'success')
    return redirect(url_for('campanas.detalle', id=hito.campana_id))


@campanas_bp.route('/hito/<int:hito_id>/eliminar')
@login_required
def hito_eliminar(hito_id):
    hito = HitoDAO.obtener(hito_id)
    if not hito:
        flash('Hito no encontrado.', 'error')
        return redirect(url_for('campanas.index'))
    HitoDAO.eliminar(hito_id)
    flash('Hito eliminado.', 'error')
    return redirect(url_for('campanas.detalle', id=hito.campana_id))
