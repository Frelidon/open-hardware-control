#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Five original periodic cinematic studies. Offline rendering; no external assets."""
import json
import math
from pathlib import Path
import subprocess
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1] / 'src/assets/app-backgrounds'
WIDTH, HEIGHT, FPS, SECONDS = 1280, 720, 24, 12
Y, X = np.mgrid[-1:1:complex(HEIGHT), -1.777:1.777:complex(WIDTH)].astype(np.float32)
STUDIES = ('aurora-silk', 'nebula-depth', 'liquid-prism', 'ocean-caustics', 'solar-orbit')


def render(study, phase):
    t = math.tau * (phase % 1.)
    rgb = np.zeros((HEIGHT, WIDTH, 3), np.float32)
    if study == 'aurora-silk':
        for i, color in enumerate(((.1, .95, .65), (.13, .45, 1), (.7, .14, .95))):
            ridge = Y - .16 * i - .25 * np.sin(X*1.7 + t + i) - .10*np.sin(X*4 - t*2+i)
            silk = np.exp(-abs(ridge)*5) * (.2 + .8*np.sin(X*10+np.sin(Y*4+t)+t+i)**2)
            rgb += silk[:, :, None] * np.array(color) * 80
    elif study == 'nebula-depth':
        radius = np.sqrt((X+.2*np.cos(t))**2+(Y-.15*np.sin(t))**2)
        angle = np.arctan2(Y, X)
        clouds = np.zeros_like(X)
        for i in range(1, 5):
            clouds += (np.sin(X*(i*2)+np.cos(Y*3+t+i)+t)*np.cos(Y*(i*3)-np.sin(X+t+i)))/(i*2)
        density = np.exp(-((radius-.6-.12*np.sin(angle*3+t))/.65)**2)*np.maximum(0, .5+clouds)
        rgb[:, :, 0] = density*(60+45*np.cos(t+X))
        rgb[:, :, 1] = density*40
        rgb[:, :, 2] = density*140
        stars = np.maximum(0, np.cos(X*127.7+Y*311.3)*np.sin(Y*173.1-X*269.5)-.997)**2 * 900000
        rgb += stars[:, :, None] * (.65+.35*math.cos(t))
    elif study == 'liquid-prism':
        surface = np.sin(X*2+t)*np.cos(Y*3-t)+.3*np.sin(X*5+Y*4+t*2)
        dx = 2*np.cos(X*2+t)*np.cos(Y*3-t)+1.5*np.cos(X*5+Y*4+t*2)
        dy = -3*np.sin(X*2+t)*np.sin(Y*3-t)+1.2*np.cos(X*5+Y*4+t*2)
        specular = np.maximum(0, (dx*.35-dy*.5+1.4)/np.sqrt(dx*dx+dy*dy+1))**12
        for c in range(3):
            rgb[:, :, c] = (17+30*np.sin(surface*2+c*2+t*.0)**2)+specular*(60+35*c)
    elif study == 'ocean-caustics':
        caustic = np.zeros_like(X)
        for i in range(3):
            wave = np.sin(X*(3+i)+np.cos(Y*(4-i)+t+i)+t)*np.cos(Y*(3+i)-t+i)
            caustic += np.exp(-abs(wave)*32)
        depth = np.exp(-((X*.38)**2+(Y+.7)**2)*.7)
        rgb[:, :, 0] = 3 + caustic*8
        rgb[:, :, 1] = 12 + depth*28+caustic*30
        rgb[:, :, 2] = 28 + depth*48+caustic*36
    elif study == 'solar-orbit':
        x, y = X-.45*np.cos(t), Y-.17*np.sin(t)
        r = np.sqrt(x*x+(y*1.2)**2)
        halo = np.exp(-((r-.47)/.14)**2)
        angle = np.arctan2(y, x)
        ribbons = halo*(.62+.38*np.sin(angle*8+t*2+np.sin(r*16))**2)
        core = np.exp(-((r-.46)/.018)**2)
        rgb[:, :, 0] = ribbons*150+core*80
        rgb[:, :, 1] = ribbons*44+core*100
        rgb[:, :, 2] = ribbons*12+core*40
    else:
        raise ValueError(study)
    vignette = np.clip(1-.22*(X*.56)**2-.2*Y**2, .3, 1)
    rgb = rgb * vignette[:, :, None] + np.array([3, 5, 11])
    return np.clip(rgb, 0, 255).astype(np.uint8)


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    report = {}
    for study in STUDIES:
        destination = ROOT / f'{study}.mp4'
        first = render(study, 0)
        assert np.array_equal(first, render(study, 1))
        process = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo',
            '-pix_fmt', 'rgb24', '-s', f'{WIDTH}x{HEIGHT}', '-r', str(FPS), '-i', '-',
            '-an', '-c:v', 'libx264', '-threads', '2', '-preset', 'fast', '-crf', '18',
            '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(destination)], stdin=subprocess.PIPE)
        differences=[]; previous=first
        try:
            for i in range(FPS*SECONDS):
                frame = render(study, i/(FPS*SECONDS))
                if i: differences.append(float(np.abs(frame.astype(float)-previous).mean()))
                process.stdin.write(frame.tobytes()); previous=frame
                if i == FPS*3: Image.fromarray(frame).save(destination.with_suffix('.jpg'), quality=94)
        finally:
            process.stdin.close()
        if process.wait(): raise RuntimeError('encoder failed')
        seam=float(np.abs(first.astype(float)-previous).mean())
        assert seam <= max(differences)*1.2
        report[study] = dict(seam=seam, max_adjacent=max(differences), exact_periodicity=True,
                             size=[WIDTH,HEIGHT],fps=FPS,seconds=SECONDS)
        print(study, report[study], flush=True)
    (ROOT/'render-evidence.json').write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__': main()
