#!/usr/bin/env python3
"""Add a new painting to the top of the home page gallery.

Usage:
  python3 site-tools/add_painting.py --image PHOTO --title "Title" \
      --size "30x24 inches (76x61 cm)" --medium "Acrylic on canvas" \
      [--status "Available"] [--about "Optional note"] [--dry-run]

What it does:
  * Fixes the photo's rotation, saves a large copy (max 2048 px) and a
    gallery copy (max 1024 px) as JPEG under Current/wp-content/uploads/YYYY/MM/
  * Inserts the painting FIRST in the home page gallery and in the
    painting viewer data, and updates the "N works" count
  * Never touches any other painting

Run from the repository root. Needs Pillow; for iPhone HEIC photos also
`pip install pillow-heif`.
"""
import argparse, datetime, html, json, os, re, sys, unicodedata

from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "Current")
HOME = os.path.join(SITE, "index.html")


def slugify(text):
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    t = re.sub(r"[^A-Za-z0-9]+", "-", t).strip("-")
    return t[:80] or "painting"


def open_image(path):
    try:
        import pillow_heif  # noqa: F401
        pillow_heif.register_heif_opener()
    except ImportError:
        pass
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)
    if im.mode not in ("RGB",):
        im = im.convert("RGB")
    return im


def save_resized(im, max_side, dest):
    copy = im.copy()
    copy.thumbnail((max_side, max_side), Image.LANCZOS)
    copy.save(dest, "JPEG", quality=88, optimize=True, progressive=True)
    return copy.size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--size", required=True)
    ap.add_argument("--medium", required=True)
    ap.add_argument("--status", default="")
    ap.add_argument("--about", default="")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    page = open(HOME, encoding="utf-8").read()

    # --- painting data used by the viewer
    m = re.search(r'(<script id="kb-paintings" type="application/json">)(.*?)(</script>)', page, re.S)
    if not m:
        sys.exit("Could not find the painting data in Current/index.html")
    data = json.loads(m.group(2).replace("<\\/", "</"))
    if any(p["t"].strip().lower() == a.title.strip().lower() for p in data):
        sys.exit(f'A painting titled "{a.title}" is already on the site. Stopping so it is not added twice.')

    # --- images
    now = datetime.date.today()
    rel_dir = f"wp-content/uploads/{now:%Y}/{now:%m}"
    abs_dir = os.path.join(SITE, rel_dir)
    os.makedirs(abs_dir, exist_ok=True)
    base = slugify(a.title)
    n = 1
    while os.path.exists(os.path.join(abs_dir, f"{base}.jpg")):
        n += 1
        base = f"{slugify(a.title)}-{n}"
    im = open_image(a.image)
    full_name, thumb_name = f"{base}.jpg", f"{base}-1024.jpg"
    if a.dry_run:
        fw, fh = (lambda c: (c.thumbnail((2048, 2048)), c.size)[1])(im.copy())
        tw, th = (lambda c: (c.thumbnail((1024, 1024)), c.size)[1])(im.copy())
    else:
        fw, fh = save_resized(im, 2048, os.path.join(abs_dir, full_name))
        tw, th = save_resized(im, 1024, os.path.join(abs_dir, thumb_name))
    full_url = f"/{rel_dir}/{full_name}"
    thumb_url = f"/{rel_dir}/{thumb_name}"

    rows = [["Size", a.size.strip()], ["Medium", a.medium.strip()]]
    if a.status.strip():
        rows.append(["Status", a.status.strip()])
    if a.about.strip():
        rows.append(["Info", a.about.strip()])

    entry = dict(t=a.title.strip(), rows=rows, full=full_url,
                 set=f"{full_url} {fw}w, {thumb_url} {tw}w", w=fw, h=fh)
    data.insert(0, entry)
    new_json = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    page = page[:m.start(2)] + new_json + page[m.end(2):]

    # --- gallery tiles: shift existing indexes by one, then add the new tile first
    gstart = page.index('<div class="kb-justify">')
    gend = page.index('</section>', gstart)
    gallery = page[gstart:gend]
    gallery = re.sub(r'data-i="(\d+)"', lambda x: f'data-i="{int(x.group(1)) + 1}"', gallery)
    e = html.escape
    tile = (f'<a class="kb-tile" href="{e(full_url)}" data-i="0" style="--r:{tw / th:.4f}">'
            f'<img src="{e(thumb_url)}" srcset="{e(entry["set"])}" sizes="(max-width: 700px) 60vw, 30vw" '
            f'width="{tw}" height="{th}" alt="{e(entry["t"])}" loading="eager" decoding="async">'
            f'<span class="kb-tile__cap">{e(entry["t"])}</span></a>')
    head = '<div class="kb-justify">'
    gallery = gallery.replace(head, head + "\n        " + tile, 1)
    page = page[:gstart] + gallery + page[gend:]

    # --- count
    page, k = re.subn(r'<p>\d+ works &middot;', f'<p>{len(data)} works &middot;', page, count=1)

    tiles = len(re.findall(r'class="kb-tile"', page))
    if tiles != len(data):
        sys.exit(f"Safety check failed: {tiles} tiles but {len(data)} paintings. Nothing was saved.")

    if a.dry_run:
        print("DRY RUN, nothing saved.")
    else:
        open(HOME, "w", encoding="utf-8").write(page)
    print(json.dumps({"added": entry["t"], "rows": rows, "image": full_url, "gallery_image": thumb_url,
                      "total_paintings": len(data)}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
