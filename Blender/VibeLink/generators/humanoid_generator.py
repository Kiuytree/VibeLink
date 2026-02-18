"""
humanoid_generator.py - Low Poly Villager Generator
Genera aldeanos masculinos y femeninos con variación procedural por seed.
Sin rig, sin animaciones - solo malla estática de calidad.
"""
import bpy
import bmesh
import random
import math
from mathutils import Vector

# ─────────────────────────────────────────────────────────────────
#  MATERIAL HELPER
# ─────────────────────────────────────────────────────────────────
def get_mat(name, color):
    """Crea o reutiliza un material por nombre."""
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name=name)
    m.diffuse_color = (*color[:3], 1.0)
    return m

# ─────────────────────────────────────────────────────────────────
#  MESH PRIMITIVE HELPERS
# ─────────────────────────────────────────────────────────────────
def box(name, cx, cy, cz, sx, sy, sz, mat):
    """Crea un cubo escalado en la posición dada."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, cz))
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(scale=True)
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return obj

def cyl(name, cx, cy, cz, r, h, verts, mat):
    """Crea un cilindro."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h,
                                         location=(cx, cy, cz))
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return obj

def sphere(name, cx, cy, cz, r, sub, mat):
    """Crea una icosfera."""
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, radius=r,
                                           location=(cx, cy, cz))
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return obj

def cone(name, cx, cy, cz, r, h, verts, mat):
    """Crea un cono."""
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=0,
                                     depth=h, location=(cx, cy, cz))
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return obj

# ─────────────────────────────────────────────────────────────────
#  JOIN HELPER
# ─────────────────────────────────────────────────────────────────
def join_all(parts, final_name):
    """Une todos los objetos en uno solo."""
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        if p is not None:
            p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    result = bpy.context.active_object
    result.name = final_name
    return result

# ─────────────────────────────────────────────────────────────────
#  COLOR PALETTES
# ─────────────────────────────────────────────────────────────────
SKIN_TONES = [
    (0.95, 0.80, 0.65),  # Claro
    (0.85, 0.65, 0.50),  # Medio
    (0.70, 0.50, 0.35),  # Moreno
    (0.45, 0.30, 0.20),  # Oscuro
]

HAIR_COLORS = [
    (0.08, 0.05, 0.02),  # Negro
    (0.25, 0.15, 0.05),  # Castaño oscuro
    (0.50, 0.30, 0.10),  # Castaño
    (0.80, 0.60, 0.20),  # Rubio
    (0.70, 0.20, 0.10),  # Pelirrojo
    (0.75, 0.75, 0.75),  # Gris (mayor)
    (0.95, 0.95, 0.90),  # Blanco (anciano)
]

CLOTH_PALETTES = [
    # (primary, secondary, accent)
    [(0.55, 0.25, 0.10), (0.35, 0.15, 0.05), (0.80, 0.65, 0.30)],  # Marrón/Cuero
    [(0.20, 0.35, 0.55), (0.15, 0.25, 0.40), (0.85, 0.80, 0.60)],  # Azul/Marino
    [(0.25, 0.45, 0.20), (0.15, 0.30, 0.12), (0.80, 0.70, 0.40)],  # Verde/Bosque
    [(0.55, 0.20, 0.20), (0.35, 0.12, 0.12), (0.85, 0.75, 0.50)],  # Rojo/Burdeos
    [(0.50, 0.45, 0.35), (0.35, 0.30, 0.22), (0.80, 0.75, 0.55)],  # Gris/Piedra
    [(0.60, 0.50, 0.20), (0.40, 0.32, 0.12), (0.90, 0.85, 0.60)],  # Dorado/Ocre
]

