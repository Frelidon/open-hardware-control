# MSI VRR Ubuntu automation, version 1.
"""Read the MSI's DRM VRR property without taking display ownership."""
import ctypes as c
import hashlib
import os
from pathlib import Path

PATCH='2066c56832b221da3169be8173875e3bcb2dab4fb1c3eb99f1382b803920116e'
class Props(c.Structure):
    _fields_=[('count',c.c_uint32),('ids',c.POINTER(c.c_uint32)),('values',c.POINTER(c.c_uint64))]
class Prop(c.Structure):
    _fields_=[('id',c.c_uint32),('flags',c.c_uint32),('name',c.c_char*32)]
class MSIVRR:
    def __init__(self):
        self.lib=c.CDLL('libdrm.so.2')
        self.lib.drmModeObjectGetProperties.argtypes=[c.c_int,c.c_uint32,c.c_uint32];self.lib.drmModeObjectGetProperties.restype=c.POINTER(Props)
        self.lib.drmModeGetProperty.argtypes=[c.c_int,c.c_uint32];self.lib.drmModeGetProperty.restype=c.POINTER(Prop)
        self.lib.drmModeFreeObjectProperties.argtypes=[c.POINTER(Props)];self.lib.drmModeFreeProperty.argtypes=[c.POINTER(Prop)]
        self.lib.drmSetClientCap.argtypes=[c.c_int,c.c_uint64,c.c_uint64]
    def props(self,fd,object_id,type_id):
        result={};p=self.lib.drmModeObjectGetProperties(fd,object_id,type_id)
        if not p:return result
        try:
            for i in range(p.contents.count):
                prop=self.lib.drmModeGetProperty(fd,p.contents.ids[i])
                if prop:
                    result[prop.contents.name.decode()]=p.contents.values[i];self.lib.drmModeFreeProperty(prop)
        finally:self.lib.drmModeFreeObjectProperties(p)
        return result
    def value(self):
        for status in Path('/sys/class/drm').glob('card*-*/status'):
            try:
                if status.read_text().strip()!='connected':continue
                connector=status.parent
                if hashlib.sha256((connector/'edid').read_bytes()).hexdigest()!=PATCH:continue
                fd=os.open('/dev/dri/'+connector.name.split('-',1)[0],os.O_RDONLY)
                try:
                    self.lib.drmSetClientCap(fd,3,1)
                    props=self.props(fd,int((connector/'connector_id').read_text()),0xc0c0c0c0)
                    crtc=props.get('CRTC_ID',0)
                    return self.props(fd,crtc,0xcccccccc).get('VRR_ENABLED') if crtc else None
                finally:os.close(fd)
            except (FileNotFoundError,PermissionError,OSError):continue
        return None
