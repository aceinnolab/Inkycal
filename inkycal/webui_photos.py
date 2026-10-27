"""Photos card for the Inkycal web UI: upload, list, delete and show pictures for the Slideshow module.

Uploaded pictures are turned upright (EXIF), shrunk to at most MAX_SIDE px on the long side and
stored as JPG in PHOTO_DIR (default ``~/inkycal_images``). Small thumbnails for the page are kept in
``PHOTO_DIR/.thumbs``. Only the Python standard library and Pillow are used.
"""

from __future__ import annotations

import html
import io
import os
import re
import urllib.parse
from email.parser import BytesParser
from email.policy import default as email_policy
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PIL import Image, ImageOps

PHOTO_DIR = Path(os.getenv("INKYCAL_PHOTO_DIR", str(Path.home() / "inkycal_images")))
THUMB_DIR = PHOTO_DIR / ".thumbs"
MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # per request; the page sends one picture per request
MAX_SIDE = 1600  # about 2x the 800 x 480 display, enough for crops and autoflip
THUMB_SIDE = 240
JPEG_QUALITY = 90
SLIDESHOW = "Slideshow"
CACHE_NAME = "inkycal_slideshow"

ACTIONS = {"photo_delete", "photo_show", "photo_next", "photos_use_folder"}

_SUFFIXES = (".jpg", ".jpeg", ".png")


class _Outcome:
    def __init__(self, message: str, sudo_required: bool = False):
        self.message = message
        self.sudo_required = sudo_required


# ---------------------------------------------------------------------------
# Files
# ---------------------------------------------------------------------------
def list_photos() -> List[str]:
    """File names in PHOTO_DIR in the order the slideshow shows them."""
    try:
        names = [p.name for p in PHOTO_DIR.iterdir()
                 if p.is_file() and not p.name.startswith(".") and p.suffix.lower() in _SUFFIXES]
    except OSError:
        return []
    return sorted(names, key=str.lower)


def _existing(name: str) -> Optional[Path]:
    """Path of a photo by its plain file name - never anything outside PHOTO_DIR."""
    return PHOTO_DIR / name if name in list_photos() else None


def _clean_stem(filename: str) -> str:
    stem = Path(filename.replace("\\", "/")).stem
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._-")
    return stem[:60] or "photo"


def _free_name(stem: str) -> str:
    taken = {n.lower() for n in list_photos()}
    name, n = f"{stem}.jpg", 2
    while name.lower() in taken:
        name, n = f"{stem}-{n}.jpg", n + 1
    return name


def save_upload(filename: str, data: bytes) -> str:
    """Store one uploaded picture. Returns the saved file name, raises ValueError with a readable message."""
    if not data:
        raise ValueError(f"{filename}: empty file")
    try:
        im = Image.open(io.BytesIO(data))
        im.draft("RGB", (MAX_SIDE, MAX_SIDE))  # JPEG: decode at reduced size, fast + little memory
        im = ImageOps.exif_transpose(im)
        im.load()
    except Exception:
        if filename.lower().endswith((".heic", ".heif")):
            raise ValueError(f"{filename}: HEIC is not supported - please send it as JPG")
        raise ValueError(f"{filename}: not a picture this frame can read (use JPG or PNG)")

    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        background = Image.new("RGB", im.size, "white")
        background.paste(im, mask=im.getchannel("A"))
        im = background
    else:
        im = im.convert("RGB")
    im.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)

    PHOTO_DIR.mkdir(parents=True, exist_ok=True)
    name = _free_name(_clean_stem(filename))
    tmp = PHOTO_DIR / f".{name}.part"
    im.save(tmp, "JPEG", quality=JPEG_QUALITY, optimize=True)
    tmp.replace(PHOTO_DIR / name)  # atomic: the slideshow never sees half a file
    return name


def delete_photo(name: str) -> bool:
    path = _existing(name)
    if not path:
        return False
    path.unlink(missing_ok=True)
    (THUMB_DIR / name).unlink(missing_ok=True)
    return True


def thumb_bytes(name: str) -> Optional[bytes]:
    path = _existing(name)
    if not path:
        return None
    thumb = THUMB_DIR / name
    try:
        if not thumb.exists() or thumb.stat().st_mtime < path.stat().st_mtime:
            THUMB_DIR.mkdir(parents=True, exist_ok=True)
            with Image.open(path) as im:
                im.draft("RGB", (THUMB_SIDE, THUMB_SIDE))
                im = im.convert("RGB")
                im.thumbnail((THUMB_SIDE, THUMB_SIDE))
                im.save(thumb, "JPEG", quality=80)
        return thumb.read_bytes()
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Upload request (multipart/form-data)
# ---------------------------------------------------------------------------
def parse_multipart(content_type: str, body: bytes) -> Tuple[Dict[str, List[str]], List[Tuple[str, bytes]]]:
    """Returns (plain fields, [(filename, data), ...]) without the removed ``cgi`` module."""
    head = f"MIME-Version: 1.0\r\nContent-Type: {content_type}\r\n\r\n".encode("latin-1")
    message = BytesParser(policy=email_policy).parsebytes(head + body)
    fields: Dict[str, List[str]] = {}
    files: List[Tuple[str, bytes]] = []
    if not message.is_multipart():
        return fields, files
    for part in message.iter_parts():
        name = part.get_param("name", header="content-disposition")
        filename = part.get_filename()
        payload = part.get_payload(decode=True) or b""
        if filename is not None:
            if payload:
                files.append((filename, payload))
        elif name:
            fields.setdefault(name, []).append(payload.decode("utf-8", "replace"))
    return fields, files


