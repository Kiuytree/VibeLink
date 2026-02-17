import bpy
import bmesh
import random
import math
from mathutils import Vector, Matrix

def create_material(name, color):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
        mat.diffuse_color = color
    return mat

def add_icosphere(location, radius, subdivisions, material, name="Part"):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=radius, location=location)
    obj = bpy.context.active_object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    return obj

def add_cylinder(location, radius, depth, material, name="Part"):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=location)
    obj = bpy.context.active_object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    return obj

def distort_mesh(obj, strength=0.2):
    """Mueve vertices aleatoriamente para dar look organico"""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(obj.data)
    
    for v in bm.verts:
        offset = Vector((
            random.uniform(-1, 1),
            random.uniform(-1, 1),
            random.uniform(-1, 1)
        ))
        v.co += offset * strength
        
    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode='OBJECT')

def generate_tree(params):
    height = params.get("height", 4.0) + random.uniform(-0.5, 0.5)
    width = params.get("width", 1.5)
    
    mat_trunk = create_material("Mat_F_Wood", (0.35, 0.25, 0.15, 1.0))
    mat_leaves = create_material("Mat_F_Grass", (0.1, 0.6, 0.1, 1.0)) # Verde Bosque
    
    objects = []
    
    # 1. Tronco (Cilindro Low Poly)
    trunk_h = height * 0.4
    trunk = add_cylinder((0,0, trunk_h/2), width*0.3, trunk_h, mat_trunk, "Trunk")
    distort_mesh(trunk, 0.05) # Leve distorsión
    objects.append(trunk)
    
    # 2. Copa (Varias Icosferas)
    num_blobs = random.randint(3, 5)
    for i in range(num_blobs):
        # Posición relativa a la copa
        bx = random.uniform(-width/2, width/2)
        by = random.uniform(-width/2, width/2)
        bz = trunk_h + random.uniform(0, height - trunk_h)
        
        # Tamaño
        br = random.uniform(width*0.4, width*0.8)
        
        blob = add_icosphere((bx, by, bz), br, 1, mat_leaves, f"Leaves_{i}")
        distort_mesh(blob, 0.15) # Más irregular
        objects.append(blob)
        
    return objects

def generate_rock(params):
    size = params.get("scale", 1.0)
    mat_stone = create_material("Mat_F_Stone", (0.5, 0.5, 0.55, 1.0))
    
    # Empezar con un cubo subdividido o Icosfera
    # Icosfera nivel 1 es buena base para rocas low poly
    rock = add_icosphere((0,0,size/2), size/2, 1, mat_stone, "Rock_Base")
    
    # Escalar aleatoriamente en ejes para que no sea redonda
    rock.scale = (
        random.uniform(0.8, 1.2),
        random.uniform(0.8, 1.2),
        random.uniform(0.6, 1.0) # Aplatada
    )
    bpy.ops.object.transform_apply(scale=True)
    
    # Distorsión fuerte (Voronoi stylistic)
    distort_mesh(rock, strength=0.2 * size)
    
    # Decimate (opcional) para look más afilado? 
    # Mejor Shade Flat (ya es default)
    
    return [rock] # Lista para mantener consistencia

def generate(params):
    """
    Entry point.
    Params: type="tree"|"rock", seed, height/scale
    """
    seed = params.get("seed", 12345)
    random.seed(seed)
    
    gen_type = params.get("type", "tree") # default tree
    
    created_objects = []
    
    if gen_type == "rock":
        created_objects = generate_rock(params)
    else:
        created_objects = generate_tree(params)
        
    # Unir
    bpy.ops.object.select_all(action='DESELECT')
    for obj in created_objects:
        obj.select_set(True)
    
    bpy.context.view_layer.objects.active = created_objects[0]
    bpy.ops.object.join()
    
    final_obj = bpy.context.active_object
    final_obj.name = f"{gen_type.capitalize()}_{seed}"
    
    # Reset Origin
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN') 
    
    return final_obj
