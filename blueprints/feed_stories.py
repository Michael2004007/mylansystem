import os
from uuid import uuid4
from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file, abort
from flask_login import login_required
from werkzeug.utils import secure_filename

from dao.feed_story_dao import FeedStoryDAO
from dao.idea_feed_story_dao import IdeaFeedStoryDAO
from dao.usuario_dao import UsuarioDAO
from decorators import requiere_permiso

feed_stories_bp = Blueprint('feed_stories', __name__)

ALLOWED = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'mov', 'avi'}


def _allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED


@feed_stories_bp.route('/')
@login_required
@requiere_permiso('feed_stories')
def index():
    hoy = date.today()
    anio = request.args.get('anio', type=int, default=hoy.year)
    mes = request.args.get('mes', type=int, default=hoy.month)
    tipo = request.args.get('tipo') or None
    dia_semana = request.args.get('dia_semana', type=int)
    contenidos = FeedStoryDAO.listar(anio=anio, mes=mes, tipo=tipo, dia_semana=dia_semana)
    usuarios = UsuarioDAO.listar()

    feed = [c for c in contenidos if c.get('tipo') == 'feed']
    stories = [c for c in contenidos if c.get('tipo') == 'stories']
    dias = sorted({str(c.get('fecha_publicacion')) for c in contenidos if c.get('fecha_publicacion')})

    return render_template(
        'feed_stories/index.html',
        contenidos=contenidos,
        feed=feed,
        stories=stories,
        dias=dias,
        usuarios=usuarios,
        anio=anio,
        mes=mes,
        hoy=hoy,
    )


@feed_stories_bp.route('/nuevo', methods=['POST'])
@login_required
@requiere_permiso('feed_stories', requiere_editar=True)
def nuevo():
    tipo = request.form.get('tipo')
    fecha_publicacion = request.form.get('fecha_publicacion')
    hora_publicacion = request.form.get('hora_publicacion')
    copy_texto = request.form.get('copy_texto')
    responsable_id = request.form.get('responsable_id', type=int)
    observacion = request.form.get('observacion')
    archivo = request.files.get('archivo')
    mes_vista = request.form.get('mes_vista', type=int)
    anio_vista = request.form.get('anio_vista', type=int)

    def _back():
        if anio_vista and mes_vista:
            return redirect(url_for('feed_stories.index', anio=anio_vista, mes=mes_vista))
        return redirect(url_for('feed_stories.index'))

    if tipo not in ('feed', 'stories') or not fecha_publicacion or not hora_publicacion or not archivo:
        flash('Completa tipo, fecha, hora y archivo.', 'error')
        return _back()
    if not _allowed(archivo.filename):
        flash('Formato no permitido.', 'error')
        return _back()

    try:
        fecha_dt = datetime.strptime(fecha_publicacion, '%Y-%m-%d')
    except ValueError:
        flash('Fecha invalida.', 'error')
        return _back()

    nombre_original = secure_filename(archivo.filename)
    carpeta = os.path.join(
        current_app.config['UPLOAD_FOLDER'],
        'feed_stories',
        tipo,
        f'{fecha_dt.year:04d}',
        f'{fecha_dt.month:02d}',
        f'{fecha_dt.day:02d}',
    )
    os.makedirs(carpeta, exist_ok=True)
    final_name = f"{uuid4().hex}_{nombre_original}"
    ruta = os.path.join(carpeta, final_name)

    try:
        archivo.save(ruta)
    except Exception:
        flash('No se pudo guardar el archivo.', 'error')
        return _back()

    nuevo_id = FeedStoryDAO.insertar(
        tipo=tipo,
        fecha_publicacion=fecha_publicacion,
        hora_publicacion=hora_publicacion,
        copy_texto=copy_texto,
        archivo_nombre=nombre_original,
        archivo_ruta=ruta,
        responsable_id=responsable_id,
        observacion=observacion,
    )

    if not nuevo_id:
        try:
            if os.path.exists(ruta):
                os.remove(ruta)
        except OSError:
            pass
        flash('No se pudo registrar el contenido en base de datos.', 'error')
        return _back()

    flash('Contenido cargado.', 'success')
    return _back()


@feed_stories_bp.route('/descargar/<int:id>')
@login_required
@requiere_permiso('feed_stories')
def descargar(id):
    item = FeedStoryDAO.obtener(id)
    if not item:
        abort(404)
    ruta = item['archivo_ruta']
    if not os.path.exists(ruta):
        abort(404)
    return send_file(ruta, as_attachment=True, download_name=item['archivo_nombre'])


@feed_stories_bp.route('/publicado/<int:id>', methods=['POST'])
@login_required
@requiere_permiso('feed_stories', requiere_editar=True)
def marcar_publicado(id):
    if not FeedStoryDAO.marcar_publicado(id):
        flash('No se pudo actualizar el estado.', 'error')
    else:
        flash('Marcado como publicado.', 'success')
    return redirect(request.referrer or url_for('feed_stories.index'))


@feed_stories_bp.route('/observacion/<int:id>', methods=['POST'])
@login_required
@requiere_permiso('feed_stories', requiere_editar=True)
def guardar_observacion(id):
    if not FeedStoryDAO.actualizar_observacion(id, request.form.get('observacion')):
        flash('No se pudo guardar la observacion.', 'error')
    else:
        flash('Observacion guardada.', 'success')
    return redirect(request.referrer or url_for('feed_stories.index'))


@feed_stories_bp.route('/ideas')
@login_required
@requiere_permiso('ideas_feed_stories')
def ideas():
    hoy = date.today()
    anio = request.args.get('anio', type=int, default=hoy.year)
    mes = request.args.get('mes', type=int, default=hoy.month)
    ideas_rows = IdeaFeedStoryDAO.listar(anio=anio, mes=mes)
    usuarios = UsuarioDAO.listar()
    return render_template('feed_stories/ideas.html', ideas=ideas_rows, usuarios=usuarios, anio=anio, mes=mes)


@feed_stories_bp.route('/ideas/nueva', methods=['POST'])
@login_required
@requiere_permiso('ideas_feed_stories', requiere_editar=True)
def idea_nueva():
    try:
        mes = int(request.form.get('mes') or 0)
        anio = int(request.form.get('anio') or 0)
    except ValueError:
        flash('Mes/anio invalidos.', 'error')
        return redirect(url_for('feed_stories.ideas'))
    IdeaFeedStoryDAO.insertar(
        tipo=request.form.get('tipo'),
        titulo=request.form.get('titulo'),
        detalle=request.form.get('detalle'),
        copy_texto=request.form.get('copy_texto'),
        mes=mes,
        anio=anio,
        agrupador=request.form.get('agrupador'),
        responsable_id=request.form.get('responsable_id', type=int),
    )
    flash('Idea guardada.', 'success')
    return redirect(url_for('feed_stories.ideas', anio=anio, mes=mes))


@feed_stories_bp.route('/ideas/pasar/<int:id>', methods=['POST'])
@login_required
@requiere_permiso('ideas_feed_stories', requiere_editar=True)
def idea_pasar(id):
    idea = next((x for x in IdeaFeedStoryDAO.listar() if x['id'] == id), None)
    if not idea:
        flash('Idea no encontrada.', 'error')
        return redirect(url_for('feed_stories.ideas'))
    IdeaFeedStoryDAO.marcar_pasada(id)
    flash('Idea marcada como pasada a operativo. Carga el archivo en Feed & Stories.', 'success')
    return redirect(url_for('feed_stories.ideas', anio=idea['anio'], mes=idea['mes']))