# ─────────────────────────────────────────────────────────────────
#  MAIN GENERATOR
# ─────────────────────────────────────────────────────────────────
def generate(params):
    seed  = params.get("seed", 42)
    style = params.get("style", "villager")  # villager | guard | elder | female_villager | female_elder
    rng   = random.Random(seed)

    # ── Determinar género ──────────────────────────────────────────
    is_female = "female" in style or rng.random() < 0.5
    is_elder  = "elder"  in style or rng.random() < 0.15
    is_guard  = "guard"  in style

    # ── Proporciones base ──────────────────────────────────────────
    if is_female:
        H       = rng.uniform(1.55, 1.70)
        torso_w = rng.uniform(0.18, 0.22)
        hip_w   = rng.uniform(0.22, 0.28)   # Caderas más anchas
        shoulder_w = rng.uniform(0.20, 0.24)
        leg_w   = rng.uniform(0.09, 0.11)
        arm_w   = rng.uniform(0.07, 0.09)
        head_r  = rng.uniform(0.12, 0.14)
    elif is_guard:
        H       = rng.uniform(1.80, 1.95)
        torso_w = rng.uniform(0.26, 0.32)
        hip_w   = rng.uniform(0.24, 0.28)
        shoulder_w = rng.uniform(0.32, 0.38)
        leg_w   = rng.uniform(0.12, 0.15)
        arm_w   = rng.uniform(0.10, 0.13)
        head_r  = rng.uniform(0.13, 0.15)
    elif is_elder:
        H       = rng.uniform(1.55, 1.68)
        torso_w = rng.uniform(0.20, 0.25)
        hip_w   = rng.uniform(0.20, 0.24)
        shoulder_w = rng.uniform(0.20, 0.25)
        leg_w   = rng.uniform(0.09, 0.11)
        arm_w   = rng.uniform(0.07, 0.09)
        head_r  = rng.uniform(0.12, 0.14)
    else:  # villager masculino
        H       = rng.uniform(1.68, 1.82)
        torso_w = rng.uniform(0.22, 0.27)
        hip_w   = rng.uniform(0.20, 0.25)
        shoulder_w = rng.uniform(0.26, 0.32)
        leg_w   = rng.uniform(0.10, 0.13)
        arm_w   = rng.uniform(0.08, 0.10)
        head_r  = rng.uniform(0.12, 0.15)

    # ── Alturas clave (desde el suelo) ────────────────────────────
    foot_z     = 0.0
    ankle_z    = H * 0.08
    knee_z     = H * 0.28
    hip_z      = H * 0.52
    waist_z    = H * 0.60
    chest_z    = H * 0.72
    shoulder_z = H * 0.82
    neck_z     = H * 0.88
    head_cz    = H * 0.93 + head_r

    # ── Colores ───────────────────────────────────────────────────
    skin_col   = SKIN_TONES[rng.randint(0, len(SKIN_TONES)-1)]
    hair_col   = HAIR_COLORS[rng.randint(0, len(HAIR_COLORS)-1)]
    if is_elder:
        hair_col = rng.choice([(0.75, 0.75, 0.75), (0.90, 0.90, 0.88)])
    palette    = rng.choice(CLOTH_PALETTES)
    cloth_pri  = palette[0]
    cloth_sec  = palette[1]
    cloth_acc  = palette[2]

    # ── Materiales ────────────────────────────────────────────────
    uid = f"{seed}"
    m_skin  = get_mat(f"Mat_F_Skin_{uid}",  skin_col)
    m_hair  = get_mat(f"Mat_F_Hair_{uid}",  hair_col)
    m_cloth = get_mat(f"Mat_F_Cloth_{uid}", cloth_pri)
    m_sec   = get_mat(f"Mat_F_Sec_{uid}",   cloth_sec)
    m_acc   = get_mat(f"Mat_F_Acc_{uid}",   cloth_acc)
    m_eye   = get_mat(f"Mat_F_Eye_{uid}",   (0.05, 0.05, 0.08))

    parts = []

    # ─────────────────────────────────────────────────────────────
    #  PIERNAS
    # ─────────────────────────────────────────────────────────────
    for sx, side in [(-1, "L"), (1, "R")]:
        lx = sx * (hip_w * 0.35)

        # Muslo
        thigh_h = knee_z - hip_z
        parts.append(box(f"Thigh_{side}", lx, 0,
                         hip_z + thigh_h * 0.5,
                         leg_w, leg_w * 0.9, abs(thigh_h), m_cloth))

        # Espinilla
        shin_h = ankle_z - knee_z
        parts.append(box(f"Shin_{side}", lx, 0,
                         knee_z + shin_h * 0.5,
                         leg_w * 0.85, leg_w * 0.85, abs(shin_h), m_skin))

        # Pie
        parts.append(box(f"Foot_{side}", lx, leg_w * 0.3, ankle_z + 0.03,
                         leg_w * 0.9, leg_w * 1.8, 0.07, m_sec))

    # ─────────────────────────────────────────────────────────────
    #  TORSO
    # ─────────────────────────────────────────────────────────────
    # Cadera/Pelvis
    parts.append(box("Pelvis", 0, 0,
                     (hip_z + waist_z) * 0.5,
                     hip_w, hip_w * 0.7, waist_z - hip_z + 0.02, m_cloth))

    # Torso principal
    torso_h = chest_z - waist_z
    parts.append(box("Torso", 0, 0,
                     waist_z + torso_h * 0.5,
                     torso_w, torso_w * 0.65, torso_h, m_cloth))

    # Pecho/Hombros (más ancho arriba)
    chest_h = shoulder_z - chest_z
    parts.append(box("Chest", 0, 0,
                     chest_z + chest_h * 0.5,
                     shoulder_w, shoulder_w * 0.6, chest_h, m_cloth))

    # Cinturón/Detalle
    parts.append(box("Belt", 0, 0,
                     waist_z + 0.01,
                     hip_w * 1.02, hip_w * 0.72, 0.04, m_acc))

    # Femenino: falda/vestido
    if is_female:
        skirt_h = hip_z - foot_z * 0.5
        parts.append(box("Skirt", 0, 0,
                         hip_z - skirt_h * 0.5,
                         hip_w * 1.3, hip_w * 0.9, skirt_h * 0.6, m_cloth))

    # ─────────────────────────────────────────────────────────────
    #  BRAZOS
    # ─────────────────────────────────────────────────────────────
    elbow_z = shoulder_z - (shoulder_z - waist_z) * 0.50
    wrist_z = elbow_z    - (shoulder_z - waist_z) * 0.42

    for sx, side in [(-1, "L"), (1, "R")]:
        ax = sx * (shoulder_w * 0.5 + arm_w * 0.4)

        # Hombro (pequeño cubo de unión)
        parts.append(box(f"Shoulder_{side}", ax, 0, shoulder_z,
                         arm_w * 1.1, arm_w * 1.1, arm_w * 0.8, m_cloth))

        # Brazo superior
        ua_h = elbow_z - shoulder_z
        parts.append(box(f"UpperArm_{side}", ax, 0,
                         shoulder_z + ua_h * 0.5,
                         arm_w, arm_w, abs(ua_h), m_cloth))

        # Antebrazo
        la_h = wrist_z - elbow_z
        parts.append(box(f"LowerArm_{side}", ax, 0,
                         elbow_z + la_h * 0.5,
                         arm_w * 0.85, arm_w * 0.85, abs(la_h), m_skin))

        # Mano
        parts.append(box(f"Hand_{side}", ax, 0, wrist_z - 0.04,
                         arm_w * 0.9, arm_w * 1.1, 0.09, m_skin))

    # ─────────────────────────────────────────────────────────────
    #  CUELLO
    # ─────────────────────────────────────────────────────────────
    neck_h = head_cz - head_r - neck_z
    parts.append(box("Neck", 0, 0,
                     neck_z + neck_h * 0.5,
                     head_r * 0.55, head_r * 0.55, neck_h, m_skin))

    # ─────────────────────────────────────────────────────────────
    #  CABEZA
    # ─────────────────────────────────────────────────────────────
    # Forma base de la cabeza (ligeramente rectangular)
    head_sx = head_r * rng.uniform(1.7, 2.0)
    head_sy = head_r * rng.uniform(1.5, 1.8)
    head_sz = head_r * rng.uniform(1.9, 2.2)
    parts.append(box("Head", 0, 0, head_cz,
                     head_sx, head_sy, head_sz, m_skin))

    # Ojos
    eye_z  = head_cz + head_sz * 0.10
    eye_x  = head_sx * 0.28
    eye_r  = head_r * 0.12
    eye_depth = head_sy * 0.52
    for sx in [-1, 1]:
        parts.append(box(f"Eye_{'L' if sx<0 else 'R'}", sx * eye_x, eye_depth, eye_z,
                         eye_r * 1.5, eye_r * 0.3, eye_r * 1.2, m_eye))

    # Nariz
    nose_h = head_r * rng.uniform(0.15, 0.25)
    parts.append(box("Nose", 0, head_sy * 0.52, head_cz - head_sz * 0.05,
                     head_r * 0.15, nose_h, head_r * 0.18, m_skin))

    # ─────────────────────────────────────────────────────────────
    #  PELO / SOMBRERO
    # ─────────────────────────────────────────────────────────────
    hair_style = rng.randint(0, 3)

    if hair_style == 0:
        # Pelo corto (caja encima)
        parts.append(box("Hair", 0, 0, head_cz + head_sz * 0.45,
                         head_sx * 1.05, head_sy * 1.0, head_sz * 0.35, m_hair))

    elif hair_style == 1:
        # Pelo largo (caja encima + laterales)
        parts.append(box("HairTop", 0, 0, head_cz + head_sz * 0.45,
                         head_sx * 1.05, head_sy * 1.0, head_sz * 0.35, m_hair))
        parts.append(box("HairSideL", -head_sx * 0.52, 0, head_cz - head_sz * 0.1,
                         head_r * 0.25, head_sy * 0.9, head_sz * 0.8, m_hair))
        parts.append(box("HairSideR",  head_sx * 0.52, 0, head_cz - head_sz * 0.1,
                         head_r * 0.25, head_sy * 0.9, head_sz * 0.8, m_hair))
        if is_female:
            parts.append(box("HairBack", 0, -head_sy * 0.55, head_cz - head_sz * 0.2,
                             head_sx * 0.9, head_r * 0.3, head_sz * 1.0, m_hair))

    elif hair_style == 2:
        # Sombrero cónico (aldeano/campesino)
        hat_r = head_sx * 0.65
        hat_h = head_r * rng.uniform(1.2, 1.8)
        parts.append(cone("Hat", 0, 0, head_cz + head_sz * 0.5 + hat_h * 0.5,
                          hat_r, hat_h, 8, m_sec))
        # Ala del sombrero
        parts.append(box("HatBrim", 0, 0, head_cz + head_sz * 0.5,
                         hat_r * 2.2, hat_r * 2.2, hat_h * 0.12, m_sec))

    else:
        # Capucha/Pañuelo (caja redondeada)
        parts.append(box("Hood", 0, -head_sy * 0.1, head_cz + head_sz * 0.35,
                         head_sx * 1.1, head_sy * 1.2, head_sz * 0.55, m_cloth))

    # ─────────────────────────────────────────────────────────────
    #  ACCESORIOS OPCIONALES
    # ─────────────────────────────────────────────────────────────
    # Barba (solo masculinos adultos, 40% probabilidad)
    if not is_female and not is_elder and rng.random() < 0.4:
        beard_col = hair_col
        m_beard = get_mat(f"Mat_F_Hair_{uid}", beard_col)
        parts.append(box("Beard", 0, head_sy * 0.48, head_cz - head_sz * 0.25,
                         head_sx * 0.6, head_r * 0.25, head_sz * 0.4, m_beard))

    # Barba blanca para ancianos
    if is_elder and rng.random() < 0.7:
        m_wbeard = get_mat(f"Mat_F_WhiteHair_{uid}", (0.90, 0.90, 0.88))
        parts.append(box("ElderBeard", 0, head_sy * 0.48, head_cz - head_sz * 0.30,
                         head_sx * 0.55, head_r * 0.22, head_sz * 0.5, m_wbeard))

    # Bolsa/Mochila (30% probabilidad)
    if rng.random() < 0.3:
        bag_w = torso_w * 0.5
        bag_h = (chest_z - waist_z) * 0.7
        parts.append(box("Bag", 0, -torso_w * 0.45,
                         waist_z + bag_h * 0.5 + 0.05,
                         bag_w, bag_w * 0.4, bag_h, m_sec))

    # ─────────────────────────────────────────────────────────────
    #  JOIN Y EXPORTAR
    # ─────────────────────────────────────────────────────────────
    gender_tag = "F" if is_female else "M"
    type_tag   = "Elder" if is_elder else ("Guard" if is_guard else "Villager")
    final_name = f"Villager_{gender_tag}_{type_tag}_{seed}"

    result = join_all(parts, final_name)
    return result
