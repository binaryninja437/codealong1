"""Swap the JOWELE end-card logo for BABA JEWELLERS.

The old mark is a static, fully opaque overlay that pops on at frame 253 and holds
to the end; at frame 292 the footage hard-cuts to black behind it.  Nothing is
composited over it -- the necklace threads through the gap between the W and the E
rather than crossing any letter -- so removing it is a matter of painting out its
own footprint and laying the new logo on top.
"""
import cv2, numpy as np, os, sys

F=np.load('frames2.npy')
H,W=F.shape[1:3]
ALPHA=np.load('old_alpha.npy')                 # matte, read off the black end card
FIRST,LAST=253,322                             # frames carrying the old mark

# repaint box: wide enough to give the inpainter clean source pixels on all sides
Y0,Y1,X0,X1=520,730,60,680
MASK=cv2.dilate((ALPHA>0.01).astype(np.uint8),np.ones((5,5),np.uint8))

# ---------- new logo, placed on the old mark's footprint ----------
LOGO_W, CX, CY = 467.0, 360.0, 626.0
lg=cv2.imread('logo_crop.png',cv2.IMREAD_UNCHANGED)
lw=int(round(LOGO_W)); lh=int(round(LOGO_W*lg.shape[0]/lg.shape[1]))
_A=lg[:,:,3].astype(np.float32)/255.0
_prem=cv2.resize(lg[:,:,:3].astype(np.float32)*_A[...,None],(lw,lh),interpolation=cv2.INTER_AREA)
_a=cv2.resize(_A,(lw,lh),interpolation=cv2.INTER_AREA)
lx,ly=int(round(CX-lw/2.0)),int(round(CY-lh/2.0))
LP=np.zeros((H,W,3),np.float32); LA=np.zeros((H,W),np.float32)
LP[ly:ly+lh,lx:lx+lw]=_prem
LA[ly:ly+lh,lx:lx+lw]=_a

def render(i):
    if not (FIRST<=i<=LAST): return F[i]
    out=F[i].copy()
    out[Y0:Y1,X0:X1]=cv2.inpaint(F[i][Y0:Y1,X0:X1],MASK[Y0:Y1,X0:X1],10,cv2.INPAINT_TELEA)
    o=out.astype(np.float32)
    # grain, so the repainted skin is not a smooth patch inside grainy footage
    if F[i].mean()>20:
        g=np.random.default_rng(2000+i).normal(0.0,1.5,o.shape).astype(np.float32)
        reg=cv2.GaussianBlur(cv2.dilate((ALPHA>0.01).astype(np.uint8),
                                        np.ones((9,9),np.uint8)).astype(np.float32),(0,0),4.0)[...,None]
        o=o+g*reg
    o=LP+o*(1.0-LA[...,None])
    return np.clip(o,0,255).astype(np.uint8)

def render_all(d='out2'):
    os.makedirs(d,exist_ok=True)
    for i in range(len(F)): cv2.imwrite('%s/%05d.png'%(d,i),render(i))
    return len(F)

if __name__=='__main__':
    if sys.argv[1:2]==['preview']:
        cells=[cv2.resize(render(i),(216,384)) for i in (250,253,266,278,290,292,305,322)]
        for c,i in zip(cells,(250,253,266,278,290,292,305,322)):
            cv2.putText(c,str(i),(4,22),cv2.FONT_HERSHEY_SIMPLEX,0.65,(0,255,255),2)
        cv2.imwrite('preview2.png',np.vstack([np.hstack(cells[:4]),np.hstack(cells[4:])]))
        cv2.imwrite('zoom2a.png',cv2.resize(np.vstack([render(i)[535:720,90:640] for i in (258,274,290)]),None,fx=1.3,fy=1.3))
        print('preview written')
