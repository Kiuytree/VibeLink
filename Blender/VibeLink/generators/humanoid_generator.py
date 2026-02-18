"""
humanoid_generator.py - Low Poly Villager Generator v2
Aldeanos masculinos y femeninos con proporciones correctas y variación visual.
"""
import bpy
import random

# ─────────────────────────────────────────────────────────────────
#  MATERIAL HELPER
# ─────────────────────────────────────────────────────────────────
def get_mat(name, color):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name=name)
    m.use_nodes = False
    m.diffuse_color = (color[0], color[1], color[2], 1.0)
    return m

# ─────────────────────────────────────────────────────────────────
#  PRIMITIVES — siempre en coordenadas absolutas
# ─────────────────────────────────────────────────────────────────
def box(name, cx, cy, cz, sx, sy, sz, mat):
    """Cubo centrado en (cx,cy,cz) con dimensiones (sx,sy,sz)."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, cz))
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(scale=True)
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return obj

def cone_hat(name, cx, cy, cz, r_base, height, mat):
    """Cono de 6 caras para sombrero."""
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=r_base, radius2=0.01,
                                     depth=height, location=(cx, cy, cz))
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return obj

# ─────────────────────────────────────────────────────────────────
#  JOIN
# ─────────────────────────────────────────────────────────────────
def join_all(parts, final_name):
    valid = [p for p in parts if p is not None]
    bpy.ops.object.select_all(action='DESELECT')
    for p in valid:
        p.select_set(True)
    bpy.context.view_layer.objects.active = valid[0]
    bpy.ops.object.join()
    result = bpy.context.active_object
    result.name = final_name
    return result

# ─────────────────────────────────────────────────────────────────
#  PALETAS
# ─────────────────────────────────────────────────────────────────
SKIN_TONES = [
    (0.93, 0.78, 0.62),
    (0.82, 0.62, 0.46),
    (0.65, 0.45, 0.30),
    (0.40, 0.27, 0.17),
]

HAIR_COLORS = [
    (0.06, 0.04, 0.02),   # Negro
    (0.22, 0.13, 0.05),   # Castaño oscuro
    (0.48, 0.28, 0.10),   # Castaño
    (0.78, 0.58, 0.18),   # Rubio
    (0.65, 0.18, 0.08),   # Pelirrojo
    (0.70, 0.70, 0.70),   # Gris
    (0.92, 0.92, 0.90),   # Blanco
]

# Paletas: (ropa_principal, ropa_secundaria, acento/cinturon)
CLOTH_PALETTES = [
    ((0.52, 0.22, 0.08), (0.32, 0.13, 0.05), (0.78, 0.62, 0.28)),  # Marrón cuero
    ((0.18, 0.32, 0.52), (0.12, 0.22, 0.38), (0.82, 0.75, 0.52)),  # Azul marino
    ((0.22, 0.42, 0.18), (0.14, 0.28, 0.11), (0.78, 0.68, 0.38)),  # Verde bosque
    ((0.52, 0.18, 0.18), (0.32, 0.10, 0.10), (0.82, 0.72, 0.48)),  # Rojo burdeos
    ((0.48, 0.43, 0.33), (0.32, 0.28, 0.20), (0.78, 0.72, 0.52)),  # Gris piedra
    ((0.58, 0.48, 0.18), (0.38, 0.30, 0.10), (0.88, 0.82, 0.58)),  # Dorado ocre
    ((0.35, 0.18, 0.48), (0.22, 0.10, 0.32), (0.82, 0.72, 0.52)),  # Púrpura
]

# ─────────────────────────────────────────────────────────────────
#  GENERADOR PRINCIPAL
# ─────────────────────────────────────────────────────────────────
def generate(params):
    seed  = params.get("seed", 42)
    style = params.get("style", "villager")
    rng   = random.Random(seed)

    is_female = "female" in style
    is_elder  = "elder"  in style
    is_guard  = "guard"  in style

    # ── Proporciones ──────────────────────────────────────────────
    # Altura total
    if is_guard:
        H = rng.uniform(1.85, 2.00)
    elif is_elder:
        H = rng.uniform(1.55, 1.68)
    elif is_female:
        H = rng.uniform(1.58, 1.72)
    else:
        H = rng.uniform(1.68, 1.82)

    # Anchuras relativas a H
    if is_female:
        shoulder_w = H * rng.uniform(0.155, 0.175)
        hip_w      = H * rng.uniform(0.170, 0.195)
        torso_d    = shoulder_w * 0.62
    elif is_guard:
        shoulder_w = H * rng.uniform(0.200, 0.230)
        hip_w      = H * rng.uniform(0.175, 0.200)
        torso_d    = shoulder_w * 0.68
    else:
        shoulder_w = H * rng.uniform(0.170, 0.195)
        hip_w      = H * rng.uniform(0.160, 0.185)
        torso_d    = shoulder_w * 0.65

    leg_w  = H * rng.uniform(0.072, 0.088)
    arm_w  = H * rng.uniform(0.055, 0.068)
    head_w = H * rng.uniform(0.130, 0.155)
    head_h = head_w * rng.uniform(1.10, 1.30)
    head_d = head_w * rng.uniform(0.90, 1.10)

    # ── Alturas clave (desde el suelo) ────────────────────────────
    # Proporciones clásicas: cabeza = H/8, piernas = H*0.47, torso = H*0.35
    foot_h     = H * 0.040   # Altura del pie
    leg_total  = H * 0.470   # Desde suelo hasta cadera
    hip_z      = leg_total                          # Centro de cadera
    waist_z    = hip_z   + H * 0.060               # Cintura
    chest_z    = waist_z + H * 0.130               # Pecho
    shoulder_z = chest_z + H * 0.080               # Hombros
    neck_bot_z = shoulder_z                         # Base del cuello
    neck_top_z = neck_bot_z + H * 0.045            # Top del cuello
    head_cz    = neck_top_z + head_h * 0.5         # Centro de la cabeza

    knee_z     = H * 0.230   # Rodilla
    ankle_z    = H * 0.055   # Tobillo

    elbow_z    = shoulder_z - H * 0.130
    wrist_z    = elbow_z    - H * 0.115

    # ── Colores ───────────────────────────────────────────────────
    skin_col  = SKIN_TONES[rng.randint(0, len(SKIN_TONES)-1)]
    hair_col  = HAIR_COLORS[rng.randint(0, len(HAIR_COLORS)-1)]
    if is_elder:
        hair_col = rng.choice([(0.70, 0.70, 0.70), (0.92, 0.92, 0.90)])

    palette   = CLOTH_PALETTES[rng.randint(0, len(CLOTH_PALETTES)-1)]
    cloth_col = palette[0]
    sec_col   = palette[1]
    acc_col   = palette[2]

    # ── Materiales (nombres únicos por seed para variedad) ────────
    uid = str(seed)
    m_skin  = get_mat(f"Mat_F_Skin_{uid}",  skin_col)
    m_hair  = get_mat(f"Mat_F_Hair_{uid}",  hair_col)
    m_cloth = get_mat(f"Mat_F_Cloth_{uid}", cloth_col)
    m_sec   = get_mat(f"Mat_F_Sec_{uid}",   sec_col)
    m_acc   = get_mat(f"Mat_F_Acc_{uid}",   acc_col)
    m_eye   = get_mat(f"Mat_F_Eye_{uid}",   (0.04, 0.04, 0.06))
    m_white = get_mat(f"Mat_F_White_{uid}", (0.92, 0.92, 0.90))

    parts = []

    # ─────────────────────────────────────────────────────────────
    #  PIERNAS
    # ─────────────────────────────────────────────────────────────
    leg_gap = hip_w * 0.28   # Separación entre piernas desde centro

    for sx in [-1, 1]:
        lx = sx * leg_gap

        # Muslo: desde cadera hasta rodilla
        thigh_h = hip_z - knee_z
        thigh_cz = knee_z + thigh_h * 0.5
        parts.append(box(f"Thigh_{'L' if sx<0 else 'R'}",
                         lx, 0, thigh_cz,
                         leg_w, leg_w * 0.88, thigh_h, m_cloth))

        # Espinilla: desde rodilla hasta tobillo
        shin_h = knee_z - ankle_z
        shin_cz = ankle_z + shin_h * 0.5
        parts.append(box(f"Shin_{'L' if sx<0 else 'R'}",
                         lx, 0, shin_cz,
                         leg_w * 0.85, leg_w * 0.82, shin_h, m_skin))

        # Pie: plano, ligeramente hacia adelante
        parts.append(box(f"Foot_{'L' if sx<0 else 'R'}",
                         lx, leg_w * 0.35, ankle_z * 0.5,
                         leg_w * 0.88, leg_w * 1.70, ankle_z, m_sec))

    # ─────────────────────────────────────────────────────────────
    #  CADERA / PELVIS
    # ─────────────────────────────────────────────────────────────
    # Bloque que une las piernas al torso (sin hueco)
    pelvis_h = waist_z - (hip_z - H * 0.04)
    pelvis_cz = (hip_z - H * 0.04) + pelvis_h * 0.5
    parts.append(box("Pelvis", 0, 0, pelvis_cz,
                     hip_w, hip_w * 0.68, pelvis_h, m_cloth))

    # Falda femenina (reemplaza pelvis visual)
    if is_female:
        skirt_bot = knee_z + H * 0.04
        skirt_h   = (hip_z + H * 0.04) - skirt_bot
        skirt_cz  = skirt_bot + skirt_h * 0.5
        parts.append(box("Skirt", 0, 0, skirt_cz,
                         hip_w * 1.25, hip_w * 0.82, skirt_h, m_cloth))

    # ─────────────────────────────────────────────────────────────
    #  TORSO
    # ─────────────────────────────────────────────────────────────
    torso_h  = shoulder_z - waist_z
    torso_cz = waist_z + torso_h * 0.5
    parts.append(box("Torso", 0, 0, torso_cz,
                     shoulder_w, torso_d, torso_h, m_cloth))

    # Cinturón
    parts.append(box("Belt", 0, 0, waist_z,
                     hip_w * 1.02, hip_w * 0.70, H * 0.028, m_acc))

    # Detalle de ropa (línea en el pecho)
    if rng.random() < 0.5:
        parts.append(box("ChestDetail", 0, torso_d * 0.51, chest_z,
                         shoulder_w * 0.35, H * 0.004, H * 0.12, m_acc))

    # ─────────────────────────────────────────────────────────────
    #  CUELLO (conecta torso con cabeza sin hueco)
    # ─────────────────────────────────────────────────────────────
    neck_h  = neck_top_z - neck_bot_z
    neck_cz = neck_bot_z + neck_h * 0.5
    neck_w  = head_w * 0.52
    parts.append(box("Neck", 0, 0, neck_cz,
                     neck_w, neck_w * 0.88, neck_h, m_skin))

    # ─────────────────────────────────────────────────────────────
    #  CABEZA
    # ─────────────────────────────────────────────────────────────
    parts.append(box("Head", 0, 0, head_cz,
                     head_w, head_d, head_h, m_skin))

    # Ojos (dos cubitos en la cara frontal)
    eye_z   = head_cz + head_h * 0.08
    eye_x   = head_w  * 0.26
    eye_w   = head_w  * 0.14
    eye_h   = head_h  * 0.14
    eye_y   = head_d  * 0.51
    for sx in [-1, 1]:
        parts.append(box(f"Eye_{'L' if sx<0 else 'R'}",
                         sx * eye_x, eye_y, eye_z,
                         eye_w, H * 0.003, eye_h, m_eye))

    # Cejas (opcional, 60%)
    if rng.random() < 0.6:
        brow_z = eye_z + eye_h * 0.85
        brow_col = tuple(max(0, c - 0.15) for c in skin_col)
        m_brow = get_mat(f"Mat_F_Brow_{uid}", brow_col)
        for sx in [-1, 1]:
            parts.append(box(f"Brow_{'L' if sx<0 else 'R'}",
                             sx * eye_x, eye_y, brow_z,
                             eye_w * 1.1, H * 0.003, eye_h * 0.28, m_brow))

    # Nariz
    nose_w = head_w * 0.12
    nose_h = head_h * 0.14
    nose_y = head_d * 0.52
    parts.append(box("Nose", 0, nose_y, head_cz - head_h * 0.06,
                     nose_w, H * 0.018, nose_h, m_skin))

    # ─────────────────────────────────────────────────────────────
    #  BRAZOS
    # ─────────────────────────────────────────────────────────────
    arm_x = shoulder_w * 0.5 + arm_w * 0.45

    for sx in [-1, 1]:
        ax = sx * arm_x

        # Hombro (pequeño cubo de unión, mismo color que torso)
        parts.append(box(f"Shoulder_{'L' if sx<0 else 'R'}",
                         ax, 0, shoulder_z,
                         arm_w * 1.05, arm_w * 1.05, arm_w * 0.75, m_cloth))

        # Brazo superior
        ua_h  = shoulder_z - elbow_z
        ua_cz = elbow_z + ua_h * 0.5
        parts.append(box(f"UpperArm_{'L' if sx<0 else 'R'}",
                         ax, 0, ua_cz,
                         arm_w, arm_w * 0.92, ua_h, m_cloth))

        # Antebrazo
        la_h  = elbow_z - wrist_z
        la_cz = wrist_z + la_h * 0.5
        parts.append(box(f"LowerArm_{'L' if sx<0 else 'R'}",
                         ax, 0, la_cz,
                         arm_w * 0.88, arm_w * 0.85, la_h, m_skin))

        # Mano
        hand_h = H * 0.058
        parts.append(box(f"Hand_{'L' if sx<0 else 'R'}",
                         ax, 0, wrist_z - hand_h * 0.5,
                         arm_w * 0.88, arm_w * 1.05, hand_h, m_skin))

    # ─────────────────────────────────────────────────────────────
    #  PELO / SOMBRERO
    # ─────────────────────────────────────────────────────────────
    hair_style = rng.randint(0, 3)
    hair_top_z = head_cz + head_h * 0.5  # Tope de la cabeza

    if hair_style == 0:
        # Pelo corto: capa fina encima
        parts.append(box("HairTop", 0, 0, hair_top_z + head_h * 0.10,
                         head_w * 1.04, head_d * 1.02, head_h * 0.22, m_hair))

    elif hair_style == 1:
        # Pelo largo: encima + laterales + atrás
        parts.append(box("HairTop", 0, 0, hair_top_z + head_h * 0.10,
                         head_w * 1.04, head_d * 1.02, head_h * 0.22, m_hair))
        side_h = head_h * 0.75
        side_cz = head_cz - head_h * 0.10
        parts.append(box("HairL", -head_w * 0.52, 0, side_cz,
                         head_w * 0.18, head_d * 0.95, side_h, m_hair))
        parts.append(box("HairR",  head_w * 0.52, 0, side_cz,
                         head_w * 0.18, head_d * 0.95, side_h, m_hair))
        if is_female:
            parts.append(box("HairBack", 0, -head_d * 0.55, side_cz,
                             head_w * 0.88, head_d * 0.20, side_h * 1.1, m_hair))

    elif hair_style == 2:
        # Sombrero cónico campesino
        brim_h  = head_h * 0.12
        brim_r  = head_w * 0.72
        cone_h  = head_h * rng.uniform(0.55, 0.80)
        brim_cz = hair_top_z + brim_h * 0.5
        cone_cz = brim_cz + brim_h * 0.5 + cone_h * 0.5
        # Ala
        parts.append(box("HatBrim", 0, 0, brim_cz,
                         brim_r * 2.0, brim_r * 2.0, brim_h, m_sec))
        # Cono
        parts.append(cone_hat("HatCone", 0, 0, cone_cz,
                              brim_r * 0.72, cone_h, m_sec))

    else:
        # Capucha/Gorro redondeado
        hood_h = head_h * 0.55
        parts.append(box("Hood", 0, -head_d * 0.08, hair_top_z + hood_h * 0.5,
                         head_w * 1.08, head_d * 1.12, hood_h, m_cloth))

    # ─────────────────────────────────────────────────────────────
    #  ACCESORIOS
    # ─────────────────────────────────────────────────────────────
    # Barba masculina (40%)
    if not is_female and rng.random() < 0.40:
        beard_h = head_h * rng.uniform(0.28, 0.45)
        beard_cz = head_cz - head_h * 0.30
        beard_col = tuple(max(0, c - 0.05) for c in hair_col)
        m_beard = get_mat(f"Mat_F_Beard_{uid}", beard_col)
        parts.append(box("Beard", 0, head_d * 0.50, beard_cz,
                         head_w * 0.58, H * 0.018, beard_h, m_beard))

    # Barba blanca anciano (70%)
    if is_elder and rng.random() < 0.70:
        beard_h = head_h * rng.uniform(0.35, 0.55)
        beard_cz = head_cz - head_h * 0.32
        parts.append(box("ElderBeard", 0, head_d * 0.50, beard_cz,
                         head_w * 0.55, H * 0.016, beard_h, m_white))

    # Bolsa/Mochila (25%)
    if rng.random() < 0.25:
        bag_w = shoulder_w * 0.38
        bag_h = (chest_z - waist_z) * 0.65
        bag_cz = waist_z + bag_h * 0.5 + H * 0.04
        parts.append(box("Bag", 0, -torso_d * 0.52, bag_cz,
                         bag_w, bag_w * 0.38, bag_h, m_sec))

    # Bufanda (20%)
    if rng.random() < 0.20:
        scarf_col = CLOTH_PALETTES[rng.randint(0, len(CLOTH_PALETTES)-1)][2]
        m_scarf = get_mat(f"Mat_F_Scarf_{uid}", scarf_col)
        parts.append(box("Scarf", 0, 0, neck_bot_z + neck_h * 0.5,
                         neck_w * 1.6, neck_w * 1.5, neck_h * 0.6, m_scarf))

    # ─────────────────────────────────────────────────────────────
    #  JOIN Y RETORNO
    # ─────────────────────────────────────────────────────────────
    gender_tag = "F" if is_female else "M"
    type_tag   = "Elder" if is_elder else ("Guard" if is_guard else "Villager")
    final_name = f"Villager_{gender_tag}_{type_tag}_{seed}"

    return join_all(parts, final_name)
