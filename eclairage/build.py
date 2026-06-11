#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generateur de livrables - Plan d'eclairage RDC Module 4
Modele unique (cotes reelles 9600 x 9100 mm) -> exporte :
  - plan_eclairage_2D.png  (vue de dessus, implantation luminaires)
  - model.obj / model.mtl  (3D)
  - model.dae              (Collada, importable SketchUp)
  - Plan_eclairage_RDC_Module4.pdf  (livrable)
"""
import os, math, datetime

OUT = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------------
# 1) MODELE  (metres, origine coin Nord-Ouest ; x -> Est, z -> Sud)
# ----------------------------------------------------------------------------
EXT_W, EXT_D = 9.60, 9.10           # emprise exterieure
WALL = 0.30                          # mur ext 305 mm
H    = 2.60                          # hauteur sous plafond

# Pieces : nom, x0, z0, x1, z1, surface affichee, couleur (R,G,B)
ROOMS = [
    ("Coin Bureau",            0.30, 0.30, 3.30, 3.09, "8,90 m²", (0.72,0.83,0.77)),
    ("Salle détente & jeux",   0.30, 3.09, 3.30, 8.80, "15,41 m²",(0.79,0.76,0.88)),
    ("Buanderie",              3.30, 0.30, 5.30, 2.67, "5,07 m²", (0.84,0.80,0.71)),
    ("WC",                     3.30, 2.67, 4.40, 3.94, "",           (0.84,0.80,0.71)),
    ("Escalier",               3.30, 3.94, 5.30, 6.90, "",           (0.80,0.71,0.62)),
    ("Entrée",                 3.30, 6.90, 5.30, 8.80, "5,5 m²",  (0.78,0.82,0.86)),
    ("Coin Cuisine",           5.30, 0.30, 9.30, 3.00, "~9 m²",   (0.88,0.78,0.74)),
    ("Coin Repas",             5.30, 3.00, 9.30, 5.10, "7 m²",    (0.91,0.81,0.65)),
    ("Salon",                  5.30, 5.10, 9.30, 8.80, "10,3 m²", (0.74,0.81,0.88)),
]

# Luminaires : type, x, z, [options]
#  spot=encastre / susp=suspension / plaf=plafonnier / app=appoint / cove=ruban LED corniche
F_SPOT, F_SUSP, F_PLAF, F_APP, F_COVE = "spot", "susp", "plaf", "app", "cove"
FIX = []
COVES = []  # rubans LED peripheriques : (x0,z0,x1,z1, nom)
def grid(x0,z0,x1,z1,nx,nz,typ,**o):
    for i in range(nx):
        for j in range(nz):
            x = x0 + (x1-x0)*(i+0.5)/nx
            z = z0 + (z1-z0)*(j+0.5)/nz
            FIX.append((typ,round(x,2),round(z,2),o))

# ================= PROPOSITION 2 - TOUT INDIRECT / AMBIANCE =================
# Principe : rubans LED en corniche peripherique partout, lampadaires indirects,
# suspensions deco ; les encastres sont reduits aux seules taches & securite.

# --- Rubans LED corniche (uplight peripherique) ---
def cove(room_name, inset=0.18):
    for (nm,x0,z0,x1,z1,area,col) in ROOMS:
        if nm==room_name:
            COVES.append((x0+inset,z0+inset,x1-inset,z1-inset,nm)); return
for r in ["Coin Bureau","Salle détente & jeux","Coin Cuisine","Coin Repas","Salon","Entrée"]:
    cove(r)

# --- Taches fonctionnelles (spots reduits au strict necessaire) ---
# Bureau : 2 spots directionnels au-dessus du poste + lampe
FIX += [(F_SPOT,1.0,1.0,{}),(F_SPOT,2.2,1.0,{})]
FIX.append((F_APP,0.7,0.7,{"h":1.05,"label":"lampe bureau"}))
# Cuisine : 3 spots au bord du plan de travail + 2 suspensions ilot + reglette LED
FIX += [(F_SPOT,6.0,0.8,{}),(F_SPOT,7.3,0.8,{}),(F_SPOT,8.6,0.8,{})]
FIX += [(F_SUSP,6.6,1.7,{"drop":0.95}),(F_SUSP,7.5,1.7,{"drop":0.95})]
FIX.append((F_APP,8.6,0.55,{"h":2.0,"label":"réglette LED sous meuble"}))
# Repas : grappe deco de 3 suspensions (coeur d'ambiance)
FIX += [(F_SUSP,7.2,4.05,{"drop":0.8}),(F_SUSP,7.5,4.2,{"drop":0.65}),(F_SUSP,7.35,3.85,{"drop":0.95})]
# Escalier : balisage + spots securite (toujours conserves)
for j in range(4):
    FIX.append((F_SPOT,4.10,4.3+j*0.7,{"int":0.6}))
# Buanderie / WC : plafonnier fonctionnel (pieces techniques)
FIX += [(F_PLAF,4.30,1.45,{}),(F_PLAF,3.85,3.30,{})]

# --- Appoints d'ambiance (lampadaires indirects / appliques) ---
FIX += [(F_APP,0.7,4.4,{"h":1.55,"label":"lampadaire indirect"}),
        (F_APP,0.7,8.2,{"h":1.55,"label":"lampadaire indirect"}),   # Salle detente x2
        (F_APP,9.0,8.3,{"h":1.6,"label":"lampadaire arc"}),          # Salon
        (F_APP,5.6,6.2,{"h":1.5,"label":"applique murale"}),         # Salon
        (F_APP,8.9,3.2,{"h":1.5,"label":"applique murale"})]         # Repas/Salon

FIX_COL = {F_SPOT:(1.0,0.82,0.30), F_SUSP:(1.0,0.49,0.20),
           F_PLAF:(0.55,0.78,1.0), F_APP:(0.30,0.85,0.55), F_COVE:(0.78,0.49,1.0)}
FIX_LABEL = {F_SPOT:"Spot tâche/sécurité", F_SUSP:"Suspension déco",
             F_PLAF:"Plafonnier technique", F_APP:"Appoint (lampadaire/applique/réglette)",
             F_COVE:"Ruban LED corniche"}

def count(typ): return sum(1 for f in FIX if f[0]==typ)
def cove_ml(): return round(sum(2*((x1-x0)+(z1-z0)) for (x0,z0,x1,z1,n) in COVES),1)

# ----------------------------------------------------------------------------
# 2) PLAN 2D  (matplotlib)
# ----------------------------------------------------------------------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

def draw_plan(path, title=True):
    fig, ax = plt.subplots(figsize=(10,9.6))
    # emprise
    ax.add_patch(Rectangle((0,0),EXT_W,EXT_D,facecolor="none",edgecolor="#222",lw=3))
    for (nm,x0,z0,x1,z1,area,col) in ROOMS:
        ax.add_patch(Rectangle((x0,z0),x1-x0,z1-z0,facecolor=col,edgecolor="#555",lw=1.2,alpha=0.55))
        cx,cz=(x0+x1)/2,(z0+z1)/2
        ax.text(cx,cz,f"{nm}\n{area}",ha="center",va="center",fontsize=8.5,weight="bold",color="#222")
    # rubans LED corniche (peripherique)
    for (x0,z0,x1,z1,nm) in COVES:
        ax.add_patch(Rectangle((x0,z0),x1-x0,z1-z0,facecolor="none",
            edgecolor="#c77dff",lw=2.4,ls=(0,(6,3)),alpha=0.95))
    # luminaires
    for (typ,x,z,o) in FIX:
        c = FIX_COL[typ]
        if typ==F_SPOT:
            ax.plot(x,z,"o",ms=9,mfc=c,mec="#7a5a00",mew=1.0)
        elif typ==F_SUSP:
            ax.plot(x,z,"v",ms=12,mfc=c,mec="#7a3500",mew=1.0)
        elif typ==F_PLAF:
            ax.plot(x,z,"o",ms=16,mfc=c,mec="#28527a",mew=1.2,alpha=0.9)
        else:
            ax.plot(x,z,"s",ms=11,mfc=c,mec="#1c5c3a",mew=1.0)
    ax.set_xlim(-0.5,EXT_W+0.5); ax.set_ylim(EXT_D+0.5,-0.5)  # z vers le bas
    ax.set_aspect("equal"); ax.axis("off")
    # cotes
    ax.annotate("",xy=(0,-0.25),xytext=(EXT_W,-0.25),arrowprops=dict(arrowstyle="<->",color="#444"))
    ax.text(EXT_W/2,-0.42,"9600 mm",ha="center",va="bottom",fontsize=9,color="#444")
    ax.annotate("",xy=(-0.25,0),xytext=(-0.25,EXT_D),arrowprops=dict(arrowstyle="<->",color="#444"))
    ax.text(-0.42,EXT_D/2,"9100 mm",ha="center",va="center",rotation=90,fontsize=9,color="#444")
    # legende
    from matplotlib.lines import Line2D
    handles=[Line2D([0],[0],marker="o",color="w",mfc=FIX_COL[F_SPOT],mec="#7a5a00",ms=10,label="Spot tâche/sécurité"),
             Line2D([0],[0],marker="v",color="w",mfc=FIX_COL[F_SUSP],mec="#7a3500",ms=11,label="Suspension déco"),
             Line2D([0],[0],marker="o",color="w",mfc=FIX_COL[F_PLAF],mec="#28527a",ms=13,label="Plafonnier technique"),
             Line2D([0],[0],marker="s",color="w",mfc=FIX_COL[F_APP],mec="#1c5c3a",ms=10,label="Appoint"),
             Line2D([0],[0],color="#c77dff",lw=2.4,ls=(0,(6,3)),label="Ruban LED corniche")]
    ax.legend(handles=handles,loc="upper center",bbox_to_anchor=(0.5,-0.03),ncol=5,frameon=False,fontsize=8.5)
    if title:
        ax.set_title("Plan d'éclairage — Proposition 2 « tout indirect »  ·  RDC Module 4  (9,6 × 9,1 m)",
                     fontsize=12,weight="bold",pad=14)
    fig.tight_layout()
    fig.savefig(path,dpi=150,bbox_inches="tight"); plt.close(fig)

PLAN2D = os.path.join(OUT,"plan_eclairage_2D.png")
draw_plan(PLAN2D)
print("OK plan 2D")

# ----------------------------------------------------------------------------
# 3) GEOMETRIE 3D  (boites) -> OBJ + DAE
# ----------------------------------------------------------------------------
# Repere 3D : X=est, Y=haut, Z = -z (Sud -> -Z) pour orientation correcte
def box(cx,cy,cz,sx,sy,sz):
    hx,hy,hz=sx/2,sy/2,sz/2
    v=[(cx-hx,cy-hy,cz-hz),(cx+hx,cy-hy,cz-hz),(cx+hx,cy+hy,cz-hz),(cx-hx,cy+hy,cz-hz),
       (cx-hx,cy-hy,cz+hz),(cx+hx,cy-hy,cz+hz),(cx+hx,cy+hy,cz+hz),(cx-hx,cy+hy,cz+hz)]
    f=[(0,1,2),(0,2,3),(4,6,5),(4,7,6),(0,4,5),(0,5,1),
       (1,5,6),(1,6,2),(2,6,7),(2,7,3),(3,7,4),(3,4,0)]
    return v,f

MESHES=[]  # (name, verts, faces, material)
def add_box(name,cx,cz,sx,sz,cy,sy,mat):
    # plan(x,z) -> 3D(x, y=cy, -z)
    v,f=box(cx,cy,-cz,sx,sy,sz)
    MESHES.append((name,v,f,mat))

# Sol
add_box("Sol", EXT_W/2, EXT_D/2, EXT_W, EXT_D, -0.06,0.12, "Sol")
# Murs exterieurs
add_box("Mur_N", EXT_W/2, 0, EXT_W, WALL, H/2, H, "Mur")
add_box("Mur_S", EXT_W/2, EXT_D, EXT_W, WALL, H/2, H, "Mur")
add_box("Mur_O", 0, EXT_D/2, WALL, EXT_D, H/2, H, "Mur")
add_box("Mur_E", EXT_W, EXT_D/2, WALL, EXT_D, H/2, H, "Mur")
# Cloisons principales (porteur int 200 / cloison 90)
add_box("Cloison_O_centre", 3.30, EXT_D/2, 0.10, EXT_D, H/2, H, "Cloison")
add_box("Cloison_E_centre", 5.30, EXT_D/2, 0.10, EXT_D, H/2, H, "Cloison")
add_box("Cloison_bureau",   1.80, 3.09, 3.0,0.10, H/2, H, "Cloison")
# Dalles colorees par piece (reperage)
def slug(s):
    out="".join(c if (c.isalnum()) else "_" for c in s)
    while "__" in out: out=out.replace("__","_")
    return out.strip("_")
for (nm,x0,z0,x1,z1,area,col) in ROOMS:
    add_box("Zone_"+slug(nm), (x0+x1)/2,(z0+z1)/2, (x1-x0-0.05),(z1-z0-0.05), 0.012,0.02, "Z_"+slug(nm))
# Escalier (marches)
for i in range(10):
    add_box(f"Marche_{i}", 4.30, 4.3+i*0.27, 1.3,0.27, 0.08+i*0.16,0.16, "Marche")
# Luminaires
for k,(typ,x,z,o) in enumerate(FIX):
    if typ==F_SPOT:
        add_box(f"Spot_{k}", x,z,0.12,0.12, H-0.03,0.04, "L_spot")
    elif typ==F_SUSP:
        drop=o.get("drop",0.8)
        add_box(f"Susp_{k}", x,z,0.22,0.22, H-drop,0.18, "L_susp")
        add_box(f"Cord_{k}", x,z,0.02,0.02, H-drop/2,drop, "L_cord")
    elif typ==F_PLAF:
        add_box(f"Plaf_{k}", x,z,0.40,0.40, H-0.04,0.06, "L_plaf")
    else:
        h=o.get("h",1.4)
        add_box(f"App_{k}", x,z,0.20,0.20, h,0.20, "L_app")
        add_box(f"Pied_{k}", x,z,0.05,0.05, h/2,h, "L_cord")
# Rubans LED corniche : 4 brins par piece, en hauteur (uplight)
for k,(x0,z0,x1,z1,nm) in enumerate(COVES):
    yc=H-0.10; w=x1-x0; d=z1-z0
    add_box(f"Cove_{k}_N", (x0+x1)/2,z0, w,0.04, yc,0.04, "L_cove")
    add_box(f"Cove_{k}_S", (x0+x1)/2,z1, w,0.04, yc,0.04, "L_cove")
    add_box(f"Cove_{k}_O", x0,(z0+z1)/2, 0.04,d, yc,0.04, "L_cove")
    add_box(f"Cove_{k}_E", x1,(z0+z1)/2, 0.04,d, yc,0.04, "L_cove")

MAT_RGB = {
 "Sol":(0.85,0.80,0.74),"Mur":(0.90,0.88,0.84),"Cloison":(0.80,0.78,0.74),
 "Marche":(0.71,0.60,0.51),"L_spot":FIX_COL[F_SPOT],"L_susp":FIX_COL[F_SUSP],
 "L_plaf":FIX_COL[F_PLAF],"L_app":FIX_COL[F_APP],"L_cord":(0.15,0.15,0.15),
 "L_cove":FIX_COL[F_COVE],
}
for (nm,x0,z0,x1,z1,area,col) in ROOMS:
    MAT_RGB["Z_"+slug(nm)]=col

# --- OBJ + MTL ---
def write_obj():
    obj=os.path.join(OUT,"model.obj"); mtl=os.path.join(OUT,"model.mtl")
    with open(mtl,"w") as m:
        for name,(r,g,b) in MAT_RGB.items():
            m.write(f"newmtl {name}\nKd {r:.3f} {g:.3f} {b:.3f}\nKa {r*0.3:.3f} {g*0.3:.3f} {b*0.3:.3f}\nd 1.0\nillum 1\n\n")
    with open(obj,"w") as o:
        o.write("# Plan d'eclairage RDC Module 4 - genere\n")
        o.write("mtllib model.mtl\n")
        off=1
        for name,v,f,mat in MESHES:
            o.write(f"g {name}\nusemtl {mat}\n")
            for (x,y,z) in v: o.write(f"v {x:.4f} {y:.4f} {z:.4f}\n")
            for (a,b,c) in f: o.write(f"f {a+off} {b+off} {c+off}\n")
            off+=len(v)
    print("OK OBJ/MTL")
write_obj()

# --- DAE (Collada) ---
def write_dae():
    dae=os.path.join(OUT,"model.dae")
    geos=[]; nodes=[]; mats=[]; effects=[]
    matnames=sorted(MAT_RGB.keys())
    for mn in matnames:
        r,g,b=MAT_RGB[mn]
        effects.append(f'''   <effect id="{mn}-fx"><profile_COMMON><technique sid="t"><lambert>
      <diffuse><color>{r:.3f} {g:.3f} {b:.3f} 1</color></diffuse></lambert></technique></profile_COMMON></effect>''')
        mats.append(f'   <material id="{mn}-mat" name="{mn}"><instance_effect url="#{mn}-fx"/></material>')
    for i,(name,v,f,mat) in enumerate(MESHES):
        gid=f"g{i}"
        pos=" ".join(f"{x:.4f} {y:.4f} {z:.4f}" for (x,y,z) in v)
        idx=" ".join(f"{a} {b} {c}" for (a,b,c) in f)
        geos.append(f'''   <geometry id="{gid}" name="{name}"><mesh>
     <source id="{gid}-p"><float_array id="{gid}-pa" count="{len(v)*3}">{pos}</float_array>
       <technique_common><accessor source="#{gid}-pa" count="{len(v)}" stride="3">
         <param name="X" type="float"/><param name="Y" type="float"/><param name="Z" type="float"/></accessor></technique_common></source>
     <vertices id="{gid}-v"><input semantic="POSITION" source="#{gid}-p"/></vertices>
     <triangles count="{len(f)}" material="{mat}-mat">
       <input semantic="VERTEX" source="#{gid}-v" offset="0"/><p>{idx}</p></triangles></mesh></geometry>''')
        nodes.append(f'''    <node id="n{i}" name="{name}"><instance_geometry url="#{gid}">
       <bind_material><technique_common>
         <instance_material symbol="{mat}-mat" target="#{mat}-mat"/></technique_common></bind_material></instance_geometry></node>''')
    NL="\n"
    doc=f'''<?xml version="1.0" encoding="utf-8"?>
<COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" version="1.4.1">
 <asset><unit name="meter" meter="1"/><up_axis>Y_UP</up_axis></asset>
 <library_effects>
{NL.join(effects)}
 </library_effects>
 <library_materials>
{NL.join(mats)}
 </library_materials>
 <library_geometries>
{NL.join(geos)}
 </library_geometries>
 <library_visual_scenes><visual_scene id="scene" name="scene">
{NL.join(nodes)}
 </visual_scene></library_visual_scenes>
 <scene><instance_visual_scene url="#scene"/></scene>
</COLLADA>'''
    open(dae,"w").write(doc)
    print("OK DAE")
write_dae()

# ----------------------------------------------------------------------------
# 4) PDF (reportlab)
# ----------------------------------------------------------------------------
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
    Table, TableStyle, PageBreak)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

styles=getSampleStyleSheet()
H1=ParagraphStyle("H1",parent=styles["Heading1"],fontSize=20,textColor=colors.HexColor("#1b2430"),spaceAfter=6)
H2=ParagraphStyle("H2",parent=styles["Heading2"],fontSize=13,textColor=colors.HexColor("#b5860b"),spaceBefore=10,spaceAfter=4)
BODY=ParagraphStyle("BODY",parent=styles["BodyText"],fontSize=9.5,leading=13)
SMALL=ParagraphStyle("SMALL",parent=styles["BodyText"],fontSize=8,textColor=colors.grey)
CENTER=ParagraphStyle("C",parent=styles["BodyText"],alignment=TA_CENTER,fontSize=9)

pdf=os.path.join(OUT,"Plan_eclairage_RDC_Module4.pdf")
doc=SimpleDocTemplate(pdf,pagesize=A4,topMargin=16*mm,bottomMargin=14*mm,leftMargin=16*mm,rightMargin=16*mm)
S=[]
def img_fit(path,maxw,maxh):
    from PIL import Image as PImage
    try:
        from reportlab.lib.utils import ImageReader
        iw,ih=ImageReader(path).getSize()
    except Exception:
        iw,ih=maxw,maxh
    r=min(maxw/iw,maxh/ih)
    return Image(path,iw*r,ih*r)

# --- Couverture ---
S.append(Spacer(1,8))
S.append(Paragraph("Proposition d'éclairage — Variante 2",H1))
S.append(Paragraph("« Tout indirect / ambiance »  ·  RDC Module 4  ·  9,60 × 9,10 m",H2))
S.append(Paragraph("<b>Concept :</b> priorité à la lumière indirecte — rubans LED en corniche périphérique "
   "dans les pièces de vie, lampadaires et appliques d'ambiance, suspensions décoratives. "
   "Les spots encastrés sont réduits aux seules fonctions de tâche (plan de travail, bureau) "
   "et de sécurité (escalier).",BODY))
info=[["Projet","Rdc Module 4"],["Client","IDI"],["Échelle plan","1/50 (A3)"],
      ["Date","2025 — version 1"],["Établi le",datetime.date.today().strftime("%d/%m/%Y")]]
t=Table(info,colWidths=[35*mm,120*mm])
t.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),("TEXTCOLOR",(0,0),(0,-1),colors.HexColor("#b5860b")),
   ("FONT",(0,0),(0,-1),"Helvetica-Bold"),("BOTTOMPADDING",(0,0),(-1,-1),3),("LINEBELOW",(0,0),(-1,-1),0.3,colors.HexColor("#ddd"))]))
S.append(t); S.append(Spacer(1,8))
S.append(img_fit(os.path.join(OUT,"plan_source.png"),175*mm,150*mm))
S.append(Paragraph("Plan de sol fourni (cotes réelles).",SMALL))
S.append(PageBreak())

# --- Analyse ---
S.append(Paragraph("1. Analyse & avis",H1))
S.append(Paragraph("Points forts",H2))
for x in ["Logique de 3 couches déjà présente : général encastré + décoratif suspendu + appoints.",
          "Zoning cohérent : suspensions décoratives sur Repas / Cuisine / Salon, encastrés diffus sur circulations."]:
    S.append(Paragraph("• "+x,BODY))
S.append(Paragraph("Points à corriger (par priorité)",H2))
pts=[("Escalier — sécurité","Éclairer chaque nez de marche sans éblouir ; va-et-vient haut + bas ; balisage bas ou ruban LED sous main courante."),
 ("Bureau","Spots devant le poste (pas derrière la tête) pour éviter ombre/reflets écran ; 4000 K (neutre) ; lampe en appoint."),
 ("Cuisine","Spots au bord avant des meubles hauts ; AJOUT réglette LED sous meubles ; suspensions à ~75-85 cm du plan de travail."),
 ("Coin Repas","Grappe à ~80-90 cm au-dessus de la table ; spots périphériques sur variateur séparé."),
 ("Salle détente (15,4 m²)","Zone sous-équipée : AJOUT de sources + lampadaire indirect sur variateur pour l'ambiance."),
 ("Général","Circuits indépendants variables (scénarios), cohérence temp. couleur, interrupteurs à chaque entrée de zone.")]
for i,(k,v) in enumerate(pts,1):
    S.append(Paragraph(f"<b>{i}. {k}.</b> {v}",BODY))
S.append(Paragraph("Niveaux d'éclairement cibles (lux)",H2))
lux=[["Zone","Lux cible","Temp. couleur"],
 ["Cuisine (plan de travail)","300–500","4000 K"],["Bureau","300–500","4000 K"],
 ["Coin Repas","150–300 + accent","2700 K"],["Salon / Détente","100–300 + accent","2700 K"],
 ["Circulations / Entrée","100–150","3000 K"],["Escalier","100 + nez visibles","3000 K"]]
tl=Table(lux,colWidths=[60*mm,45*mm,40*mm])
tl.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1b2430")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
  ("FONT",(0,0),(-1,0),"Helvetica-Bold",9),("FONTSIZE",(0,1),(-1,-1),9),("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#ccc")),
  ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f5f3ee")]),("BOTTOMPADDING",(0,0),(-1,-1),4),("TOPPADDING",(0,0),(-1,-1),4)]))
S.append(tl)
S.append(PageBreak())

# --- Plan d'eclairage 2D ---
S.append(Paragraph("2. Plan d'éclairage proposé (vue de dessus)",H1))
S.append(img_fit(PLAN2D,175*mm,170*mm))
S.append(PageBreak())

# --- Nomenclature ---
S.append(Paragraph("3. Nomenclature des luminaires",H1))
rows=[["Type","Qté","Usage / recommandation"]]
desc={F_COVE:f"Corniche périphérique indirecte (~{cove_ml()} ml) — coeur de l'ambiance",
      F_SUSP:"Décoratif Cuisine (îlot) & Repas (table)",
      F_APP:"Lampadaires indirects, appliques + réglette LED sous meuble",
      F_SPOT:"Tâche (plan de travail, bureau) & sécurité (escalier) uniquement",
      F_PLAF:"Pièces techniques : Buanderie, WC"}
disp={F_COVE:f"{len(COVES)} pièces / ~{cove_ml()} ml"}
for t_ in [F_COVE,F_SUSP,F_APP,F_SPOT,F_PLAF]:
    rows.append([FIX_LABEL[t_],disp.get(t_,str(count(t_))),desc[t_]])
rows.append(["TOTAL points","%d + rubans"%len(FIX),""])
tn=Table(rows,colWidths=[60*mm,18*mm,95*mm])
tn.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1b2430")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
  ("FONT",(0,0),(-1,0),"Helvetica-Bold",9),("FONTSIZE",(0,1),(-1,-1),9),("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#ccc")),
  ("ROWBACKGROUNDS",(0,1),(-1,-2),[colors.white,colors.HexColor("#f5f3ee")]),
  ("BACKGROUND",(0,-1),(-1,-1),colors.HexColor("#e8e2d3")),("FONT",(0,-1),(-1,-1),"Helvetica-Bold",9),
  ("BOTTOMPADDING",(0,0),(-1,-1),4),("TOPPADDING",(0,0),(-1,-1),4)]))
S.append(tn)
S.append(Paragraph("4. Circuits & scénarios recommandés",H2))
for x in ["Circuit A – Ambiance indirecte : tous les rubans LED corniche (variateur, idéalement tunable white 2700–4000 K).",
          "Circuit B – Repas : grappe de suspensions (variateur dédié).",
          "Circuit C – Cuisine fonctionnel : spots plan de travail + réglette LED sous meuble.",
          "Circuit D – Appoints d'ambiance : lampadaires + appliques (Salon / Détente).",
          "Circuit E – Tâches & sécurité : spots bureau + escalier (va-et-vient + balisage, toujours séparé).",
          "Circuit F – Pièces techniques : plafonniers Buanderie / WC."]:
    S.append(Paragraph("• "+x,BODY))
S.append(Paragraph("<b>Note ambiance :</b> alimenter les rubans en 24 V, IRC ≥ 90, ~9–14 W/ml, "
   "profilés alu avec diffuseur pour éviter l'effet pointillé. La corniche éclaire le plafond "
   "(lumière rasante douce) ; prévoir une retombée/gorge de 10–15 cm.",SMALL))
S.append(Spacer(1,8))
S.append(Paragraph("Livrables associes : plan_eclairage_2D.png · model.obj / model.dae (3D, importable SketchUp) · maquette web eclairage-3d.html.",SMALL))

doc.build(S)
print("OK PDF ->",pdf)

# ----------------------------------------------------------------------------
# 5) MAQUETTE WEB 3D (Three.js) recalee aux cotes reelles
# ----------------------------------------------------------------------------
import json
rooms_js=json.dumps([{"n":nm,"x0":x0,"z0":z0,"x1":x1,"z1":z1,"a":area,
                      "c":int(c[0]*255)<<16|int(c[1]*255)<<8|int(c[2]*255)} for (nm,x0,z0,x1,z1,area,c) in ROOMS])
fix_js=json.dumps([{"t":t_,"x":x,"z":z,**o} for (t_,x,z,o) in FIX])
coves_js=json.dumps([{"x0":x0,"z0":z0,"x1":x1,"z1":z1} for (x0,z0,x1,z1,n) in COVES])
html=r"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Maquette 3D eclairage - RDC Module 4 (cotes reelles)</title>
<style>
:root{--bg:#11141a;--accent:#ffcf6b;--txt:#e7ecf3;--muted:#9aa6b8}
*{box-sizing:border-box}html,body{margin:0;height:100%;background:var(--bg);color:var(--txt);
font-family:system-ui,Segoe UI,Roboto,Arial,sans-serif;overflow:hidden}
#app{position:fixed;inset:0}
#ui{position:fixed;top:14px;left:14px;background:rgba(27,31,41,.92);border:1px solid #2a3140;
border-radius:14px;padding:14px 16px;width:266px;backdrop-filter:blur(6px)}
#ui h1{font-size:15px;margin:0 0 2px}#ui .sub{font-size:11px;color:var(--muted);margin-bottom:12px}
.row{display:flex;align-items:center;justify-content:space-between;margin:9px 0;font-size:13px}
input[type=range]{width:120px;accent-color:var(--accent)}
button{background:#222836;color:var(--txt);border:1px solid #313a4c;border-radius:9px;padding:7px 10px;
font-size:12px;cursor:pointer;width:100%;margin-top:4px}button:hover{border-color:var(--accent)}
.switch{position:relative;width:40px;height:22px}.switch input{opacity:0;width:0;height:0}
.slider{position:absolute;inset:0;background:#39414f;border-radius:22px;transition:.2s;cursor:pointer}
.slider:before{content:"";position:absolute;height:16px;width:16px;left:3px;top:3px;background:#cdd5e2;border-radius:50%;transition:.2s}
input:checked+.slider{background:var(--accent)}input:checked+.slider:before{transform:translateX(18px);background:#2a2210}
#legend{position:fixed;bottom:14px;left:14px;background:rgba(27,31,41,.92);border:1px solid #2a3140;
border-radius:12px;padding:10px 14px;font-size:11.5px;color:var(--muted)}#legend b{color:var(--txt)}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:5px;vertical-align:middle}
#hint{position:fixed;bottom:14px;right:14px;font-size:11px;color:var(--muted);background:rgba(27,31,41,.8);padding:7px 11px;border-radius:10px}
</style></head><body><div id="app"></div>
<div id="ui"><h1>Maquette 3D &mdash; Variante 2 (indirect)</h1>
<div class="sub">RDC Module 4 &middot; cotes reelles 9,6 &times; 9,1 m &middot; H 2,6 m</div>
<div class="row"><label>Ambiance (jour &harr; nuit)</label><input id="dayNight" type="range" min="0" max="100" value="65"></div>
<div class="row"><label>Intensite luminaires</label><input id="intensity" type="range" min="0" max="100" value="80"></div>
<div class="row"><label>Plafond</label><span class="switch"><input id="ceiling" type="checkbox"><span class="slider"></span></span></div>
<div class="row"><label>Cone de lumiere</label><span class="switch"><input id="cones" type="checkbox" checked><span class="slider"></span></span></div>
<div class="row"><label>Etiquettes zones</label><span class="switch"><input id="labels" type="checkbox" checked><span class="slider"></span></span></div>
<button id="reset">&#8634; Recentrer</button></div>
<div id="legend">
<div><span class="dot" style="background:#ffd27a"></span><b>Spot encastre</b></div>
<div><span class="dot" style="background:#ff9d5c"></span><b>Suspension</b></div>
<div><span class="dot" style="background:#9ad0ff"></span><b>Plafonnier</b></div>
<div><span class="dot" style="background:#7CFFB2"></span><b>Appoint</b></div>
<div><span class="dot" style="background:#c77dff"></span><b>Ruban LED corniche</b></div></div>
<div id="hint">Souris : tourner &middot; molette : zoom &middot; clic droit : deplacer</div>
<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>
<script type="module">
import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
const ROOMS=__ROOMS__, FIX=__FIX__, COVES=__COVES__;
const W=9.6,D=9.1,H=2.6,WALL=0.3;
const COL={spot:0xffd27a,susp:0xff9d5c,plaf:0x9ad0ff,app:0x7CFFB2,cove:0xc77dff};
const app=document.getElementById('app');
const scene=new THREE.Scene();scene.background=new THREE.Color(0x11141a);
const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth,innerHeight);renderer.shadowMap.enabled=true;app.appendChild(renderer.domElement);
const camera=new THREE.PerspectiveCamera(50,innerWidth/innerHeight,0.1,200);
const HOME=new THREE.Vector3(12,12.5,13);camera.position.copy(HOME);
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;
controls.target.set(W/2,0,D/2);controls.maxPolarAngle=Math.PI/2.05;
const ambient=new THREE.AmbientLight(0xffffff,.35);scene.add(ambient);
const sun=new THREE.DirectionalLight(0xfff2dd,.7);sun.position.set(10,15,7);sun.castShadow=true;
sun.shadow.mapSize.set(2048,2048);Object.assign(sun.shadow.camera,{left:-13,right:13,top:13,bottom:-13});scene.add(sun);
const floor=new THREE.Mesh(new THREE.BoxGeometry(W,.12,D),new THREE.MeshStandardMaterial({color:0xd9cdbd,roughness:.95}));
floor.position.set(W/2,-.06,D/2);floor.receiveShadow=true;scene.add(floor);
const ceiling=new THREE.Mesh(new THREE.PlaneGeometry(W,D),new THREE.MeshStandardMaterial({color:0xf3f1ee,side:THREE.DoubleSide}));
ceiling.rotation.x=Math.PI/2;ceiling.position.set(W/2,H,D/2);ceiling.visible=false;scene.add(ceiling);
const wm=new THREE.MeshStandardMaterial({color:0xe7e2da,roughness:1});
function wall(x,z,w,d,h){const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),wm);m.position.set(x,h/2,z);m.castShadow=m.receiveShadow=true;scene.add(m);}
wall(W/2,0,W,WALL,H);wall(W/2,D,W,WALL,H);wall(0,D/2,WALL,D,H);wall(W,D/2,WALL,D,H);
wall(3.3,D/2,.1,D,H);wall(5.3,D/2,.1,D,H);wall(1.8,3.09,3.0,.1,H);
ROOMS.forEach(z=>{const w=z.x1-z.x0,d=z.z1-z.z0;
 const pad=new THREE.Mesh(new THREE.PlaneGeometry(w-.06,d-.06),new THREE.MeshStandardMaterial({color:z.c,transparent:true,opacity:.55}));
 pad.rotation.x=-Math.PI/2;pad.position.set((z.x0+z.x1)/2,.011,(z.z0+z.z1)/2);pad.receiveShadow=true;scene.add(pad);});
for(let i=0;i<10;i++){const s=new THREE.Mesh(new THREE.BoxGeometry(1.3,.16,.27),new THREE.MeshStandardMaterial({color:0xb59a82}));
 s.position.set(4.3,.08+i*.16,4.3+i*.27);s.castShadow=s.receiveShadow=true;scene.add(s);}
const fixtures=[],coneGroup=new THREE.Group();scene.add(coneGroup);
function addFix(f){const type=f.t,color=COL[type];let y=H-.02,geo;
 if(type==='spot')geo=new THREE.CylinderGeometry(.07,.07,.04,20);
 else if(type==='susp')geo=new THREE.ConeGeometry(.13,.22,24);
 else if(type==='plaf')geo=new THREE.CylinderGeometry(.2,.2,.05,28);
 else geo=new THREE.SphereGeometry(.1,18,18);
 const g=new THREE.Group();
 if(type==='susp'){const drop=f.drop||.8;y=H-drop;const cord=new THREE.Mesh(new THREE.CylinderGeometry(.006,.006,drop,6),new THREE.MeshStandardMaterial({color:0x222}));cord.position.y=drop/2;g.add(cord);}
 if(type==='app')y=f.h||1.4;
 g.position.set(f.x,y,f.z);
 const body=new THREE.Mesh(geo,new THREE.MeshStandardMaterial({color,emissive:color,emissiveIntensity:1.4,roughness:.4}));g.add(body);scene.add(g);
 const baseInt=f.int!=null?f.int*8:(type==='spot'?6:type==='susp'?10:type==='plaf'?13:8);
 let light;if(type==='spot'||type==='susp'){light=new THREE.SpotLight(0xffe6c0,baseInt,9,type==='spot'?.85:.95,.5,1.6);
  const tgt=new THREE.Object3D();tgt.position.set(f.x,0,f.z);scene.add(tgt);light.position.copy(g.position);light.target=tgt;}
 else{light=new THREE.PointLight(0xffe9cf,baseInt,10,1.8);light.position.copy(g.position);}scene.add(light);
 let cone=null;if(type==='spot'||type==='susp'){const h=g.position.y,r=h*Math.tan(type==='spot'?.7:.85);
  cone=new THREE.Mesh(new THREE.ConeGeometry(r,h,24,1,true),new THREE.MeshBasicMaterial({color:0xffe6b0,transparent:true,opacity:.07,side:THREE.DoubleSide,depthWrite:false}));
  cone.position.set(f.x,h/2,f.z);coneGroup.add(cone);}
 fixtures.push({g,light,cone,baseInt});}
FIX.forEach(addFix);
// Rubans LED corniche : brins emissifs + lueur (uplight indirect)
const coveMeshes=[];
COVES.forEach(cv=>{const yc=H-0.10,col=COL.cove;
 const seg=[[(cv.x0+cv.x1)/2,cv.z0,cv.x1-cv.x0,0.04],[(cv.x0+cv.x1)/2,cv.z1,cv.x1-cv.x0,0.04],
            [cv.x0,(cv.z0+cv.z1)/2,0.04,cv.z1-cv.z0],[cv.x1,(cv.z0+cv.z1)/2,0.04,cv.z1-cv.z0]];
 seg.forEach(s=>{const m=new THREE.Mesh(new THREE.BoxGeometry(s[2],0.04,s[3]),
   new THREE.MeshStandardMaterial({color:col,emissive:col,emissiveIntensity:1.5}));
   m.position.set(s[0],yc,s[1]);scene.add(m);coveMeshes.push(m);});
 // quelques sources ponctuelles pour la lueur sur le plafond
 const cx=(cv.x0+cv.x1)/2,cz=(cv.z0+cv.z1)/2;
 [[cv.x0,cz],[cv.x1,cz],[cx,cv.z0],[cx,cv.z1]].forEach(p=>{
   const l=new THREE.PointLight(0xe6ccff,3.5,5,2);l.position.set(p[0],yc+0.05,p[1]);scene.add(l);
   fixtures.push({g:{position:l.position,children:[]},light:l,cone:null,baseInt:3.5});});
});
const labelSprites=[];
function roundRect(c,x,y,w,h,r){c.beginPath();c.moveTo(x+r,y);c.arcTo(x+w,y,x+w,y+h,r);c.arcTo(x+w,y+h,x,y+h,r);c.arcTo(x,y+h,x,y,r);c.arcTo(x,y,x+w,y,r);c.closePath();}
function label(text,sub,x,z){const cv=document.createElement('canvas');cv.width=256;cv.height=96;const c=cv.getContext('2d');
 c.fillStyle='rgba(20,24,32,.82)';roundRect(c,4,4,248,88,14);c.fill();c.fillStyle='#fff';c.font='bold 26px system-ui';c.textAlign='center';c.fillText(text,128,40);
 if(sub){c.fillStyle='#ffcf6b';c.font='22px system-ui';c.fillText(sub,128,72);}
 const tex=new THREE.CanvasTexture(cv);const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:tex,transparent:true,depthTest:false}));
 sp.position.set(x,1.7,z);sp.scale.set(1.5,.56,1);scene.add(sp);labelSprites.push(sp);}
ROOMS.forEach(z=>label(z.n,z.a,(z.x0+z.x1)/2,(z.z0+z.z1)/2));
const $=id=>document.getElementById(id);let iF=.8;
function applyI(){fixtures.forEach(f=>{f.light.intensity=f.baseInt*iF;f.g.children.forEach(c=>{if(c.material&&c.material.emissive)c.material.emissiveIntensity=.4+1.2*iF;});if(f.cone)f.cone.material.opacity=.02+.08*iF;});}
$('intensity').oninput=e=>{iF=e.target.value/100;applyI();};
$('dayNight').oninput=e=>{const d=e.target.value/100;ambient.intensity=.08+.45*d;sun.intensity=.08+.9*d;scene.background=new THREE.Color().setHSL(.6,.18,.06+.1*d);};
$('ceiling').onchange=e=>ceiling.visible=e.target.checked;
$('cones').onchange=e=>coneGroup.visible=e.target.checked;
$('labels').onchange=e=>labelSprites.forEach(s=>s.visible=e.target.checked);
$('reset').onclick=()=>{camera.position.copy(HOME);controls.target.set(W/2,0,D/2);};
applyI();$('dayNight').dispatchEvent(new Event('input'));
addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);});
(function loop(){requestAnimationFrame(loop);controls.update();renderer.render(scene,camera);})();
</script></body></html>"""
html=html.replace("__ROOMS__",rooms_js).replace("__FIX__",fix_js).replace("__COVES__",coves_js)
open(os.path.join(OUT,"..","eclairage-3d.html"),"w").write(html)
print("OK HTML 3D (cotes reelles)")
print("Luminaires:",{t_:count(t_) for t_ in [F_SPOT,F_SUSP,F_PLAF,F_APP]},"total",len(FIX))
