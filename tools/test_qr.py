"""Checks assets/qr.js with a real QR reader (OpenCV): links of every length it accepts must read back exactly."""
import json, subprocess, sys
import numpy as np, cv2
TEXTS = ["https://littlehivehouse.com", "a", "https://g.page/r/CbX9example/review",
         "https://www.example-pizzeria.com/menu?utm_source=magnet&utm_medium=qr", "https://maps.app.goo.gl/AbCdEfGhIjKlMnOp1",
         "https://calendly.com/maria-santos-realtor/30min-consultation-for-buyers-and-sellers",
         "https://example.com/" + "x" * 120, "https://example.com/" + "y" * 190, "Café Ñandú ☕ https://exemplo.com.br/cardápio"]
js = "const Q=require('./assets/qr.js');const t=JSON.parse(process.argv[1]);console.log(JSON.stringify(t.map(s=>{const q=Q(s);return q?{v:q.version,g:q.grid}:null})))"
out = json.loads(subprocess.run(["node", "-e", js, json.dumps(TEXTS)], capture_output=True, text=True, check=True).stdout)
det = cv2.QRCodeDetector()
det2 = cv2.QRCodeDetectorAruco()   # two readers: each has the odd code it can't read, a phone reads them all
bad = 0
for t, q in zip(TEXTS, out):
    if q is None:
        print("too long:", len(t)); continue
    g = np.array(q["g"], dtype=np.uint8)
    img = np.pad((1 - g) * 255, 4, constant_values=255).repeat(10, 0).repeat(10, 1)
    val, _, _ = det.detectAndDecode(img)
    if val != t:
        val, _, _ = det2.detectAndDecode(img)
    ok = val == t
    bad += not ok
    print("v%-2d %s %r" % (q["v"], "OK " if ok else "BAD", t[:60] if ok else (t[:40], val[:40])))
too = subprocess.run(["node", "-e", "console.log(require('./assets/qr.js')('x'.repeat(214)))"], capture_output=True, text=True).stdout.strip()
print("214 chars ->", too)
sys.exit(1 if bad else 0)
