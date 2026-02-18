import bpy
import bmesh
import random
import math
from mathutils import Vector

# ─────────────────────────────────────────────
#  MATERIALS
# ─────────────────────────────────────────────
def mat(name, color):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name=name)
        m.diffuse_color = color
    return m

# ─────────────────────────────────────────────
#  MESH HELPERS
# ─────────────────────────────────────────────
def add_box(name, loc, scale, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    if material:
        if len(obj.data.materials) == 0:
            obj.data.materials.append(material)
        else:
            obj.data.materials[0] = material
    return obj

def add_sphere(name, loc, radius, material):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=radius, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    if material:
        if len(obj.data.materials) == 0:
            obj.data.materials.append(material)
        else:
            obj.data.materials[0] = material
    return obj

# ─────────────────────────────────────────────
#  ARMATURE BUILDER
# ─────────────────────────────────────────────
def build_armature(name, bone_defs):
    """
    bone_defs: list of (bone_name, head_pos, tail_pos, parent_name|None)
    Returns the armature object.
    """
    arm_data = bpy.data.armatures.new(name + "_Armature")
    arm_obj  = bpy.data.objects.new(name, arm_data)
    bpy.context.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    arm_obj.select_set(True)

    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = arm_data.edit_bones

    created = {}
    for (bname, head, tail, parent) in bone_defs:
        b = edit_bones.new(bname)
        b.head = Vector(head)
        b.tail = Vector(tail)
        if parent and parent in created:
            b.parent = created[parent]
            b.use_connect = False
        created[bname] = b

    bpy.ops.object.mode_set(mode='OBJECT')
    return arm_obj

# ─────────────────────────────────────────────
#  MAIN GENERATE
# ─────────────────────────────────────────────
def generate(params):
    seed   = params.get("seed", 42)
    random.seed(seed)

    style = params.get("style", "villager")  # villager | guard | elder

    height_mult = {"villager": 1.0, "guard": 1.15, "elder": 0.9}.get(style, 1.0)
    bulk_mult   = {"villager": 1.0, "guard": 1.3,  "elder": 0.85}.get(style, 1.0)

    # ── Materials ──────────────────────────────
    mat_skin  = mat("Mat_F_Skin",  (
        random.uniform(0.6, 0.9),
        random.uniform(0.4, 0.7),
        random.uniform(0.3, 0.5), 1.0))
    cloth_h   = random.uniform(0, 1)
    mat_cloth = mat("Mat_F_Cloth", (
        0.2 + cloth_h * 0.5,
        0.2 + (1 - cloth_h) * 0.4,
        0.3, 1.0))
    mat_hair  = mat("Mat_F_Wood",  (
        0.25 + random.uniform(0, 0.3),
        0.15 + random.uniform(0, 0.1),
        0.05, 1.0))

    # ── Proportions ────────────────────────────
    H          = 1.8 * height_mult
    foot_z     = 0.0
    knee_z     = H * 0.27
    hip_z      = H * 0.52
    waist_z    = H * 0.60
    chest_z    = H * 0.72
    shoulder_z = H * 0.80
    neck_z     = H * 0.87
    head_z     = H * 0.93

    leg_w   = 0.13 * bulk_mult
    torso_w = 0.22 * bulk_mult
    arm_w   = 0.09 * bulk_mult
    head_r  = 0.14 * height_mult

    elbow_z = shoulder_z - (shoulder_z - waist_z) * 0.55
    wrist_z = elbow_z    - (shoulder_z - waist_z) * 0.45
    arm_x_l = -(torso_w * 0.5 + arm_w * 0.5)
    arm_x_r =  (torso_w * 0.5 + arm_w * 0.5)

    # ── Build mesh parts with bone assignment tag ──
    # Each tuple: (obj, bone_name)
    tagged_parts = []

    def part(obj, bone):
        tagged_parts.append((obj, bone))
        return obj

    part(add_sphere("Head",       (0, 0, head_z + head_r * 0.5),  head_r,                                  mat_skin),  "Head")
    part(add_box("Hair",          (0, 0, head_z + head_r * 1.1),  (head_r*1.1, head_r*1.1, head_r*0.35),  mat_hair),  "Head")
    part(add_box("Neck",          (0, 0, (neck_z+head_z)*0.5),    (0.07*bulk_mult, 0.07*bulk_mult, head_z-neck_z), mat_skin), "Neck")
    part(add_box("Torso",         (0, 0, (chest_z+waist_z)*0.5),  (torso_w, torso_w*0.7, chest_z-waist_z+0.05),   mat_cloth), "Chest")
    part(add_box("Hips_Mesh",     (0, 0, (hip_z+waist_z)*0.5),   (torso_w*0.9, torso_w*0.65, waist_z-hip_z),      mat_cloth), "Hips")

    for side, sx, bone_pre in [("L", -1, "Left"), ("R", 1, "Right")]:
        x = sx * leg_w * 0.9
        part(add_box(f"UpperLeg_{side}", (x, 0, (hip_z+knee_z)*0.5),       (leg_w,      leg_w,      hip_z-knee_z),  mat_cloth), f"{bone_pre}UpperLeg")
        part(add_box(f"LowerLeg_{side}", (x, 0, (knee_z+foot_z)*0.5+0.05), (leg_w*0.85, leg_w*0.85, knee_z-foot_z), mat_skin),  f"{bone_pre}LowerLeg")
        part(add_box(f"Foot_{side}",     (x, leg_w*0.4, foot_z+0.03),      (leg_w*0.9,  leg_w*1.6,  0.06),          mat_cloth), f"{bone_pre}Foot")

        ax = arm_x_l if sx == -1 else arm_x_r
        part(add_box(f"UpperArm_{side}", (ax, 0, (shoulder_z+elbow_z)*0.5), (arm_w,      arm_w,      shoulder_z-elbow_z), mat_cloth), f"{bone_pre}UpperArm")
        part(add_box(f"LowerArm_{side}", (ax, 0, (elbow_z+wrist_z)*0.5),    (arm_w*0.85, arm_w*0.85, elbow_z-wrist_z),   mat_skin),  f"{bone_pre}LowerArm")
        part(add_box(f"Hand_{side}",     (ax, 0, wrist_z-0.04),             (arm_w*0.9,  arm_w*1.2,  0.08),               mat_skin),  f"{bone_pre}Hand")

    # ── Step 1: Join all meshes into ONE object ──
    bpy.ops.object.select_all(action='DESELECT')
    objs = [p[0] for p in tagged_parts]
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    mesh_obj = bpy.context.active_object
    mesh_obj.name = f"Humanoid_{style}_{seed}_Mesh"

    # ── Step 2: Build armature ──────────────────
    bone_defs = [
        ("Hips",        (0, 0, hip_z),      (0, 0, waist_z),    None),
        ("Spine",       (0, 0, waist_z),    (0, 0, chest_z),    "Hips"),
        ("Chest",       (0, 0, chest_z),    (0, 0, neck_z),     "Spine"),
        ("Neck",        (0, 0, neck_z),     (0, 0, head_z),     "Chest"),
        ("Head",        (0, 0, head_z),     (0, 0, head_z+head_r*2), "Neck"),

        ("LeftUpperLeg",  (-leg_w*0.9, 0, hip_z),        (-leg_w*0.9, 0, knee_z),       "Hips"),
        ("LeftLowerLeg",  (-leg_w*0.9, 0, knee_z),       (-leg_w*0.9, 0, foot_z+0.05),  "LeftUpperLeg"),
        ("LeftFoot",      (-leg_w*0.9, 0, foot_z+0.05),  (-leg_w*0.9, leg_w*1.6, 0),    "LeftLowerLeg"),

        ("RightUpperLeg", (leg_w*0.9, 0, hip_z),         (leg_w*0.9, 0, knee_z),        "Hips"),
        ("RightLowerLeg", (leg_w*0.9, 0, knee_z),        (leg_w*0.9, 0, foot_z+0.05),   "RightUpperLeg"),
        ("RightFoot",     (leg_w*0.9, 0, foot_z+0.05),   (leg_w*0.9, leg_w*1.6, 0),     "RightLowerLeg"),

        ("LeftShoulder",  (arm_x_l+arm_w*0.5, 0, shoulder_z), (arm_x_l, 0, shoulder_z), "Chest"),
        ("LeftUpperArm",  (arm_x_l, 0, shoulder_z),  (arm_x_l, 0, elbow_z),  "LeftShoulder"),
        ("LeftLowerArm",  (arm_x_l, 0, elbow_z),     (arm_x_l, 0, wrist_z),  "LeftUpperArm"),
        ("LeftHand",      (arm_x_l, 0, wrist_z),     (arm_x_l, 0, wrist_z-0.08), "LeftLowerArm"),

        ("RightShoulder", (arm_x_r-arm_w*0.5, 0, shoulder_z), (arm_x_r, 0, shoulder_z), "Chest"),
        ("RightUpperArm", (arm_x_r, 0, shoulder_z), (arm_x_r, 0, elbow_z),  "RightShoulder"),
        ("RightLowerArm", (arm_x_r, 0, elbow_z),    (arm_x_r, 0, wrist_z),  "RightUpperArm"),
        ("RightHand",     (arm_x_r, 0, wrist_z),    (arm_x_r, 0, wrist_z-0.08), "RightLowerArm"),
    ]

    arm_obj = build_armature(f"Humanoid_{style}_{seed}", bone_defs)

    # ── Step 3: Parent mesh to armature ─────────
    # Use "Armature Deform with Empty Groups" so we control weights manually
    bpy.ops.object.select_all(action='DESELECT')
    mesh_obj.select_set(True)
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.parent_set(type='ARMATURE_NAME')  # Creates vertex groups automatically named after bones

    # ── Step 4: Assign vertex weights by position ─
    # Since join() merged everything, we assign weights based on vertex Z position
    # This is simpler and more robust than tracking individual objects
    bpy.context.view_layer.objects.active = mesh_obj
    bpy.ops.object.mode_set(mode='OBJECT')

    # Clear all vertex groups first (parent_set may have created empty ones)
    mesh_obj.vertex_groups.clear()

    # Bone → vertex group mapping by spatial region
    # Each vertex gets assigned to the nearest bone region
    bone_regions = [
        # (group_name, x_min, x_max, z_min, z_max)
        ("Head",          -1,  1,   head_z,        head_z + head_r*2.5),
        ("Neck",          -1,  1,   neck_z,        head_z),
        ("Chest",         -1,  1,   chest_z,       neck_z),
        ("Spine",         -1,  1,   waist_z,       chest_z),
        ("Hips",          -1,  1,   hip_z,         waist_z),

        ("LeftUpperLeg",  -1,  0,   knee_z,        hip_z),
        ("LeftLowerLeg",  -1,  0,   foot_z,        knee_z),
        ("LeftFoot",      -1,  0,   -0.1,          foot_z + 0.08),

        ("RightUpperLeg",  0,  1,   knee_z,        hip_z),
        ("RightLowerLeg",  0,  1,   foot_z,        knee_z),
        ("RightFoot",      0,  1,   -0.1,          foot_z + 0.08),

        ("LeftUpperArm",  arm_x_l-arm_w, arm_x_l+arm_w*0.5, elbow_z, shoulder_z+0.05),
        ("LeftLowerArm",  arm_x_l-arm_w, arm_x_l+arm_w*0.5, wrist_z, elbow_z),
        ("LeftHand",      arm_x_l-arm_w, arm_x_l+arm_w*0.5, wrist_z-0.12, wrist_z),

        ("RightUpperArm", arm_x_r-arm_w*0.5, arm_x_r+arm_w, elbow_z, shoulder_z+0.05),
        ("RightLowerArm", arm_x_r-arm_w*0.5, arm_x_r+arm_w, wrist_z, elbow_z),
        ("RightHand",     arm_x_r-arm_w*0.5, arm_x_r+arm_w, wrist_z-0.12, wrist_z),
    ]

    # Create all vertex groups
    vgroups = {}
    for (gname, *_) in bone_regions:
        if gname not in vgroups:
            vgroups[gname] = mesh_obj.vertex_groups.new(name=gname)

    # Assign each vertex to the best matching region
    verts = mesh_obj.data.vertices
    for v in verts:
        x, y, z = v.co.x, v.co.y, v.co.z
        assigned = False
        for (gname, xmin, xmax, zmin, zmax) in bone_regions:
            if xmin <= x <= xmax and zmin <= z <= zmax:
                vgroups[gname].add([v.index], 1.0, 'REPLACE')
                assigned = True
                break
        if not assigned:
            # Fallback: assign to Hips
            vgroups["Hips"].add([v.index], 1.0, 'REPLACE')

    # ── Step 5: Add armature modifier to mesh ───
    mod = mesh_obj.modifiers.new("Armature", 'ARMATURE')
    mod.object = arm_obj

    # ── Step 6: Select armature as export root ──
    # The armature contains the mesh as child
    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    mesh_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj

    return arm_obj
