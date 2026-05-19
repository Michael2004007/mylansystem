from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required
from flask_wtf.csrf import validate_csrf
from dao.influencer_dao import InfluencerDAO
from dao.colaboracion_dao import ColaboracionDAO
from dao.campana_dao import CampanaDAO
from entidades.influencer import Influencer
from entidades.colaboracion import Colaboracion
import io
import openpyxl

influencers_bp = Blueprint('influencers', __name__)


@influencers_bp.route('/')
@login_required
def index():
    estado = request.args.get('estado')
    busqueda = request.args.get('q', '').strip()

    influencers = InfluencerDAO.listar(estado=estado, busqueda=busqueda if busqueda else None)

    return render_template('influencers/index.html',
                           influencers=influencers,
                           estado=estado,
                           busqueda=busqueda)


@influencers_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if request.method == 'POST':
        inf = Influencer(
            id=None,
            nombre=request.form['nombre'],
            estado=request.form['estado'],
            handle=request.form.get('handle'),
            url_ig=request.form.get('url_ig'),
            whatsapp=request.form.get('whatsapp'),
            notas=request.form.get('notas')
        )
        InfluencerDAO.insertar(inf)
        flash('Influencer agregado.', 'success')
        return redirect(url_for('influencers.index'))
    return render_template('influencers/form.html', influencer=None)


@influencers_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    inf = InfluencerDAO.obtener(id)
    if request.method == 'POST':
        inf.nombre = request.form['nombre']
        inf.estado = request.form['estado']
        inf.handle = request.form.get('handle')
        inf.url_ig = request.form.get('url_ig')
        inf.whatsapp = request.form.get('whatsapp')
        inf.notas = request.form.get('notas')
        InfluencerDAO.actualizar(inf)
        flash('Influencer actualizado.', 'success')
        return redirect(url_for('influencers.index'))
    return render_template('influencers/form.html', influencer=inf)


@influencers_bp.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    InfluencerDAO.eliminar(id)
    flash('Influencer eliminado.', 'error')
    return redirect(url_for('influencers.index'))


@influencers_bp.route('/<int:id>/colaborar', methods=['GET', 'POST'])
@login_required
def colaborar(id):
    influencer = InfluencerDAO.obtener(id)
    if request.method == 'POST':
        campana_id_raw = request.form.get('campana_id', '').strip()
        campana_id = int(campana_id_raw) if campana_id_raw else None
        tipo = request.form.get('tipo')
        if tipo not in ('normal', 'ecom', 'ecommerce'):
            flash('Tipo de colaboración inválido.', 'error')
            return redirect(url_for('influencers.colaborar', id=id))

        try:
            monto = float(request.form.get('monto') or 0)
            pct_comision = float(request.form.get('pct_comision') or 0)
            pct_descuento = float(request.form.get('pct_descuento') or 0) or None
        except ValueError:
            flash('Valores numéricos inválidos en la colaboración.', 'error')
            return redirect(url_for('influencers.colaborar', id=id))

        colab = Colaboracion(
            id=None,
            influencer_id=id,
            campana_id=campana_id,
            tipo=tipo,
            monto=monto,
            pct_comision=pct_comision,
            pct_descuento=pct_descuento,
            detalle=request.form.get('detalle'),
            permuta_tag=request.form.get('permuta_tag'),
            fecha_entrega=request.form.get('fecha_entrega') or None,
            codigo_promo=request.form.get('codigo_promo'),
            estado='pendiente'
        )
        ColaboracionDAO.insertar(colab)
        flash('Colaboración registrada.', 'success')
        return redirect(url_for('influencers.index'))
    campanas = CampanaDAO.listar()
    return render_template('influencers/colaborar.html', influencer=influencer, campanas=campanas)


@influencers_bp.route('/colaboraciones')
@login_required
def colaboraciones():
    colabs = ColaboracionDAO.listar_todas()
    f = (request.args.get('f') or '').strip().lower()

    if f == 'campana':
        lista = [c for c in colabs if c.campana_nombre]
    elif f == 'sin_campana':
        lista = [c for c in colabs if not c.campana_nombre]
    elif f == 'ecom':
        lista = [c for c in colabs if c.tipo in ('ecom', 'ecommerce')]
    elif f == 'permuta':
        lista = [c for c in colabs if c.permuta_tag]
    elif f == 'hechas':
        lista = [c for c in colabs if (c.estado or '').strip().lower() == 'hecho']
    elif f == 'pendientes':
        lista = [c for c in colabs if (c.estado or '').strip().lower() != 'hecho']
    else:
        lista = colabs

    return render_template('influencers/colaboraciones.html', colabs=colabs, lista=lista)


@influencers_bp.route('/colaboracion/<int:id>/hecho', methods=['POST'])
@login_required
def colaboracion_hecho(id):
    colab = ColaboracionDAO.obtener(id)
    if not colab:
        flash('Colaboración no encontrada.', 'error')
        return redirect(url_for('influencers.colaboraciones'))

    if colab.tipo in ('ecom', 'ecommerce'):
        flash('Ecommerce es continuo y no se marca como hecho.', 'warning')
        return redirect(url_for('influencers.colaboraciones'))

    ColaboracionDAO.marcar_hecho(id)
    flash('Colaboración marcada como hecha.', 'success')
    return redirect(url_for('influencers.colaboraciones', f='pendientes'))


