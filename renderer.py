"""Small CPU triangle renderer. No OpenGL, browser, network or editor helpers.

Same sphere/cylinder geometry as the Three.js preview. Perspective-correct
z-buffering, near-plane clipping and flat Lambert shading. GPU stays free for H3.
"""
import math
from functools import lru_cache
import numpy as np
from .camera import basis, sample


@lru_cache(maxsize=4)
def geometry(subject_shape="mannequin", floor_cues="plain"):
    verts, faces, colors = [], [], []

    def mesh(v, f, color):
        offset = len(verts)
        verts.extend(v)
        faces.extend([[offset + i for i in tri] for tri in f])
        colors.extend([color] * len(f))

    def sphere(center, radius, color):
        v, f = [], []
        for j in range(13):
            p = math.pi * j / 12
            for i in range(20):
                a = 2 * math.pi * i / 20
                v.append(np.array(center) + radius * np.array([math.sin(p)*math.cos(a), math.cos(p), math.sin(p)*math.sin(a)]))
        for j in range(12):
            for i in range(20):
                a, b = j*20+i, j*20+(i+1)%20
                f.extend([[a, b, a+20], [b, b+20, a+20]])
        mesh(v, f, color)

    def bone(a, b, radius, color):
        a, b = np.array(a), np.array(b)
        axis = (b-a) / np.linalg.norm(b-a)
        side = np.cross(axis, [0, 0, 1])
        if np.linalg.norm(side) < 0.01:
            side = np.cross(axis, [1, 0, 0])
        side /= np.linalg.norm(side)
        up = np.cross(axis, side)
        v = [p + radius*(math.cos(i*math.tau/12)*side + math.sin(i*math.tau/12)*up) for p in [a,b] for i in range(12)]
        f = []
        for i in range(12):
            j = (i+1)%12
            f.extend([[i,j,i+12],[j,j+12,i+12]])
        mesh(v,f,color)
        sphere(a,radius,color)
        sphere(b,radius,color)

    body = [0.18, 0.42, 0.60]
    if subject_shape == "ball":
        sphere([0,1,0],.95,body)
    else:
        bone([0,0.92,0],[0,1.50,0],0.11,body)
        bone([-0.27,1.43,0],[0.27,1.43,0],0.075,body)
        for sign in [-1,1]:
            bone([sign*.27,1.43,0],[sign*.42,1.10,0],.055,body)
            bone([sign*.42,1.10,0],[sign*.50,.83,.08],.05,body)
            bone([sign*.12,.95,0],[sign*.19,.50,0],.075,body)
            bone([sign*.19,.50,0],[sign*.23,.10,0],.06,body)
            bone([sign*.23,.10,0],[sign*.23,.08,.18],.065,body)
        sphere([0,1.77,0],.20,[.80,.63,.43])
        sphere([0,1.77,.195],.055,[.30,.22,.17])  # nose identifies front
    # Only a plain finite floor: no grid/axis/path exists in this renderer.
    mesh([[-6,0,-6],[-6,0,6],[6,0,6],[6,0,-6]],[[0,1,2],[0,2,3]],[.72,.74,.77])
    if floor_cues == "markers":
        # Physical colored floor inlays, never editor axes, grids or text.
        for x,z,c in [(-.72,1.25,[.7,.25,.12]),(.72,1.25,[.2,.55,.3]),(-.72,-1.25,[.2,.3,.65]),(.72,-1.25,[.8,.6,.15])]:
            mesh([[x-.2,.008,z-.2],[x-.2,.008,z+.2],[x+.2,.008,z+.2],[x+.2,.008,z-.2]],[[0,1,2],[0,2,3]],c)
    return np.array(verts,np.float32), np.array(faces), np.array(colors,np.float32)


GEOMETRY = geometry()


def render_frame(k, width, height, subject_shape="mannequin", floor_cues="plain"):
    vertices, faces, colors = geometry(subject_shape, floor_cues)
    pos, right, up, forward = map(np.array, basis(k))
    view = (vertices-pos) @ np.array([right,up,forward]).T
    focal = height / (2*math.tan(math.radians(k["fov"])/2))
    rgb = np.full((height,width,3), [.91,.93,.96], np.float32)
    depth = np.full((height,width), np.inf, np.float32)
    light = np.array([.4,.8,.5]); light /= np.linalg.norm(light)
    for ids, color in zip(faces, colors):
        world = vertices[ids]
        normal = np.cross(world[1]-world[0],world[2]-world[0])
        length = np.linalg.norm(normal)
        if length < 1e-9:
            continue
        # Double-sided mesh; stable lighting independent of winding.
        shade = .55+.45*abs(float(normal @ light)/length)
        polygon = list(view[ids])
        clipped = []
        for a,b in zip(polygon,polygon[1:]+polygon[:1]):
            if a[2] >= .03:
                clipped.append(a)
            if (a[2]>=.03) != (b[2]>=.03):
                clipped.append(a+(b-a)*((.03-a[2])/(b[2]-a[2])))
        for i in range(1,len(clipped)-1):
            tri = np.array([clipped[0],clipped[i],clipped[i+1]])
            x = width/2 + focal*tri[:,0]/tri[:,2]
            y = height/2 - focal*tri[:,1]/tri[:,2]
            xmin,xmax = max(0,math.floor(min(x))),min(width-1,math.ceil(max(x)))
            ymin,ymax = max(0,math.floor(min(y))),min(height-1,math.ceil(max(y)))
            if xmin>xmax or ymin>ymax:
                continue
            den = (y[1]-y[2])*(x[0]-x[2])+(x[2]-x[1])*(y[0]-y[2])
            if abs(den)<1e-8:
                continue
            yy,xx = np.mgrid[ymin:ymax+1,xmin:xmax+1].astype(np.float32)
            xx += .5; yy += .5
            w0 = ((y[1]-y[2])*(xx-x[2])+(x[2]-x[1])*(yy-y[2]))/den
            w1 = ((y[2]-y[0])*(xx-x[2])+(x[0]-x[2])*(yy-y[2]))/den
            w2 = 1-w0-w1
            invz = w0/tri[0,2]+w1/tri[1,2]+w2/tri[2,2]
            z = 1/np.maximum(invz,1e-12)
            region = depth[ymin:ymax+1,xmin:xmax+1]
            mask = (w0>=-1e-6)&(w1>=-1e-6)&(w2>=-1e-6)&(z<region)
            region[mask] = z[mask]
            rgb[ymin:ymax+1,xmin:xmax+1][mask] = color*shade
    return rgb


def render_sequence(state, width, height, frames, fps, progress=None, subject_shape="mannequin", floor_cues="plain"):
    result = np.empty((frames,height,width,3),np.float32)
    for i in range(frames):
        result[i] = render_frame(sample(state,i/fps),width,height,subject_shape,floor_cues)
        if progress:
            progress(i+1)
    return result