def handle_upload(content_type: str, body: bytes) -> Tuple[bool, str]:
    if not content_type.lower().startswith("multipart/form-data"):
        return False, "Upload failed: wrong form type."
    try:
        _, files = parse_multipart(content_type, body)
    except Exception as error:
        return False, f"Upload failed: {error}"
    if not files:
        return False, "Upload failed: no picture selected."
    saved, errors = [], []
    for filename, data in files:
        try:
            saved.append(save_upload(filename, data))
        except ValueError as error:
            errors.append(str(error))
        except OSError as error:
            errors.append(f"{filename}: could not save ({error})")
    parts = []
    if saved:
        parts.append(f"{len(saved)} picture{'s' if len(saved) != 1 else ''} uploaded.")
    if errors:
        parts.append("Not uploaded: " + "; ".join(errors))
    return bool(saved), " ".join(parts)


# ---------------------------------------------------------------------------
# Slideshow state + settings
# ---------------------------------------------------------------------------
def _cache():
    from inkycal.utils import JSONCache
    return JSONCache(CACHE_NAME)


def _slideshows(data: Dict[str, object]) -> List[dict]:
    modules = data.get("modules") if isinstance(data.get("modules"), list) else []
    return [m for m in modules if isinstance(m, dict) and m.get("name") == SLIDESHOW
            and isinstance(m.get("config"), dict)]


def _same_dir(path: object) -> bool:
    try:
        return Path(os.path.expanduser(str(path))).resolve() == PHOTO_DIR.resolve()
    except Exception:
        return False


def handle(action: str, form: Dict[str, List[str]], sudo_password: str = ""):
    from inkycal import webui_extras as extras
    W = extras._webui()
    name = form.get("photo", [""])[0]

    if action == "photo_delete":
        if delete_photo(name):
            return _Outcome(f"{name} deleted.")
        return _Outcome("Delete failed: picture not found.")

    if action in ("photo_show", "photo_next"):
        if action == "photo_show":
            if not _existing(name):
                return _Outcome("Picture not found.")
            cache = _cache()
            data = cache.read()
            data["next_image"] = name
            cache.write(data)
            msg = f"{name} is shown next."
        else:
            msg = "Next picture."
        r = extras.power_action("power_refresh", sudo_password)
        if r.sudo_required or r.message.startswith("Refresh failed"):
            return _Outcome(f"{msg} {r.message}", r.sudo_required)
        return _Outcome(f"{msg} The display updates in about 20 seconds.")

    if action == "photos_use_folder":
        data = W._read_settings_json()
        shows = _slideshows(data)
        if not shows:
            return _Outcome("There is no Slideshow module yet. Add one in Settings (Add module: Slideshow).")
        for mod in shows:
            mod["config"]["path"] = str(PHOTO_DIR)
        extras.backup_settings()
        outcome = W._write_settings_json(data, "Saving folder failed", sudo_password=sudo_password)
        if outcome:
            return outcome
        r = extras.power_action("power_refresh", sudo_password)
        if r.sudo_required or r.message.startswith("Refresh failed"):
            return _Outcome(f"Slideshow now uses {PHOTO_DIR}. {r.message}", r.sudo_required)
        return _Outcome(f"Slideshow now uses {PHOTO_DIR}. The display updates in about 20 seconds.")

    return _Outcome("Unknown photo action.")


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------
def render_card(settings_data: Dict[str, object]) -> str:
    photos = list_photos()
    shows = _slideshows(settings_data if isinstance(settings_data, dict) else {})
    try:
        state = _cache().read()
    except Exception:
        state = {}
    current = state.get("last_image") if shows else None

    if not shows:
        status = ("<p class='muted'>No Slideshow module yet. Add one in <strong>Settings</strong> "
                  "(Add module: Slideshow), then press <em>Use this folder</em>.</p>")
    elif all(_same_dir(m["config"].get("path", "")) for m in shows):
        status = "<p class='muted'>The Slideshow module uses this folder. Pictures are shown in name order.</p>"
    else:
        status = ("<p class='kv-warn'>The Slideshow module uses a different folder. "
                  "Press <em>Use this folder</em> to show these pictures.</p>")

    use_button = ("" if shows and all(_same_dir(m["config"].get("path", "")) for m in shows) else
                  "<button name='action' value='photos_use_folder' class='secondary'>Use this folder</button>")
    next_button = ("<button name='action' value='photo_next'>Show next picture now</button>"
                   if shows and photos else "")

    tiles = []
    for index, name in enumerate(photos, 1):
        q = urllib.parse.quote(name)
        n = html.escape(name)
        badge = "<span class='ph-badge'>on display</span>" if name == current else ""
        tiles.append(
            f"<figure class='ph-tile{' ph-current' if name == current else ''}'>"
            f"<img loading='lazy' src='/photos/thumb/{q}' alt='{n}'>{badge}"
            f"<figcaption title='{n}'>{index}. {n}</figcaption>"
            "<form method='post' class='ph-actions'>"
            f"<input type='hidden' name='photo' value='{n}'>"
            + ("<button name='action' value='photo_show' class='small'>Show now</button>" if shows else "")
            + "<button name='action' value='photo_delete' class='small danger' "
            f"onclick=\"return confirm('Delete {n}?')\">Delete</button>"
            "</form></figure>"
        )
    grid = (f"<div class='ph-grid'>{''.join(tiles)}</div>" if tiles
            else "<p class='muted'>No pictures yet.</p>")

    return f"""
    <section class='card photos-card' data-card='photos'>
      <h2>Photos</h2>
      {status}
      <form method='post' action='/photos/upload' enctype='multipart/form-data' id='photoUpload' class='ph-upload'>
        <label class='ph-drop' id='photoDrop'>
          <input type='file' name='photos' id='photoInput' accept='image/jpeg,image/png,image/webp' multiple>
          <span>Choose pictures or drop them here (JPG / PNG)</span>
        </label>
        <div class='button-row'><button type='submit'>Upload</button></div>
        <p class='muted' id='photoProgress'></p>
      </form>
      <form method='post'><div class='button-row'>{next_button}{use_button}</div></form>
      <p class='muted'>{len(photos)} picture{'s' if len(photos) != 1 else ''} in <code>{html.escape(str(PHOTO_DIR))}</code>.
      Pictures are turned upright and shrunk to {MAX_SIDE} px when uploaded.</p>
      {grid}
    </section>
    """


