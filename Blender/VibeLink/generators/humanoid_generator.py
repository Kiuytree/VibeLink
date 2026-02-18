import bpy
import bmesh
import random
import math
from mathutils import Vector, Matrix

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
    obj.data.materials.append(material)
    return obj

def add_sphere(name, loc, radius, material):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=radius, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(material)
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
    arm_obj  = bpy.data.objects.new(name + "_Rig", arm_data)
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
#  SKIN MESH TO ARMATURE
# ─────────────────────────────────────────────
def skin_to_armature(mesh_objs, arm_obj, bone_weights):
    """
    bone_weights: dict { mesh_obj_name: bone_name }
    Each mesh part gets 100% weight to its corresponding bone.
    """
    for obj in mesh_objs:
        # Parent to armature
        obj.parent = arm_obj
        # Add Armature modifier
        mod = obj.modifiers.new("Armature", 'ARMATURE')
        mod.object = arm_obj
        # Create vertex group for the bone
        bone_name = bone_weights.get(obj.name, "Hips")
        vg = obj.vertex_groups.new(name=bone_name)
        # All vertices get full weight
        vg.add(list(range(len(obj.data.vertices))), 1.0, 'REPLACE')

# ─────────────────────────────────────────────
#  MAIN GENERATE
# ─────────────────────────────────────────────
def generate(params):
    seed   = params.get("seed", 42)
    random.seed(seed)

    # Style variation
    style = params.get("style", "villager")  # villager | guard | elder

    # Scale variation per style
    height_mult = {"villager": 1.0, "guard": 1.15, "elder": 0.9}.get(style, 1.0)
    bulk_mult   = {"villager": 1.0, "guard": 1.3,  "elder": 0.85}.get(style, 1.0)

    # ── Materials ──────────────────────────────
    skin_color  = (
        random.uniform(0.6, 0.9),
        random.uniform(0.4, 0.7),
        random.uniform(0.3, 0.5),
        1.0
    )
    cloth_h = random.uniform(0, 1)
    cloth_color = (
        0.2 + cloth_h * 0.5,
        0.2 + (1 - cloth_h) * 0.4,
        0.3,
        1.0
    )

    mat_skin  = mat("Mat_F_Skin",  skin_color)
    mat_cloth = mat("Mat_F_Cloth", cloth_color)
    mat_hair  = mat("Mat_F_Wood",  (0.25 + random.uniform(0,0.3),
                                    0.15 + random.uniform(0,0.1),
                                    0.05, 1.0))

    # ── Proportions ────────────────────────────
    H  = 1.8 * height_mult   # Total height
    # Key heights (from ground)
    foot_z   = 0.0
    knee_z   = H * 0.27
    hip_z    = H * 0.52
    waist_z  = H * 0.60
    chest_z  = H * 0.72
    shoulder_z = H * 0.80
    neck_z   = H * 0.87
    head_z   = H * 0.93

    leg_w    = 0.13 * bulk_mult
    torso_w  = 0.22 * bulk_mult
    arm_w    = 0.09 * bulk_mult
    head_r   = 0.14 * height_mult

    # ── Mesh Parts ─────────────────────────────
    parts = []

    # Head
    head = add_sphere("Head", (0, 0, head_z + head_r * 0.5), head_r, mat_skin)
    parts.append(head)

    # Hair (flat box on top)
    hair = add_box("Hair", (0, 0, head_z + head_r * 1.1),
                   (head_r * 1.1, head_r * 1.1, head_r * 0.35), mat_hair)
    parts.append(hair)

    # Neck
    neck = add_box("Neck", (0, 0, (neck_z + head_z) * 0.5),
                   (0.07 * bulk_mult, 0.07 * bulk_mult, head_z - neck_z), mat_skin)
    parts.append(neck)

    # Torso (chest + waist as one box)
    torso = add_box("Torso", (0, 0, (chest_z + waist_z) * 0.5),
                    (torso_w, torso_w * 0.7, chest_z - waist_z + 0.05), mat_cloth)
    parts.append(torso)

    # Hips
    hips = add_box("Hips_Mesh", (0, 0, (hip_z + waist_z) * 0.5),
                   (torso_w * 0.9, torso_w * 0.65, waist_z - hip_z), mat_cloth)
    parts.append(hips)

    # Upper Legs
    for side, sx in [("L", -1), ("R", 1)]:
        x = sx * leg_w * 0.9
        ul = add_box(f"UpperLeg_{side}",
                     (x, 0, (hip_z + knee_z) * 0.5),
                     (leg_w, leg_w, hip_z - knee_z), mat_cloth)
        parts.append(ul)

        # Lower Legs
        ll = add_box(f"LowerLeg_{side}",
                     (x, 0, (knee_z + foot_z) * 0.5 + 0.05),
                     (leg_w * 0.85, leg_w * 0.85, knee_z - foot_z), mat_skin)
        parts.append(ll)

        # Feet
        ft = add_box(f"Foot_{side}",
                     (x, leg_w * 0.4, foot_z + 0.03),
                     (leg_w * 0.9, leg_w * 1.6, 0.06), mat_cloth)
        parts.append(ft)

    # Upper Arms
    for side, sx in [("L", -1), ("R", 1)]:
        x = sx * (torso_w * 0.5 + arm_w * 0.5)
        elbow_z = shoulder_z - (shoulder_z - waist_z) * 0.55
        wrist_z = elbow_z - (shoulder_z - waist_z) * 0.45

        ua = add_box(f"UpperArm_{side}",
                     (x, 0, (shoulder_z + elbow_z) * 0.5),
                     (arm_w, arm_w, shoulder_z - elbow_z), mat_cloth)
        parts.append(ua)

        la = add_box(f"LowerArm_{side}",
                     (x, 0, (elbow_z + wrist_z) * 0.5),
                     (arm_w * 0.85, arm_w * 0.85, elbow_z - wrist_z), mat_skin)
        parts.append(la)

        # Hand
        hand = add_box(f"Hand_{side}",
                       (x, 0, wrist_z - 0.04),
                       (arm_w * 0.9, arm_w * 1.2, 0.08), mat_skin)
        parts.append(hand)

    # ── Armature ───────────────────────────────
    # Bone definitions: (name, head, tail, parent)
    # Using Unity Humanoid naming convention
    bone_defs = [
        ("Hips",        (0, 0, hip_z),      (0, 0, waist_z),    None),
        ("Spine",       (0, 0, waist_z),    (0, 0, chest_z),    "Hips"),
        ("Chest",       (0, 0, chest_z),    (0, 0, neck_z),     "Spine"),
        ("Neck",        (0, 0, neck_z),     (0, 0, head_z),     "Chest"),
        ("Head",        (0, 0, head_z),     (0, 0, head_z + head_r * 2), "Neck"),

        # Left leg
        ("LeftUpperLeg",  (-leg_w*0.9, 0, hip_z),   (-leg_w*0.9, 0, knee_z),  "Hips"),
        ("LeftLowerLeg",  (-leg_w*0.9, 0, knee_z),  (-leg_w*0.9, 0, foot_z+0.05), "LeftUpperLeg"),
        ("LeftFoot",      (-leg_w*0.9, 0, foot_z+0.05), (-leg_w*0.9, leg_w*1.6, 0), "LeftLowerLeg"),

        # Right leg
        ("RightUpperLeg", (leg_w*0.9, 0, hip_z),    (leg_w*0.9, 0, knee_z),   "Hips"),
        ("RightLowerLeg", (leg_w*0.9, 0, knee_z),   (leg_w*0.9, 0, foot_z+0.05), "RightUpperLeg"),
        ("RightFoot",     (leg_w*0.9, 0, foot_z+0.05), (leg_w*0.9, leg_w*1.6, 0), "RightLowerLeg"),

        # Left arm
        ("LeftShoulder",  (-(torso_w*0.5), 0, shoulder_z), (-(torso_w*0.5+arm_w*0.5), 0, shoulder_z), "Chest"),
        ("LeftUpperArm",  (-(torso_w*0.5+arm_w*0.5), 0, shoulder_z),
                          (-(torso_w*0.5+arm_w*0.5), 0, shoulder_z - (shoulder_z-waist_z)*0.55), "LeftShoulder"),
        ("LeftLowerArm",  (-(torso_w*0.5+arm_w*0.5), 0, shoulder_z - (shoulder_z-waist_z)*0.55),
                          (-(torso_w*0.5+arm_w*0.5), 0, shoulder_z - (shoulder_z-waist_z)*1.0), "LeftUpperArm"),
        ("LeftHand",      (-(torso_w*0.5+arm_w*0.5), 0, shoulder_z - (shoulder_z-waist_z)*1.0),
                          (-(torso_w*0.5+arm_w*0.5), 0, shoulder_z - (shoulder_z-waist_z)*1.15), "LeftLowerArm"),

        # Right arm
        ("RightShoulder", (torso_w*0.5, 0, shoulder_z), (torso_w*0.5+arm_w*0.5, 0, shoulder_z), "Chest"),
        ("RightUpperArm", (torso_w*0.5+arm_w*0.5, 0, shoulder_z),
                          (torso_w*0.5+arm_w*0.5, 0, shoulder_z - (shoulder_z-waist_z)*0.55), "RightShoulder"),
        ("RightLowerArm", (torso_w*0.5+arm_w*0.5, 0, shoulder_z - (shoulder_z-waist_z)*0.55),
                          (torso_w*0.5+arm_w*0.5, 0, shoulder_z - (shoulder_z-waist_z)*1.0), "RightUpperArm"),
        ("RightHand",     (torso_w*0.5+arm_w*0.5, 0, shoulder_z - (shoulder_z-waist_z)*1.0),
                          (torso_w*0.5+arm_w*0.5, 0, shoulder_z - (shoulder_z-waist_z)*1.15), "RightUpperArm"),
    ]

    arm_obj = build_armature(f"Humanoid_{seed}", bone_defs)

    # ── Bone → Mesh mapping ────────────────────
    bone_weights = {
        "Head":           "Head",
        "Hair":           "Head",
        "Neck":           "Neck",
        "Torso":          "Chest",
        "Hips_Mesh":      "Hips",
        "UpperLeg_L":     "LeftUpperLeg",
        "LowerLeg_L":     "LeftLowerLeg",
        "Foot_L":         "LeftFoot",
        "UpperLeg_R":     "RightUpperLeg",
        "LowerLeg_R":     "RightLowerLeg",
        "Foot_R":         "RightFoot",
        "UpperArm_L":     "LeftUpperArm",
        "LowerArm_L":     "LeftLowerArm",
        "Hand_L":         "LeftHand",
        "UpperArm_R":     "RightUpperArm",
        "LowerArm_R":     "RightLowerArm",
        "Hand_R":         "RightHand",
    }

    skin_to_armature(parts, arm_obj, bone_weights)

    # ── Join all meshes into one ───────────────
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    mesh_obj = bpy.context.active_object
    mesh_obj.name = f"Humanoid_{style}_{seed}"

    # Re-parent joined mesh to armature
    mesh_obj.parent = arm_obj
    mod = mesh_obj.modifiers.new("Armature", 'ARMATURE')
    mod.object = arm_obj

    # ── Name the armature ──────────────────────
    arm_obj.name = f"Humanoid_{style}_{seed}_Rig"

    return arm_obj  # Return armature as root (contains mesh as child)
