#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Generate the eight original bundled Open Hardware Control LCD themes.

The artwork is fully procedural and contains no third-party media.  Keeping the
recipe in the source tree makes the bundled GIFs reproducible and editable.
"""
from __future__ import annotations

import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "lcd-designs"
SIZE = 240
FPS = 20
FRAMES = 40
DURATION = round(1000 / FPS)

THEMES = (
    ("nebula-vanguard", "Nebula Vanguard"),
    ("ringworld-runner", "Ringworld Runner"),
    ("singularity-dive", "Singularity Dive"),
    ("abyssal-bloom", "Abyssal Bloom"),
    ("neon-rain", "Neon Rain"),
    ("magma-heart", "Magma Heart"),
    ("polar-aurora", "Polar Aurora"),
    ("firefly-grove", "Firefly Grove"),
)


def clamp(v: float) -> int:
    return max(0, min(255, round(v)))


def gradient(top, bottom) -> Image.Image:
    img = Image.new("RGB", (SIZE, SIZE))
    p = img.load()
    for y in range(SIZE):
        t = y / max(1, SIZE - 1)
        c = tuple(clamp(a + (b - a) * t) for a, b in zip(top, bottom))
        for x in range(SIZE):
            p[x, y] = c
    return img


def stars(img: Image.Image, seed: int, phase: float, count: int = 78) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(seed)
    for i in range(count):
        x = rng.randrange(SIZE)
        y = rng.randrange(SIZE)
        r = 0.5 + rng.random() * 1.4
        a = 85 + int(150 * (0.5 + 0.5 * math.sin(phase * math.tau + i * 1.73)))
        draw.ellipse((x-r, y-r, x+r, y+r), fill=(220, 235, 255, a))


def glow_layer(size=SIZE) -> Image.Image:
    return Image.new("RGBA", (size, size), (0, 0, 0, 0))


def nebula_vanguard(phase: float) -> Image.Image:
    img = gradient((5, 3, 20), (19, 2, 38)).convert("RGBA")
    stars(img, 101, phase, 95)
    gl = glow_layer(); d = ImageDraw.Draw(gl, "RGBA")
    for i, (cx, cy, col) in enumerate(((70, 95, (118, 46, 255)), (155, 132, (10, 205, 255)), (120, 65, (255, 40, 164)))):
        wob = math.sin(phase*math.tau + i*2.1) * 9
        d.ellipse((cx-62+wob, cy-35, cx+62+wob, cy+35), fill=(*col, 80))
    gl = gl.filter(ImageFilter.GaussianBlur(26)); img.alpha_composite(gl)
    draw = ImageDraw.Draw(img, "RGBA")
    sx = 88 + 26 * math.sin(phase * math.tau)
    sy = 135 + 8 * math.cos(phase * math.tau)
    draw.polygon([(sx,sy-10),(sx+43,sy),(sx,sy+10),(sx+10,sy)], fill=(210,225,250,235))
    draw.polygon([(sx-5,sy),(sx-30,sy-4),(sx-30,sy+4)], fill=(50,205,255,160))
    return img.convert("RGB")


def ringworld_runner(phase: float) -> Image.Image:
    img = gradient((3, 8, 25), (17, 10, 28)).convert("RGBA"); stars(img, 202, phase, 78)
    draw = ImageDraw.Draw(img, "RGBA")
    angle = phase * 28
    for width, alpha, offs in ((10, 190, 0), (3, 230, 8)):
        draw.arc((18,55,222,190), 200+angle+offs, 520+angle+offs, fill=(255,188,70,alpha), width=width)
    draw.ellipse((68,75,174,182), outline=(76,100,160,110), width=2)
    a = phase * math.tau
    sx = 120 + math.cos(a) * 78; sy = 120 + math.sin(a) * 42
    draw.polygon([(sx-13,sy-5),(sx+13,sy),(sx-13,sy+5),(sx-6,sy)], fill=(235,244,255,240))
    draw.line((sx-20,sy,sx-36,sy), fill=(65,205,255,190), width=3)
    return img.convert("RGB")


def singularity_dive(phase: float) -> Image.Image:
    img = gradient((2, 3, 15), (5, 0, 12)).convert("RGBA"); stars(img, 303, phase, 82)
    gl = glow_layer(); d = ImageDraw.Draw(gl,"RGBA")
    cx, cy = 120, 120
    for r in range(86, 23, -3):
        t=(86-r)/63
        col=(40+int(90*t),70+int(80*t),255)
        d.arc((cx-r,cy-r*0.55,cx+r,cy+r*0.55), phase*360+r*1.7, phase*360+r*1.7+235, fill=(*col,125), width=3)
    gl=gl.filter(ImageFilter.GaussianBlur(4)); img.alpha_composite(gl)
    draw=ImageDraw.Draw(img,"RGBA")
    draw.ellipse((83,83,157,157), fill=(0,0,2,255), outline=(70,105,255,180), width=3)
    draw.ellipse((104,104,136,136), fill=(0,0,0,255))
    return img.convert("RGB")


def abyssal_bloom(phase: float) -> Image.Image:
    img = gradient((0, 5, 18), (0, 28, 48)).convert("RGBA")
    draw=ImageDraw.Draw(img,"RGBA")
    for i in range(34):
        rng=random.Random(404+i)
        x=rng.randrange(SIZE); y=(rng.randrange(SIZE)+phase*70*(0.4+rng.random()))%SIZE
        draw.ellipse((x-1,y-1,x+1,y+1),fill=(70,215,255,90))
    cx=120+math.sin(phase*math.tau)*12; cy=92+math.cos(phase*math.tau)*5
    gl=glow_layer(); gd=ImageDraw.Draw(gl,"RGBA")
    gd.ellipse((cx-55,cy-34,cx+55,cy+34),fill=(90,220,255,105)); gl=gl.filter(ImageFilter.GaussianBlur(20)); img.alpha_composite(gl)
    draw=ImageDraw.Draw(img,"RGBA")
    draw.ellipse((cx-48,cy-28,cx+48,cy+30),fill=(30,175,225,125),outline=(160,245,255,210),width=3)
    for i in range(9):
        x=cx-38+i*9.5
        pts=[]
        for j in range(18):
            y=cy+28+j*5.6; xx=x+math.sin(j*.55+phase*math.tau+i)*6
            pts.append((xx,y))
        draw.line(pts,fill=(100,225,255,155),width=2)
    return img.convert("RGB")


def neon_rain(phase: float) -> Image.Image:
    img=gradient((7,3,22),(20,2,32)).convert("RGBA"); draw=ImageDraw.Draw(img,"RGBA")
    rng=random.Random(505)
    x=0
    while x<SIZE:
        w=rng.randint(13,26); h=rng.randint(42,126); y=SIZE-h
        col=(15+rng.randrange(30),8,36+rng.randrange(25),255)
        draw.rectangle((x,y,x+w,SIZE),fill=col)
        for wy in range(y+8,SIZE-8,11):
            for wx in range(x+5,x+w-3,8):
                if rng.random()<.55: draw.rectangle((wx,wy,wx+2,wy+4),fill=(255 if rng.random()<.45 else 45,45 if rng.random()<.45 else 210,220,160))
        x+=w+3
    offset=int(phase*24)%24
    for i in range(44):
        rx=(i*37)%SIZE; ry=((i*53+offset*8)%300)-40
        draw.line((rx,ry,rx-8,ry+25),fill=(70,185,255,130),width=1)
    draw.line((0,205,SIZE,205),fill=(255,25,180,180),width=2)
    return img.convert("RGB")


def magma_heart(phase: float) -> Image.Image:
    img=gradient((10,2,1),(45,5,0)).convert("RGBA"); draw=ImageDraw.Draw(img,"RGBA")
    pulse=1+.10*math.sin(phase*math.tau)
    gl=glow_layer(); gd=ImageDraw.Draw(gl,"RGBA")
    cx,cy=120,118; r=62*pulse
    gd.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(255,66,5,110)); gl=gl.filter(ImageFilter.GaussianBlur(22)); img.alpha_composite(gl)
    draw=ImageDraw.Draw(img,"RGBA")
    points=[]
    for i in range(48):
        a=i/48*math.tau; rr=(54+8*math.sin(a*5+phase*math.tau))*pulse
        points.append((cx+math.cos(a)*rr,cy+math.sin(a)*rr))
    draw.polygon(points,fill=(100,16,2,255),outline=(255,95,18,235))
    rng=random.Random(606)
    for i in range(18):
        a=rng.random()*math.tau; length=18+rng.random()*32
        x1=cx+math.cos(a)*14; y1=cy+math.sin(a)*14
        x2=cx+math.cos(a)*length; y2=cy+math.sin(a)*length
        draw.line((x1,y1,x2,y2),fill=(255,160+rng.randrange(80),20,210),width=2)
    return img.convert("RGB")


def polar_aurora(phase: float) -> Image.Image:
    img=gradient((1,9,28),(2,32,45)).convert("RGBA"); stars(img,707,phase,62)
    gl=glow_layer(); d=ImageDraw.Draw(gl,"RGBA")
    for band,col,off in ((0,(50,255,175),0),(1,(45,160,255),2.0),(2,(170,80,255),4.2)):
        pts=[]
        for x in range(-20,261,5):
            y=58+band*17+18*math.sin(x/42+phase*math.tau+off)
            pts.append((x,y))
        d.line(pts,fill=(*col,120),width=12)
    gl=gl.filter(ImageFilter.GaussianBlur(10)); img.alpha_composite(gl)
    draw=ImageDraw.Draw(img,"RGBA")
    draw.polygon([(0,190),(42,155),(76,184),(111,142),(151,185),(198,154),(240,183),(240,240),(0,240)],fill=(180,214,225,245))
    draw.polygon([(0,212),(55,185),(104,207),(152,178),(211,207),(240,192),(240,240),(0,240)],fill=(70,118,142,245))
    return img.convert("RGB")


def firefly_grove(phase: float) -> Image.Image:
    img=gradient((3,13,18),(3,31,24)).convert("RGBA"); draw=ImageDraw.Draw(img,"RGBA")
    for x in (18,43,72,180,207,230):
        draw.rectangle((x,70,x+9,220),fill=(7,24,18,255))
        draw.ellipse((x-22,45,x+32,104),fill=(10,48,31,220))
    draw.ellipse((38,170,207,242),fill=(3,62,68,255),outline=(35,155,150,120),width=2)
    gl=glow_layer(); gd=ImageDraw.Draw(gl,"RGBA")
    rng=random.Random(808)
    for i in range(34):
        base_x=rng.randrange(24,220); base_y=rng.randrange(64,204)
        x=base_x+math.sin(phase*math.tau*(.7+rng.random())+i)*10
        y=base_y+math.cos(phase*math.tau*(.5+rng.random())+i*.8)*7
        a=110+int(120*(.5+.5*math.sin(phase*math.tau+i)))
        gd.ellipse((x-3,y-3,x+3,y+3),fill=(210,255,94,a))
    gl=gl.filter(ImageFilter.GaussianBlur(5)); img.alpha_composite(gl)
    draw=ImageDraw.Draw(img,"RGBA")
    for i in range(22):
        rng=random.Random(900+i); x=rng.randrange(25,215)+math.sin(phase*math.tau+i)*8; y=rng.randrange(60,200)+math.cos(phase*math.tau+i*.7)*5
        draw.ellipse((x-1.2,y-1.2,x+1.2,y+1.2),fill=(238,255,138,235))
    return img.convert("RGB")


RENDERERS={
    "nebula-vanguard":nebula_vanguard,
    "ringworld-runner":ringworld_runner,
    "singularity-dive":singularity_dive,
    "abyssal-bloom":abyssal_bloom,
    "neon-rain":neon_rain,
    "magma-heart":magma_heart,
    "polar-aurora":polar_aurora,
    "firefly-grove":firefly_grove,
}


def generate() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest=[]
    for slug,title in THEMES:
        frames=[RENDERERS[slug](i/FRAMES) for i in range(FRAMES)]
        path=OUT/f"{slug}.gif"
        frames[0].save(path,format="GIF",save_all=True,append_images=frames[1:],duration=DURATION,loop=0,disposal=2,optimize=True)
        frames[0].resize((320,320),Image.Resampling.LANCZOS).save(OUT/f"{slug}-preview-320.png",optimize=True)
        frames[0].resize((640,640),Image.Resampling.LANCZOS).save(OUT/f"{slug}-source-640.png",optimize=True)
        manifest.append({"id":slug,"name":title,"gif":path.name,"preview":f"{slug}-preview-320.png","source":f"{slug}-source-640.png","fps":FPS,"size":"240x240"})
    import json
    (OUT/"manifest.json").write_text(json.dumps({"schema":1,"license":"GPL-3.0-or-later","third_party_media":False,"themes":manifest},indent=2)+"\n",encoding="utf-8")
    (OUT/"README.md").write_text(
        "# Bundled LCD themes\n\nThese eight themes are original procedural Open Hardware Control artwork. "
        "No third-party images, logos, characters, brands or stock media are embedded. "
        "The generator is retained in `tools/generate_builtin_lcd_gifs.py`.\n",
        encoding="utf-8",
    )

if __name__ == "__main__":
    generate()
