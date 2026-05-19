import os
import subprocess
from uuid import uuid4
from datetime import date, datetime
import mimetypes
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


def _build_preview_path(ruta_original):
    base, _ext = os.path.splitext(ruta_original)
    return f"{base}__preview.mp4"


def _resolve_ruta_guardada(ruta_db):
    if not ruta_db:
        return None

    if os.path.exists(ruta_db):
        return ruta_db

    normal = str(ruta_db).replace('\\', '/')

    if normal.startswith('static/uploads/'):
        candidata = os.path.join(current_app.root_path, normal.replace('/', os.sep))
        if os.path.exists(candidata):
            return candidata

    marker = '/uploads/'
    idx = normal.lower().find(marker)
    if idx != -1:
        sub = normal[idx + 1:]  # uploads/...
        candidata = os.path.join(current_app.root_path, 'static', sub.replace('/', os.sep))
        if os.path.exists(candidata):
            return candidata

    return None


def _crear_preview_video(ruta_original):
    """Crea mp4 web-compatible para previsualizacion. Mantiene original para descarga."""
    preview = _build_preview_path(ruta_original)
    cmd = [
        "ffmpeg", "-y",
        "-i", ruta_original,
        "-vcodec", "libx264",
        "-acodec", "aac",
        "-movflags", "+faststart",
        "-pix_fmt", "yuv420p",
        preview
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if proc.returncode == 0 and os.path.exists(preview):
            return preview
    except Exception:
        pass
    return None


@feed_stories_bp.route('/')
@login_required
@requiere_permiso('feed_stories')
def index():
    hoy = date.today()
    anio = request.args.get('anio', type=int, default=hoy.year)
    mes = request.args.get('mes', type=int, default=hoy.month)
    tipo = request.args.get('tipo') or 'feed'
    vista = request.args.get('vista') or 'carpetas'  # carpetas | preview
    semana = request.args.get('semana')
    dia_semana = None
    contenidos = FeedStoryDAO.listar(anio=anio, mes=mes, tipo=tipo, dia_semana=dia_semana)
    usuarios = UsuarioDAO.listar()

    feed = [c for c in contenidos if c.get('tipo') == 'feed']
    stories = [c for c in contenidos if c.get('tipo') == 'stories']

    def _semana_del_mes(fecha_val):
        d = fecha_val.day if hasattr(fecha_val, 'day') else int(str(fecha_val).split('-')[-1])
        if d <= 7:
            return 'Semana 1-7'
        if d <= 14:
            return 'Semana 8-14'
        if d <= 21:
            return 'Semana 15-21'
        if d <= 28:
            return 'Semana 22-28'
        return 'Semana 29-fin'

    def _agrupar(items):
        grupos = {}
        for it in items:
            f = it.get('fecha_publicacion')
            if not f:
                continue
            semana = _semana_del_mes(f)
            fecha_key = str(f)
            grupos.setdefault(semana, {}).setdefault(fecha_key, []).append(it)
        return grupos

    feed_grupos = _agrupar(feed)
    stories_grupos = _agrupar(stories)
    grupos_actual = feed_grupos if tipo == 'feed' else stories_grupos
    semanas = list(grupos_actual.keys())
    semana_activa = semana if semana in grupos_actual else None
    contenidos_semana = grupos_actual.get(semana_activa, {}) if semana_activa else {}

    # Previsualizacion estilo feed (orden cronologico)
    feed_sorted = sorted(
        feed,
        key=lambda x: (str(x.get('fecha_publicacion') or ''), str(x.get('hora_publicacion') or ''), x.get('id') or 0)
    )
    last_published_idx = -1
    for i, item in enumerate(feed_sorted):
        if item.get('estado') == 'publicado':
            last_published_idx = i
    next_idx = last_published_idx + 1 if (last_published_idx + 1) < len(feed_sorted) else None

    return render_template(
        'feed_stories/index.html',
        contenidos=contenidos,
        feed=feed,
        stories=stories,
        semanas=semanas,
        semana_activa=semana_activa,
        contenidos_semana=contenidos_semana,
        usuarios=usuarios,
        anio=anio,
        mes=mes,
        tipo=tipo,
        vista=vista,
        feed_preview=feed_sorted,
        last_published_idx=last_published_idx,
        next_idx=next_idx,
        hoy=hoy,
    )


@feed_stories_bp.route('/nuevo', methods=['POST'])
@login_required
@requiere_permiso('feed_stories', requiere_editar=True)
def nuevo():
    tipo = request.form.get('tipo')
    fecha_publicacion = request.form.get('fecha_publicacion')
    hora_publicacion = '09:00'
    copy_texto = None
    responsable_id = None
    observacion = None
    archivos = request.files.getlist('archivo')
    mes_vista = request.form.get('mes_vista', type=int)
    anio_vista = request.form.get('anio_vista', type=int)

    def _back():
        if anio_vista and mes_vista:
            return redirect(url_for('feed_stories.index', anio=anio_vista, mes=mes_vista))
        return redirect(url_for('feed_stories.index'))

    if tipo not in ('feed', 'stories') or not fecha_publicacion or not archivos:
        flash('Completa tipo, fecha y archivo.', 'error')
        return _back()

    try:
        fecha_dt = datetime.strptime(fecha_publicacion, '%Y-%m-%d')
    except ValueError:
        flash('Fecha invalida.', 'error')
        return _back()

    carpeta = os.path.join(
        current_app.config['UPLOAD_FOLDER'],
        'feed_stories',
        tipo,
        f'{fecha_dt.year:04d}',
        f'{fecha_dt.month:02d}',
        f'{fecha_dt.day:02d}',
    )
    os.makedirs(carpeta, exist_ok=True)
    subidos = 0
    for archivo in archivos:
        if not archivo or not archivo.filename:
            continue
        if not _allowed(archivo.filename):
            continue
        nombre_original = secure_filename(archivo.filename)
        final_name = f"{uuid4().hex}_{nombre_original}"
        ruta = os.path.join(carpeta, final_name)
        try:
            archivo.save(ruta)
        except Exception:
            continue

        if nombre_original.lower().endswith(('.mov', '.avi', '.mp4')):
            _crear_preview_video(ruta)

        ruta_rel = os.path.join(
            'static',
            'uploads',
            'feed_stories',
            tipo,
            f'{fecha_dt.year:04d}',
            f'{fecha_dt.month:02d}',
            f'{fecha_dt.day:02d}',
            final_name,
        )

        nuevo_id = FeedStoryDAO.insertar(
            tipo=tipo,
            fecha_publicacion=fecha_publicacion,
            hora_publicacion=hora_publicacion,
            copy_texto=copy_texto,
            archivo_nombre=nombre_original,
            archivo_ruta=ruta_rel,
            responsable_id=responsable_id,
            observacion=observacion,
        )
        if not nuevo_id:
            try:
                if os.path.exists(ruta):
                    os.remove(ruta)
            except OSError:
                pass
            continue
        subidos += 1

    if subidos == 0:
        flash('No se pudo cargar ningun archivo.', 'error')
    else:
        flash(f'Contenidos cargados: {subidos}', 'success')
    return _back()


@feed_stories_bp.route('/descargar/<int:id>')
@login_required
@requiere_permiso('feed_stories')
def descargar(id):
    item = FeedStoryDAO.obtener(id)
    if not item:
        flash('Contenido no encontrado.', 'error')
        return redirect(url_for('feed_stories.index'))
    ruta = _resolve_ruta_guardada(item.get('archivo_ruta'))
    if not ruta or not os.path.exists(ruta):
        flash('Archivo no encontrado en servidor.', 'error')
        return redirect(url_for('feed_stories.index'))
    return send_file(ruta, as_attachment=True, download_name=item['archivo_nombre'])


@feed_stories_bp.route('/ver/<int:id>')
@login_required
@requiere_permiso('feed_stories')
def ver_archivo(id):
    item = FeedStoryDAO.obtener(id)
    if not item:
        abort(404)
    ruta = _resolve_ruta_guardada(item.get('archivo_ruta'))
    if not ruta:
        abort(404)
    use_preview = request.args.get('preview') == '1'
    if use_preview and item.get('archivo_nombre', '').lower().endswith(('.mov', '.avi', '.mp4')):
        preview = _build_preview_path(ruta)
        if os.path.exists(preview):
            ruta = preview
    if not os.path.exists(ruta):
        abort(404)
    nombre_mime = os.path.basename(ruta)
    mime = mimetypes.guess_type(nombre_mime or '')[0]
    return send_file(ruta, mimetype=mime or None)


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


@feed_stories_bp.route('/actualizar/<int:id>', methods=['POST'])
@login_required
@requiere_permiso('feed_stories', requiere_editar=True)
def actualizar_card(id):
    item = FeedStoryDAO.obtener(id)
    if not item:
        flash('Contenido no encontrado.', 'error')
        return redirect(url_for('feed_stories.index'))
    hora = request.form.get('hora_publicacion') or item.get('hora_publicacion') or '09:00'
    copy_texto = request.form.get('copy_texto')
    responsable_id = request.form.get('responsable_id', type=int)
    observacion = request.form.get('observacion')
    ok = FeedStoryDAO.actualizar_detalle(id, hora, copy_texto, responsable_id, observacion)
    if ok:
        flash('Tarjeta actualizada.', 'success')
    else:
        flash('No se pudo actualizar la tarjeta.', 'error')
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
