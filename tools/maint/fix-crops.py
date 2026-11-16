"""Re-frames photo magnets of one order so faces aren't cut, without anyone seeing the photos.

ORDER_PHOTOS = "LHH-1003:1,3,8,12,15,16" (photo numbers as the order page shows them, counted across the order's
photo packs). For each photo: reads the original from Storage (upright, EXIF applied), finds the faces (OpenCV YuNet,
Haar as a fallback) and picks where the square window sits so every face has headroom and as much of the bodies below
shows as fits. Saves the new crop {x, y, z} in the order (the same crop the customer's "move and zoom" makes: see
functions/crop.js) unless DRY_RUN=1. Prints only numbers: no image, no name, no address.
Run by .github/workflows/maint.yml (task fix-crops)."""
import io, os, sys
import numpy as np, cv2
from PIL import Image, ImageOps
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except Exception:
    pass
from google.cloud import firestore, storage

PROJECT = os.environ.get("PROJECT", "little-hive-house")
BUCKET = os.environ.get("BUCKET", f"{PROJECT}.firebasestorage.app")
spec = (os.environ.get("ORDER_PHOTOS") or "").strip()
dry = os.environ.get("DRY_RUN", "0") == "1"
if ":" not in spec:
    sys.exit('ORDER_PHOTOS must look like "LHH-1003:1,3,8"')
number, nums = spec.split(":", 1)
wanted = sorted({int(n) for n in nums.replace(" ", "").split(",") if n})

db = firestore.Client(project=PROJECT)
bucket = storage.Client(project=PROJECT).bucket(BUCKET)
snap = list(db.collection("orders").where("number", "==", number.strip()).limit(1).stream())
if not snap:
    sys.exit(f"order {number} not found")
ref = snap[0].reference
order = snap[0].to_dict()

yunet = None
if os.path.exists("/tmp/yunet.onnx"):
    try:
        yunet = cv2.FaceDetectorYN.create("/tmp/yunet.onnx", "", (320, 320), 0.75, 0.3, 5000)
    except Exception as e:
        print("YuNet unavailable:", e)
haar = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


def faces_in(img):
    """[(x, y, w, h)] in the upright image's pixels, small false hits removed."""
    W, H = img.size
    k = 1600 / max(W, H)
    small = img.convert("RGB").resize((max(1, int(W * k)), max(1, int(H * k))))
    bgr = cv2.cvtColor(np.array(small), cv2.COLOR_RGB2BGR)
    found = []
    if yunet is not None:
        yunet.setInputSize((bgr.shape[1], bgr.shape[0]))
        _, dets = yunet.detect(bgr)
        if dets is not None:
            found = [tuple(d[:4]) for d in dets if d[-1] >= 0.75]
    if not found:
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        found = [tuple(f) for f in haar.detectMultiScale(gray, 1.1, 6, minSize=(40, 40))]
    m = min(bgr.shape[:2])
    found = [f for f in found if f[2] >= 0.04 * m]
    return [(x / k, y / k, w / k, h / k) for x, y, w, h in found]


def pick(W, H, faces):
    """New crop {x, y, z}: square window at zoom 1, placed for heads with headroom and bodies below."""
    S = min(W, H)
    if not faces:
        return None, "no faces found"
    fh = max(f[3] for f in faces)
    if H > W:   # portrait: slide up/down
        need_top = max(0, min(f[1] for f in faces) - 1.1 * fh)           # hair, hats, bows (a big bow is about a face tall)
        want_bottom = min(H, max(f[1] + f[3] for f in faces) + 2.2 * fh)  # shoulders and some body
        lo, hi = want_bottom - S, need_top                               # any top in [lo, hi] keeps both
        top = (lo + hi) / 2 if lo <= hi else need_top                    # can't keep both: heads first
        top = min(max(0, top), H - S)
        return {"x": 0.5, "y": round(float((top + S / 2) / H), 4), "z": 1}, f"top at {top / H:.0%} of the height"
    if W > H:   # landscape: slide left/right around the people
        l = max(0, min(f[0] for f in faces) - 0.4 * fh)
        r = min(W, max(f[0] + f[2] for f in faces) + 0.4 * fh)
        left = min(max(0, (l + r) / 2 - S / 2), W - S)
        return {"x": round(float((left + S / 2) / W), 4), "y": 0.5, "z": 1}, f"left at {left / W:.0%} of the width"
    return None, "square photo: nothing to move"


def inside(W, H, crop, faces):
    """How many faces (with headroom) sit fully inside the window for this crop."""
    S = min(W, H)
    c = crop or {"x": 0.5, "y": 0.5}
    left = min(max(0, c["x"] * W - S / 2), W - S); top = min(max(0, c["y"] * H - S / 2), H - S)
    n = 0
    for x, y, w, h in faces:
        if x >= left and x + w <= left + S and y - 0.3 * h >= top and y + h <= top + S:
            n += 1
    return n


items = order.get("items") or []
flat = []
for i, it in enumerate(items):
    if it.get("kind") == "photos":
        for j, p in enumerate(it.get("photos") or []):
            flat.append((i, j, p))
print(f"order {number}: {len(flat)} photos; working on {wanted}; {'DRY RUN, nothing saved' if dry else 'saving'}")
changed = 0
for n in wanted:
    if n < 1 or n > len(flat):
        print(f"photo {n}: not in this order"); continue
    i, j, p = flat[n - 1]
    blob = bucket.blob(p["path"])
    img = ImageOps.exif_transpose(Image.open(io.BytesIO(blob.download_as_bytes())))
    W, H = img.size
    faces = faces_in(img)
    new, why = pick(W, H, faces)
    old = p.get("crop")
    before, after = inside(W, H, old, faces), inside(W, H, new, faces) if new else None
    boxes = " ".join(f"[{x / W:.2f},{y / H:.2f} {w / W:.2f}x{h / H:.2f}]" for x, y, w, h in faces)
    print(f"photo {n}: {W}x{H}, {len(faces)} face(s) {boxes}; old crop {old}; new crop {new} ({why}); "
          f"faces fully in the magnet: before {before}/{len(faces)}, after {after}/{len(faces)}")
    if new and new != old:
        items[i]["photos"][j]["crop"] = new
        changed += 1
if changed and not dry:
    ref.update({"items": items, "cropsAdjustedAt": firestore.SERVER_TIMESTAMP})
    print(f"saved {changed} new crop(s) in {number}")