@influencers_bp.route('/colaboracion/<int:id>/pendiente', methods=['POST'])
@login_required
def colaboracion_pendiente(id):
    ColaboracionDAO.marcar_pendiente(id)
    flash('Colaboración movida a pendientes.', 'success')
    return redirect(url_for('influencers.colaboraciones', f='hechas'))


@influencers_bp.route('/colaboracion/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_colaboracion(id):
    colab = ColaboracionDAO.obtener(id)
    if not colab:
        flash('Colaboración no encontrada.', 'error')
        return redirect(url_for('influencers.colaboraciones'))

    if request.method == 'POST':
        colab.tipo = request.form.get('tipo', colab.tipo)
        colab.monto = float(request.form.get('monto') or 0)
        colab.pct_comision = float(request.form.get('pct_comision') or 0)
        colab.pct_descuento = float(request.form.get('pct_descuento') or 0) or None
        colab.detalle = request.form.get('detalle')
        colab.permuta_tag = request.form.get('permuta_tag')
        colab.fecha_entrega = request.form.get('fecha_entrega') or None
        colab.codigo_promo = request.form.get('codigo_promo')
        ColaboracionDAO.actualizar(colab)
        flash('Colaboración actualizada.', 'success')
        return redirect(url_for('influencers.colaboraciones'))

    return render_template('influencers/editar_colaboraciones.html', c=colab)


@influencers_bp.route('/colaboracion/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_colaboracion(id):
    ColaboracionDAO.eliminar(id)
    flash('Colaboración eliminada.', 'error')
    return redirect(url_for('influencers.colaboraciones'))


@influencers_bp.route('/importar', methods=['GET'])
@login_required
def importar():
    return render_template('influencers/importar.html')


@influencers_bp.route('/importar-excel', methods=['POST'])
@login_required
def importar_excel():
    # Verificar CSRF manualmente
    try:
        csrf_token = request.headers.get('X-CSRFToken')
        if csrf_token:
            validate_csrf(csrf_token)
    except Exception as e:
        print(f"❌ Error CSRF: {e}")
        return jsonify({'ok': False, 'error': 'Token CSRF inválido'}), 400

    data = request.get_json()
    if not data:
        return jsonify({'ok': False, 'error': 'No se recibieron datos'}), 400

    rows = data.get('influencers', [])

    if not rows:
        return jsonify({'ok': False, 'error': 'No hay datos para importar'}), 400

    # MAPEO DE ESTADOS
    estado_map = {
        'new': 'nuevo',
        'worked': 'trabajaron',
        'suggested': 'sugerido',
        'nuevo': 'nuevo',
        'trabajaron': 'trabajaron',
        'sugerido': 'sugerido',
        'sugeridos': 'sugerido'
    }

    try:
        contador = 0
        duplicados = 0
        errores = []

        for idx, row in enumerate(rows, start=1):
            nombre = row.get('nombre', '').strip()
            handle = row.get('handle', '').strip()

            if not nombre:
                errores.append(f"Fila {idx}: falta el nombre")
                continue

            if not handle:
                errores.append(f"Fila {idx}: falta el handle")
                continue

            # VERIFICAR DUPLICADO
            if InfluencerDAO.existe_por_handle(handle):
                duplicados += 1
                errores.append(f"Fila {idx}: {handle} ya existe (duplicado)")
                print(f"⚠️ Duplicado ignorado: {handle}")
                continue

            # Obtener y mapear el estado
            estado_raw = row.get('estado', '').strip().lower()
            estado_final = estado_map.get(estado_raw, 'nuevo')

            print(f"📝 Fila {idx}: {nombre} ({handle}) - estado '{estado_raw}' → '{estado_final}'")

            inf = Influencer(
                id=None,
                nombre=nombre,
                handle=handle,
                url_ig=row.get('ig', '').strip(),
                whatsapp=row.get('wa', '').strip(),
                estado=estado_final,
                notas=None
            )

            resultado = InfluencerDAO.insertar(inf)
            if resultado:
                contador += 1
                print(f"✅ Guardado: {nombre}")
            else:
                errores.append(f"Fila {idx}: error al guardar {nombre}")
                print(f"❌ Error guardando: {nombre}")

        if errores:
            print(f"⚠️ Errores durante importación: {errores}")

        print(f"✅ Importados: {contador}/{len(rows)} | Duplicados ignorados: {duplicados}")

        mensaje = f"Importados: {contador}"
        if duplicados > 0:
            mensaje += f" | Duplicados ignorados: {duplicados}"

        return jsonify({
            'ok': True,
            'importados': contador,
            'duplicados': duplicados,
            'total': len(rows),
            'mensaje': mensaje,
            'errores': errores if errores else None
        })

    except Exception as e:
        print(f"❌ Error al importar: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'ok': False, 'error': str(e)}), 500


@influencers_bp.route('/descargar-plantilla')
@login_required
def descargar_plantilla():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Influencers'

    # Headers
    ws.append(['nombre', 'handle', 'ig', 'wa', 'estado'])

    # Ejemplos con los valores CORRECTOS
    ws.append(['Juan Pérez', '@juanperez', 'https://instagram.com/juanperez', '5491112345678', 'nuevo'])
    ws.append(['María López', '@mlopez', 'https://instagram.com/mlopez', '5491187654321', 'trabajaron'])
    ws.append(['Carlos Gómez', '@cgomez', 'https://instagram.com/cgomez', '5491198765432', 'sugerido'])

    # Ajustar anchos de columna
    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = 25

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='plantilla_influencers.xlsx'
    )
