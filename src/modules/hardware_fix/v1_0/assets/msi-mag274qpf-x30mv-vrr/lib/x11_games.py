# MSI VRR Ubuntu automation, version 1.
"""Read Steam game windows from Xwayland without changing the display."""
import ctypes as c
import hashlib
from pathlib import Path
import re
import subprocess
import sys
import time
from vrr_hardware import PATCH

def window_coverage(geometry, rects, decorated=False):
    if not geometry:
        return False, False
    x, y, width, height = geometry
    on_msi = any(rx <= x < rx + rw and ry <= y < ry + rh for rx, ry, rw, rh in rects)
    covers_msi = not decorated and tuple(geometry) in {tuple(rect) for rect in rects}
    return on_msi, covers_msi

class GameWindows:
    def __init__(self):
        self.x=c.CDLL('libX11.so.6')
        self.x.XOpenDisplay.argtypes=[c.c_char_p];self.x.XOpenDisplay.restype=c.c_void_p
        self.x.XDefaultRootWindow.argtypes=[c.c_void_p];self.x.XDefaultRootWindow.restype=c.c_ulong
        self.x.XInternAtom.argtypes=[c.c_void_p,c.c_char_p,c.c_int];self.x.XInternAtom.restype=c.c_ulong
        self.x.XGetWindowProperty.argtypes=[c.c_void_p,c.c_ulong,c.c_ulong,c.c_long,c.c_long,c.c_int,c.c_ulong,c.POINTER(c.c_ulong),c.POINTER(c.c_int),c.POINTER(c.c_ulong),c.POINTER(c.c_ulong),c.POINTER(c.POINTER(c.c_ubyte))]
        self.x.XFree.argtypes=[c.c_void_p];self.x.XCloseDisplay.argtypes=[c.c_void_p]
        self.x.XGetInputFocus.argtypes=[c.c_void_p,c.POINTER(c.c_ulong),c.POINTER(c.c_int)]
        self.x.XGetGeometry.argtypes=[c.c_void_p,c.c_ulong,c.POINTER(c.c_ulong),c.POINTER(c.c_int),c.POINTER(c.c_int),c.POINTER(c.c_uint),c.POINTER(c.c_uint),c.POINTER(c.c_uint),c.POINTER(c.c_uint)]
        self.x.XTranslateCoordinates.argtypes=[c.c_void_p,c.c_ulong,c.c_ulong,c.c_int,c.c_int,c.POINTER(c.c_int),c.POINTER(c.c_int),c.POINTER(c.c_ulong)]
        # Windows can close between reading the client list and their properties.
        class Error(c.Structure):
            _fields_=[('type',c.c_int),('display',c.c_void_p),('resourceid',c.c_ulong),('serial',c.c_ulong),
                      ('error_code',c.c_ubyte),('request_code',c.c_ubyte),('minor_code',c.c_ubyte)]
        Handler=c.CFUNCTYPE(c.c_int,c.c_void_p,c.POINTER(Error))
        def on_error(display,event):
            if event.contents.error_code!=3:
                print('Xwayland-Abfragefehler:',event.contents.error_code,file=sys.stderr,flush=True)
            return 0
        self.error_handler=Handler(on_error)
        self.x.XSetErrorHandler.argtypes=[Handler];self.x.XSetErrorHandler(self.error_handler)
        self.display=self.x.XOpenDisplay(None)
        if not self.display:raise RuntimeError('Keine Xwayland-Verbindung.')
        self.root=self.x.XDefaultRootWindow(self.display)
        self.atoms={}
        self._rects=[]
        self._rects_at=-10.0
    def msi_rects(self):
        now=time.monotonic()
        if now-self._rects_at<3:
            return self._rects
        self._rects_at=now
        names=set()
        for status in Path('/sys/class/drm').glob('card*-*/status'):
            try:
                if status.read_text().strip()=='connected' and hashlib.sha256((status.parent/'edid').read_bytes()).hexdigest()==PATCH:
                    names.add(status.parent.name.split('-',1)[1])
            except OSError:
                continue
        result=subprocess.run(['xrandr','--listmonitors'],capture_output=True,text=True,timeout=3,check=True)
        rects=[]
        for line in result.stdout.splitlines():
            match=re.match(r'\s*\d+:\s+(\S+)\s+(\d+)/\d+x(\d+)/\d+([+-]\d+)([+-]\d+)\s+(.*)',line)
            if match and (match[1].lstrip('+*') in names or names.intersection(match[6].split())):
                rects.append((int(match[4]),int(match[5]),int(match[2]),int(match[3])))
        self._rects=rects
        return rects
    def geometry(self,window):
        root=c.c_ulong();x=c.c_int();y=c.c_int();width=c.c_uint();height=c.c_uint();border=c.c_uint();depth=c.c_uint()
        if not self.x.XGetGeometry(self.display,window,c.byref(root),c.byref(x),c.byref(y),c.byref(width),c.byref(height),c.byref(border),c.byref(depth)):
            return None
        child=c.c_ulong()
        if not self.x.XTranslateCoordinates(self.display,window,self.root,0,0,c.byref(x),c.byref(y),c.byref(child)):
            return None
        return [x.value,y.value,width.value,height.value]
    def prop(self,window,name):
        if name not in self.atoms:
            self.atoms[name]=self.x.XInternAtom(self.display,name.encode(),0)
        atom=self.atoms[name]
        typ=c.c_ulong();fmt=c.c_int();count=c.c_ulong();after=c.c_ulong();data=c.POINTER(c.c_ubyte)()
        result=self.x.XGetWindowProperty(self.display,window,atom,0,65536,0,0,c.byref(typ),c.byref(fmt),c.byref(count),c.byref(after),c.byref(data))
        if result or not data:return None
        try:
            if fmt.value==32:return list(c.cast(data,c.POINTER(c.c_ulong))[:count.value])
            if fmt.value==8:return c.string_at(data,count.value)
            return None
        finally:self.x.XFree(data)
    def games(self):
        result=[]
        rects=self.msi_rects()
        for window in self.prop(self.root,'_NET_CLIENT_LIST') or []:
            klass=self.prop(window,'WM_CLASS') or b''
            match=re.search(rb'(?:^|\x00)steam_app_([1-9][0-9]*)(?:\x00|$)',klass,re.I)
            if match:
                states=self.prop(window,'_NET_WM_STATE') or []
                title=self.prop(window,'_NET_WM_NAME') or self.prop(window,'WM_NAME') or b''
                # Wine's explorer creates a nameless tray helper carrying the
                # same Steam class. It remains after the real game exits.
                def atom(name):
                    if name not in self.atoms:
                        self.atoms[name]=self.x.XInternAtom(self.display,name.encode(),0)
                    return self.atoms[name]
                if (not title and atom('_NET_WM_STATE_SKIP_TASKBAR') in states
                        and atom('_NET_WM_STATE_SKIP_PAGER') in states
                        and atom('_NET_WM_STATE_FULLSCREEN') not in states):
                    continue
                pid=self.prop(window,'_NET_WM_PID') or []
                geometry=self.geometry(window)
                extents=(self.prop(window,'_NET_FRAME_EXTENTS') or [])+(self.prop(window,'_GTK_FRAME_EXTENTS') or [])
                on_msi,covers_msi=window_coverage(geometry,rects,any(extents))
                result.append({'window':window,'appid':match.group(1).decode(),'pid':pid[0] if pid else None,
                               'fullscreen':atom('_NET_WM_STATE_FULLSCREEN') in states,
                               'geometry':geometry,'on_msi':on_msi,'covers_msi':covers_msi})
        return result
    def close(self):
        if self.display:self.x.XCloseDisplay(self.display);self.display=None
    def focused(self):
        window=c.c_ulong();revert=c.c_int()
        self.x.XGetInputFocus(self.display,c.byref(window),c.byref(revert))
        return window.value

if __name__=='__main__':
    detector=GameWindows()
    try:print(detector.games())
    finally:detector.close()
