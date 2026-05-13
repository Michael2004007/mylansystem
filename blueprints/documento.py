import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required
from dao.documento_dao import DocumentoDAO
from entidades.documento import Documento

documentos_bp = Blueprint('documentos', __name__)


@documentos_bp.route('/')
@login_required
def index():
    tipo       = request.args.get('tipo')
    documentos = DocumentoDAO.listar(tipo)
    return render_template('documentos/index.html', documentos=documentos, tipo=tipo)


@documentos_bp.route('/requisicion', methods=['GET', 'POST'])
@login_required
def requisicion():
    if request.method == 'POST':
        datos = {
            'solicitante': request.form['solicitante'],
            'fecha':       request.form['fecha'],
            'items':       request.form.getlist('item'),
            'cantidades':  request.form.getlist('cantidad'),
            'precios':     request.form.getlist('precio'),
            'total':       request.form['total'],
            'nota':        request.form.get('nota')
        }
        doc = Documento(id=None, tipo='requisicion', datos=datos)
        DocumentoDAO.insertar(doc)
        flash('Requisición guardada.', 'success')
        return redirect(url_for('documentos.index'))
    return render_template('documentos/requisicion.html')


@documentos_bp.route('/solicitud_pago', methods=['GET', 'POST'])
@login_required
def solicitud_pago():
    if request.method == 'POST':
        datos = {
            'beneficiario':    request.form['beneficiario'],
            'concepto':        request.form['concepto'],
            'campana':         request.form.get('campana'),
            'metodo_pago':     request.form['metodo_pago'],
            'monto':           request.form['monto'],
            'fecha':           request.form['fecha'],
            'nota':            request.form.get('nota')
        }
        doc = Documento(id=None, tipo='solicitud_pago', datos=datos)
        DocumentoDAO.insertar(doc)
        flash('Solicitud de pago guardada.', 'success')
        return redirect(url_for('documentos.index'))
    return render_template('documentos/solicitud_pago.html')