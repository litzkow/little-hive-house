"""Painterly finish for a finished 600x600 design body: softly irregular, brush-like edges, a fine bristle/paper
texture and pigment grain over the ART, while every <text> stays crisp and legible on top.

    from painterly import painterly
    save(COL, slug, painterly(body, seed=3))            # default strength
    save(COL, slug, painterly(body, seed=3, edge=2.5))  # quieter edges

How it works: the body is drawn twice. The first copy (art) has all text hidden and goes through an SVG filter
(fractal-noise displacement of edges + streaky bristle texture + fine grain). The second copy (ink) hides everything
except text, unfiltered. Ids are only defined once (in the art copy) so url(#...) references keep working.
"""
import re

_FILTER = '''<filter id="{fid}" x="0" y="0" width="600" height="600" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
<feTurbulence type="fractalNoise" baseFrequency="{bf}" numOctaves="3" seed="{seed}" result="n"/>
<feDisplacementMap in="SourceGraphic" in2="n" scale="{edge}" xChannelSelector="R" yChannelSelector="G" result="d"/>
<feTurbulence type="fractalNoise" baseFrequency="0.035 0.42" numOctaves="3" seed="{seed2}" result="b"/>
<feColorMatrix in="b" type="matrix" values="0 0 0 0 0.5 0 0 0 0 0.5 0 0 0 0 0.5 0 0 0 {bristle} 0" result="bs"/>
<feComposite in="bs" in2="d" operator="in" result="bs2"/>
<feBlend in="d" in2="bs2" mode="soft-light" result="t"/>
<feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="{seed3}" result="g"/>
<feColorMatrix in="g" type="matrix" values="0 0 0 0 0.25 0 0 0 0 0.2 0 0 0 0 0.15 0 0 0 {grain} 0" result="gg"/>
<feComposite in="gg" in2="t" operator="in" result="g3"/>
<feBlend in="t" in2="g3" mode="multiply"/>
</filter>'''


def painterly(body, seed=3, edge=3.2, freq=0.05, bristle=0.55, grain=0.22, prefix="pf"):
    fid = f"{prefix}{seed}"
    filt = _FILTER.format(fid=fid, seed=seed, seed2=seed + 17, seed3=seed + 31, edge=edge, bf=freq, bristle=bristle, grain=grain)
    ink = re.sub(r'\sid="[^"]*"', "", body)          # second copy: no duplicate ids
    style = (f"<style>.{fid}a text{{visibility:hidden}}.{fid}i *{{visibility:hidden}}"
             f".{fid}i text,.{fid}i text *{{visibility:visible}}</style>")
    return (f"<defs>{filt}</defs>{style}"
            f'<g class="{fid}a" filter="url(#{fid})">{body}</g>'
            f'<g class="{fid}i" aria-hidden="true">{ink}</g>')