CSS = """
    .photos-card { margin-bottom: 1rem; }
    .ph-upload { margin: 0.6rem 0; }
    .ph-drop { display: block; border: 2px dashed var(--border); border-radius: 12px; padding: 1rem; text-align: center; cursor: pointer; color: var(--muted); }
    .ph-drop.over { border-color: var(--accent); color: var(--accent); }
    .ph-drop input { display: block; margin: 0 auto 0.5rem; width: auto; max-width: 100%; box-sizing: border-box; }
    .ph-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 0.7rem; margin-top: 0.6rem; }
    .ph-tile { margin: 0; border: 1px solid var(--border); border-radius: 10px; overflow: hidden; background: #fff; position: relative; }
    .ph-tile img { width: 100%; aspect-ratio: 5 / 3; object-fit: cover; display: block; background: #f3f3f1; }
    .ph-tile figcaption { font-size: 0.78rem; padding: 0.3rem 0.45rem 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .ph-current { outline: 3px solid var(--accent); }
    .ph-badge { position: absolute; top: 6px; left: 6px; background: var(--accent); color: #fff; font-size: 0.7rem; padding: 0.05rem 0.4rem; border-radius: 6px; }
    .ph-actions { display: flex; gap: 0.3rem; padding: 0.35rem 0.45rem 0.45rem; flex-wrap: wrap; }
"""

JS = """
    (function() {
      const form = document.getElementById('photoUpload');
      if (!form || !window.fetch || !window.FormData) return;
      const input = document.getElementById('photoInput');
      const drop = document.getElementById('photoDrop');
      const out = document.getElementById('photoProgress');
      ['dragenter', 'dragover'].forEach(t => drop.addEventListener(t, e => { e.preventDefault(); drop.classList.add('over'); }));
      ['dragleave', 'drop'].forEach(t => drop.addEventListener(t, () => drop.classList.remove('over')));
      drop.addEventListener('drop', e => { e.preventDefault(); if (e.dataTransfer.files.length) { input.files = e.dataTransfer.files; send(); } });
      form.addEventListener('submit', e => { e.preventDefault(); send(); });
      async function send() {
        const files = [...input.files];
        if (!files.length) { out.textContent = 'Choose pictures first.'; return; }
        let ok = 0; const errors = [];
        for (let i = 0; i < files.length; i++) {
          out.textContent = 'Uploading ' + (i + 1) + ' of ' + files.length + ' …';
          const fd = new FormData(); fd.append('photos', files[i], files[i].name);
          try {
            const r = await fetch('/photos/upload', { method: 'POST', body: fd, headers: { 'Accept': 'application/json' } });
            const d = await r.json();
            if (d.ok) ok++; else errors.push(d.message);
          } catch (err) { errors.push(files[i].name + ': ' + err); }
        }
        let msg = ok + ' picture' + (ok === 1 ? '' : 's') + ' uploaded.';
        if (errors.length) msg += ' ' + errors.join(' ');
        location.href = '/?msg=' + encodeURIComponent(msg);
      }
    })();
"""
