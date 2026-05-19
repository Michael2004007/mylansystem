import os
from uuid import uuid4
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file, abort
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
    tipo = request.args.get('tipo', 'tiendas')
    carpeta_id = request.args.get('carpeta_id', type=int)
    carpetas = ArchivoDAO.listar_carpetas(tipo)
    carpeta_actual = ArchivoDAO.obtener_carpeta(carpeta_id) if carpeta_id else None
    subcarpetas = ArchivoDAO.listar_subcarpetas(carpeta_id) if carpeta_id else []
    archivos = ArchivoDAO.listar_por_carpeta(carpeta_id) if carpeta_id else []
    return render_template(
        'contenidos/galeria.html',
        tipo=tipo,
        carpetas=carpetas,
        carpeta_actual=carpeta_actual,
        subcarpetas=subcarpetas,
        archivos=archivos
    )


@contenidos_bp.route('/carpeta/nueva', methods=['POST'])
@login_required
def nueva_carpeta():
    nombre = (request.form.get('nombre') or '').strip()
    tipo = (request.form.get('tipo') or 'tiendas').strip()
    parent_id = request.form.get('parent_id', type=int)
    if not nombre:
        flash('Escribí un nombre para la carpeta.', 'error')
        return redirect(url_for('contenidos.index', tipo=tipo, carpeta_id=parent_id))
    ArchivoDAO.crear_carpeta(nombre=nombre, tipo=tipo, parent_id=parent_id)
    flash('Carpeta creada.', 'success')
    return redirect(url_for('contenidos.index', tipo=tipo, carpeta_id=parent_id))


@contenidos_bp.route('/subir/<int:carpeta_id>', methods=['POST'])
@login_required
def subir(carpeta_id):
    carpeta = ArchivoDAO.obtener_carpeta(carpeta_id)
    if not carpeta:
        flash('Carpeta no encontrada.', 'error')
        return redirect(url_for('contenidos.index'))

    file = request.files.get('archivo')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        folder_fs = os.path.join(current_app.config['UPLOAD_FOLDER'], 'contenidos', str(carpeta_id))
        os.makedirs(folder_fs, exist_ok=True)
        final_name = f"{uuid4().hex}_{filename}"
        ruta = os.path.join(folder_fs, final_name)
        file.save(ruta)
        tamano_kb = os.path.getsize(ruta) // 1024
        tipo = 'video' if ext in {'mp4', 'mov', 'avi'} else 'imagen'
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
    return redirect(url_for('contenidos.index', tipo=carpeta.get('tipo'), carpeta_id=carpeta_id))


@contenidos_bp.route('/descargar/<int:id>')
@login_required
def descargar(id):
    archivo = ArchivoDAO.obtener(id)
    if not archivo:
        abort(404)
    ruta = archivo.ruta
    if not os.path.isabs(ruta):
        ruta = os.path.join(current_app.root_path, ruta)
    if not os.path.exists(ruta):
        abort(404)
    return send_file(ruta, as_attachment=True, download_name=archivo.nombre)


@contenidos_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    archivo = ArchivoDAO.obtener(id)
    if not archivo:
        flash('Archivo no encontrado.', 'error')
        return redirect(url_for('contenidos.index'))
    ruta = archivo.ruta
    if ruta and os.path.exists(ruta):
        try:
            os.remove(ruta)
        except OSError:
            pass
    ArchivoDAO.eliminar(id)
    flash('Archivo eliminado.', 'error')
    return redirect(url_for('contenidos.index', carpeta_id=archivo.carpeta_id))
