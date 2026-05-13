import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file
from flask_login import login_required
from dao.archivo_dao import ArchivoDAO
from entidades.archivo import Archivo
from werkzeug.utils import secure_filename

contenidos_bp = Blueprint('contenidos', __name__)

ALLOWED = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED


@contenidos_bp.route('/')
@login_required
def index():
    tipo     = request.args.get('tipo', 'influencer')
    carpetas = ArchivoDAO.listar_carpetas(tipo)
    return render_template('contenidos/galeria.html', carpetas=carpetas, tipo=tipo)


@contenidos_bp.route('/subir/<int:carpeta_id>', methods=['POST'])
@login_required
def subir(carpeta_id):
    file = request.files.get('archivo')
    if file and allowed_file(file.filename):
        filename  = secure_filename(file.filename)
        ruta      = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(ruta)
        tamano_kb = os.path.getsize(ruta) // 1024
        ext       = filename.rsplit('.', 1)[1].lower()
        tipo      = 'video' if ext in {'mp4', 'mov', 'avi'} else 'imagen'
        archivo   = Archivo(
            id         = None,
            carpeta_id = carpeta_id,
            nombre     = filename,
            tipo       = tipo,
            ruta       = ruta,
            tamano_kb  = tamano_kb
        )
        ArchivoDAO.insertar(archivo)
        flash('Archivo subido correctamente.', 'success')
    else:
        flash('Tipo de archivo no permitido.', 'error')
    return redirect(url_for('contenidos.index'))


@contenidos_bp.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    ArchivoDAO.eliminar(id)
    flash('Archivo eliminado.', 'error')
    return redirect(url_for('contenidos.index'))