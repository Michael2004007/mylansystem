from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from dao.ecommerce_dao import EcommerceDAO
from dao.influencer_dao import InfluencerDAO
import datetime
import calendar

ecommerce_bp = Blueprint('ecommerce', __name__)


@ecommerce_bp.route('/')
@login_required
def index():
    hoy         = datetime.date.today()
    mes         = request.args.get('mes',  type=int, default=hoy.month)
    anio        = request.args.get('anio', type=int, default=hoy.year)
    ventas      = EcommerceDAO.listar_ventas(mes, anio)
    metas       = EcommerceDAO.listar_metas_con_real(anio)   # ← único cambio
    influencers = InfluencerDAO.listar()
    dias_mes    = calendar.monthrange(anio, mes)[1]
    dia_actual  = hoy.day if (hoy.month == mes and hoy.year == anio) else dias_mes
    hoy_str     = hoy.strftime('%Y-%m-%d')
    ventas_hoy  = sum(v['monto'] for v in ventas if str(v.get('fecha', '')) == hoy_str)
    return render_template('ecommerce/index.html',
                           ventas=ventas, metas=metas,
                           influencers=influencers,
                           mes=mes, anio=anio,
                           dias_en_mes=dias_mes,
                           dia_actual=dia_actual,
                           ventas_hoy=ventas_hoy,
                           hoy_str=hoy_str)


@ecommerce_bp.route('/registrar_venta', methods=['POST'])
@login_required
def registrar_venta():
    raw_id = request.form.get('influencer_id')
    fecha  = request.form.get('fecha')
    monto_raw = request.form.get('monto')
    if not monto_raw:
        flash('Ingresá el monto de la venta.', 'error')
        return redirect(url_for('ecommerce.index'))
    try:
        monto = float(monto_raw)
    except ValueError:
        flash('Monto inválido.', 'error')
        return redirect(url_for('ecommerce.index'))
    fecha_dt = datetime.datetime.strptime(fecha, '%Y-%m-%d').date() if fecha else datetime.date.today()
    EcommerceDAO.insertar_venta(
        influencer_id = int(raw_id) if raw_id else None,
        mes           = fecha_dt.month,
        anio          = fecha_dt.year,
        monto         = monto,
        nota          = request.form.get('nota'),
        fecha         = fecha_dt
    )
    flash('Venta registrada correctamente.', 'success')
    return redirect(url_for('ecommerce.index', mes=fecha_dt.month, anio=fecha_dt.year))


@ecommerce_bp.route('/editar_venta/<int:venta_id>', methods=['POST'])
@login_required
def editar_venta(venta_id):
    raw_id = request.form.get('influencer_id')
    fecha  = request.form.get('fecha')
    fecha_dt = datetime.datetime.strptime(fecha, '%Y-%m-%d').date() if fecha else datetime.date.today()
    try:
        monto = float(request.form.get('monto') or 0)
    except ValueError:
        flash('Monto inválido.', 'error')
        return redirect(url_for('ecommerce.index'))
    EcommerceDAO.actualizar_venta(
        venta_id      = venta_id,
        influencer_id = int(raw_id) if raw_id else None,
        mes           = fecha_dt.month,
        anio          = fecha_dt.year,
        monto         = monto,
        nota          = request.form.get('nota'),
        fecha         = fecha_dt
    )
    flash('Venta actualizada correctamente.', 'success')
    return redirect(url_for('ecommerce.index', mes=fecha_dt.month, anio=fecha_dt.year))


@ecommerce_bp.route('/eliminar_venta/<int:venta_id>', methods=['POST'])
@login_required
def eliminar_venta(venta_id):
    EcommerceDAO.eliminar_venta(venta_id)
    flash('Venta eliminada.', 'success')
    return redirect(url_for('ecommerce.index'))


@ecommerce_bp.route('/metas', methods=['GET', 'POST'])
@login_required
def metas():
    hoy  = datetime.date.today()
    anio = request.args.get('anio', type=int, default=hoy.year)
    if request.method == 'POST':
        try:
            mes = int(request.form.get('mes') or 0)
            anio_form = int(request.form.get('anio') or 0)
            meta = float(request.form.get('meta') or 0)
            real = float(request.form.get('real') or 0)
        except ValueError:
            flash('Datos de meta inválidos.', 'error')
            return redirect(url_for('ecommerce.index'))
        EcommerceDAO.actualizar_meta(
            mes=mes,
            anio=anio_form,
            meta=meta,
            real=real
        )
        flash('Meta actualizada.', 'success')
        return redirect(url_for('ecommerce.index'))
    metas_data = EcommerceDAO.listar_metas(anio)
    return render_template('ecommerce/metas.html', metas=metas_data, anio=anio)
