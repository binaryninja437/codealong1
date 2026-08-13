"""Re-brand the jewellery box lid: swap the STROILI mark for the BABA JEWELLERS logo.

The shot is locked off and the lid never moves while it is seated, so the logo is
placed once in image space.  Two things still have to be respected per frame:
the finger that passes over the lid, and the soft shadow it casts across it.
"""
import cv2, numpy as np, sys

UP='/root/.claude/uploads/2085b69e-20e9-5d77-ad3e-6926823d9c4e'
F=np.load('frames.npy')
H,W=F.shape[1:3]
REF=F[0].astype(np.float32)

SEATED=set(range(0,21))|set(range(219,270))     # frames where the lid is on the box

MARK=dict(x0=301,x1=411,y0=522,y1=590)          # existing STROILI mark, measured
LOGO_W, CX, CY = 244.0, 357.0, 557.0            # new logo: width and centre on the lid

RX0,RX1,RY0,RY1 = 200,520,490,640               # work region (entirely on the lid face)
OX0,OX1,OY0,OY1 = 190,530,470,745               # finger probe region (reaches lid edge)

# ---------- logo layer (static) ----------
lg=cv2.imread('logo_crop.png',cv2.IMREAD_UNCHANGED)
lw=int(round(LOGO_W)); lh=int(round(LOGO_W*lg.shape[0]/lg.shape[1]))
lg=cv2.resize(lg,(lw,lh),interpolation=cv2.INTER_AREA)
lx,ly=int(round(CX-lw/2.0)),int(round(CY-lh/2.0))
logo_rgb=np.zeros((H,W,3),np.float32); logo_a=np.zeros((H,W),np.float32)
logo_rgb[ly:ly+lh,lx:lx+lw]=lg[:,:,:3]
logo_a[ly:ly+lh,lx:lx+lw]=lg[:,:,3]/255.0
logo_rgb=cv2.GaussianBlur(logo_rgb,(0,0),0.55)  # match the lens softness of the plate
logo_a=cv2.GaussianBlur(logo_a,(0,0),0.55)

# ---------- clean lid plate: frame 0 with the STROILI mark painted out ----------
g0=cv2.cvtColor(F[0],cv2.COLOR_BGR2GRAY).astype(np.float32)
_y,_x=slice(MARK['y0']-25,MARK['y1']+25),slice(MARK['x0']-25,MARK['x1']+25)
sub=g0[_y,_x]
mk=((cv2.medianBlur(sub.astype(np.uint8),31).astype(np.float32)-sub)>4).astype(np.uint8)
mk=cv2.dilate(mk,np.ones((5,5),np.uint8),iterations=2)
mark_mask=np.zeros((H,W),np.uint8); mark_mask[_y,_x]=mk
PLATE=cv2.inpaint(F[0],mark_mask,7,cv2.INPAINT_TELEA).astype(np.float32)

# feathered work-region mask: only where the old mark or the new ink actually lands
_reg=((logo_a>0.02)|(mark_mask>0)).astype(np.uint8)
_reg=cv2.dilate(_reg,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(11,11)))
REG=cv2.GaussianBlur(_reg.astype(np.float32),(0,0),3.0)[...,None]

def finger_alpha(f):
    """Soft coverage of skin/nail over the lid.

    Chromaticity c = (B-G)/R, measured as a change from frame 0 so the printed
    mark (present in both) cancels out.  Shadow only nudges c by about +0.025;
    skin swings it to -0.07 and the burgundy nail to +0.13, so the two sides of
    the ramp catch the finger and leave the cast shadow alone.  Ramping instead
    of thresholding gives an edge that follows the real defocus.
    """
    a=f[OY0:OY1,OX0:OX1].astype(np.float32)+1.0
    dc=(a[:,:,0]-a[:,:,1])/a[:,:,2]-CREF
    al=np.maximum(np.clip((-dc-0.020)/0.030,0,1),np.clip((dc-0.055)/0.045,0,1))
    core=(al>0.5).astype(np.uint8)
    core=cv2.morphologyEx(core,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
    core=cv2.morphologyEx(core,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(21,21)))
    n,lab,stats,_=cv2.connectedComponentsWithStats(core,8)
    keep=np.zeros_like(core)
    for i in range(1,n):
        if stats[i,4]>=250 and stats[i,1]+stats[i,3]>=core.shape[0]-3:
            keep[lab==i]=1
    if not keep.any():
        return np.zeros((H,W),np.float32)
    gate=np.clip(cv2.GaussianBlur(cv2.dilate(keep,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(21,21))).astype(np.float32),(0,0),4.0),0,1)
    al=cv2.GaussianBlur(np.maximum(al,keep.astype(np.float32))*gate,(0,0),1.2)
    soft=np.zeros((H,W),np.float32); soft[OY0:OY1,OX0:OX1]=np.clip(al,0,1)
    return soft

_r=REF[OY0:OY1,OX0:OX1]+1.0
CREF=(_r[:,:,0]-_r[:,:,1])/_r[:,:,2]

def shading(f,occ):
    """Per-channel light ratio vs frame 0, so the cast shadow keeps its colour."""
    valid=(1.0-np.clip(occ*3.0,0,1))[...,None]
    num=cv2.GaussianBlur(f.astype(np.float32)*valid,(0,0),9.0)
    den=cv2.GaussianBlur(REF*valid,(0,0),9.0)
    s=num/np.maximum(den,1e-3)
    return np.clip(cv2.GaussianBlur(s,(0,0),4.0),0.15,1.25)

def render(i):
    f=F[i].astype(np.float32)
    if i not in SEATED: return F[i]
    occ=finger_alpha(F[i])
    sh=shading(F[i],occ)
    clean=PLATE*sh                       # lid, unbranded, lit like this frame
    a=logo_a[...,None]
    branded=logo_rgb*sh*a+clean*(1-a)    # ink takes the same light as the card
    # match the footage grain so the rebuilt patch is not a frozen still
    g=np.random.default_rng(1000+i).normal(0.0,1.6,branded.shape).astype(np.float32)
    out=(branded+g)*REG+f*(1-REG)
    o=occ[...,None]
    out=f*o+out*(1-o)                    # the real finger goes back on top
    return np.clip(out,0,255).astype(np.uint8)

if __name__=='__main__':
    if sys.argv[1:2]==['preview']:
        idx=[0,10,15,18,20,219,221,224,240,269]
        cells=[]
        for i in idx:
            c=cv2.resize(render(i)[380:760,170:550],(300,300))
            cv2.putText(c,str(i),(5,28),cv2.FONT_HERSHEY_SIMPLEX,0.9,(0,255,255),2); cells.append(c)
        cv2.imwrite('preview.png',np.vstack([np.hstack(cells[j:j+5]) for j in (0,5)]))
        zoom=[np.hstack([F[i][495:625,215:505],render(i)[495:625,215:505]]) for i in (18,20,219,221)]
        cv2.imwrite('zoom.png',cv2.resize(np.vstack(zoom),None,fx=2.0,fy=2.0,interpolation=cv2.INTER_NEAREST))
        print('preview written')

def render_all(out_path='out_frames'):
    import os
    os.makedirs(out_path,exist_ok=True)
    for i in range(len(F)):
        cv2.imwrite('%s/%05d.png'%(out_path,i), render(i))
    return len(F)
