import bpy
import bmesh
import random
import math

def create_material(name, color):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
        mat.diffuse_color = color
    return mat

def add_cube(location, scale, material, name="Part"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    # Aplicar escala es vital para que las transformaciones posteriores (bevel, UV) funcionen bien
    bpy.ops.object.transform_apply(scale=True)
    
    if material:
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)
    return obj

def generate(params):
    """
    Generador de Casas Low Poly v2 (Arquitectónico)
    """
    # 1. Parámetros y Semilla
    level = params.get("level", 1)
    seed = params.get("seed", 12345)
    base_width = params.get("width", 5.0)
    base_depth = params.get("depth", 5.0)
    
    random.seed(seed)
    
    # Variación aleatoria sutil
    width = base_width + random.uniform(-0.5, 0.5)
    depth = base_depth + random.uniform(-0.5, 0.5)
    floor_height = 3.2
    
    # 2. Materiales (Paleta de Colores Unity)
    mat_walls = create_material("Mat_F_Walls", (0.85, 0.82, 0.75, 1.0)) # Stucco
    mat_wood = create_material("Mat_F_Wood", (0.35, 0.25, 0.15, 1.0))   # Vigas
    mat_roof = create_material("Mat_F_Roof", (0.6, 0.2, 0.15, 1.0))     # Teja
    mat_door = create_material("Mat_F_Door", (0.25, 0.15, 0.1, 1.0))    # Madera Oscura
    mat_window = create_material("Mat_F_Window", (0.2, 0.7, 0.9, 1.0))  # Cristal Azul
    mat_stone = create_material("Mat_F_Stone", (0.5, 0.5, 0.55, 1.0))   # Base Piedra

    objects = []
    
    # === ESTRUCTURA PRINCIPAL ===
    current_z = 0
    levels_to_build = level
    
    for lvl in range(levels_to_build):
        is_ground = (lvl == 0)
        
        # Ajuste de tamaño por planta (Planta 2 a veces es más grande "voladizo" o más pequeña)
        lvl_w = width + (0.4 if lvl > 0 else 0)
        lvl_d = depth + (0.4 if lvl > 0 else 0)
        
        center_z = current_z + (floor_height / 2)
        
        # A. Vigas Esquineras (Pillars) - Dan la silueta fuerte
        pillar_size = 0.45 # Un poco más gruesos
        half_w = (lvl_w / 2) - (pillar_size / 2)
        half_d = (lvl_d / 2) - (pillar_size / 2)
        
        corners = [
            (-half_w, -half_d), (half_w, -half_d),
            (-half_w, half_d), (half_w, half_d)
        ]
        
        for cx, cy in corners:
            p = add_cube((cx, cy, center_z), (pillar_size, pillar_size, floor_height), mat_wood, f"Pillar_L{lvl}")
            objects.append(p)
            
        # B. Paredes (Retranqueadas hacia adentro para dar relieve a las vigas)
        wall_inset = 0.15
        wall_padding = 0.12 # Cuánto se mete la pared hacia dentro respecto al pilar
        
        # Calcular posición para que queden metidas
        # Frente: Y negativo.
        y_front = -(lvl_d/2 - wall_padding - wall_inset/2)
        w_front = add_cube((0, y_front, center_z), (lvl_w - pillar_size, wall_inset, floor_height), mat_walls, f"Wall_Front_L{lvl}")
        objects.append(w_front)
        
        y_back = (lvl_d/2 - wall_padding - wall_inset/2)
        w_back = add_cube((0, y_back, center_z), (lvl_w - pillar_size, wall_inset, floor_height), mat_walls, f"Wall_Back_L{lvl}")
        objects.append(w_back)
        
        # Paredes Laterales
        x_left = -(lvl_w/2 - wall_padding - wall_inset/2)
        w_left = add_cube((x_left, 0, center_z), (wall_inset, lvl_d - pillar_size, floor_height), mat_walls, f"Wall_Left_L{lvl}")
        objects.append(w_left)
        
        x_right = (lvl_w/2 - wall_padding - wall_inset/2)
        w_right = add_cube((x_right, 0, center_z), (wall_inset, lvl_d - pillar_size, floor_height), mat_walls, f"Wall_Right_L{lvl}")
        objects.append(w_right)
        
        # C. Suelo/Techo entre plantas (Viga perimetral)
        if lvl > 0:
            beam_h = 0.4
            # La viga sobresale un poco de las paredes pero menos que los pilares
            beam_trim = add_cube((0, 0, current_z), (lvl_w - 0.1, lvl_d - 0.1, beam_h), mat_wood, f"Trim_L{lvl}")
            objects.append(beam_trim)

        # D. Detalles Planta Baja (Puerta)
        if is_ground:
            # Ajustar posición puerta al nuevo muro retranqueado
            door_y = y_front - wall_inset/2
            
            door_w = 1.2
            door_h = 2.2
            
            # Marco
            frame = add_cube((0, door_y, door_h/2), (door_w + 0.3, 0.3, door_h + 0.15), mat_wood, "DoorFrame")
            objects.append(frame)
            # Hoja
            door = add_cube((0, door_y - 0.05, door_h/2), (door_w, 0.15, door_h), mat_door, "DoorBlade")
            objects.append(door)
            
            # Escalón de piedra
            step = add_cube((0, door_y - 0.4, 0.15), (door_w + 0.6, 0.5, 0.3), mat_stone, "DoorStep")
            objects.append(step)

        # E. Ventanas (Aleatorias pero simétricas)
        if random.random() > 0.3:
            win_h = 1.2
            win_w = 1.0
            win_z = current_z + 1.8 
            
            # Ajustar posición ventanas a muros laterales retranqueados
            win_x_left = x_left - wall_inset/2
            win_x_right = x_right + wall_inset/2
            
            # Izquierda
            win_l = add_cube((win_x_left, 0, win_z), (0.25, win_w, win_h), mat_wood, "WindowFrame_L")
            glass_l = add_cube((win_x_left - 0.05, 0, win_z), (0.1, win_w - 0.2, win_h - 0.2), mat_window, "WindowGlass_L")
            objects.append(win_l)
            objects.append(glass_l)
            # Derecha
            win_r = add_cube((win_x_right, 0, win_z), (0.25, win_w, win_h), mat_wood, "WindowFrame_R")
            glass_r = add_cube((win_x_right + 0.05, 0, win_z), (0.1, win_w - 0.2, win_h - 0.2), mat_window, "WindowGlass_R")
            objects.append(win_r)
            objects.append(glass_r)

        # F. BALCON (Solo Nivel 3 en adelante, en planta 2)
        if lvl == 1 and level >= 3:
            # Balcón frontal (Simplificado)
            balc_d = 0.8
            balc_w = 2.0
            balc_z = center_z - floor_height/2 + 0.2
            y_balc = y_front - balc_d/2 - 0.1
            
            floor_b = add_cube((0, y_balc, balc_z), (balc_w, balc_d, 0.2), mat_wood, "Balcony_Floor")
            objects.append(floor_b)
            # Barandilla
            rail = add_cube((0, y_balc - balc_d/2, balc_z + 0.5), (balc_w, 0.1, 0.8), mat_wood, "Balcony_Rail")
            objects.append(rail)
        
        current_z += floor_height

    # === ALA LATERAL (SIDE WING) - Nivel 4+ ===
    if level >= 4:
        wing_w = 4.0
        wing_d = 3.0
        wing_h = floor_height
        # Pegada a la derecha
        wx = width/2 + wing_w/2 - 0.2 
        wy = -depth/4 
        
        wing_walls = add_cube((wx, wy, wing_h/2), (wing_w, wing_d, wing_h), mat_walls, "Wing_Walls")
        objects.append(wing_walls)
        
        # Tejado Ala
        w_roof = add_cube((wx, wy, wing_h + 0.2), (wing_w + 0.4, wing_d + 0.4, 0.4), mat_roof, "Wing_Roof")
        objects.append(w_roof)

    # === TORRE (TOWER) - Nivel 5 ===
    if level >= 5:
        tow_w = 2.5
        tow_d = 2.5
        tow_h = floor_height * 2.5 # Alta
        # Esquina trasera izquierda
        tx = -width/2 - tow_w/2 + 0.5
        ty = depth/2 + tow_d/2 - 0.5
        
        tower = add_cube((tx, ty, tow_h/2), (tow_w, tow_d, tow_h), mat_walls, "Tower_Body")
        objects.append(tower)
        
        # Techo Torre
        t_roof = add_cube((tx, ty, tow_h + 1.0), (tow_w+0.6, tow_d+0.6, 2.0), mat_roof, "Tower_Roof")
        objects.append(t_roof)

    # === TEJADO GABLE (Triangular Prism Explicito) ===
    # Método infalible: Crear malla vértice a vértice
    roof_h = 2.5
    overhang = 0.6
    
    # Dimensiones totales del tejado
    rw = width + overhang * 2
    rd = depth + overhang * 2
    
    # Altura base y pico
    z_base = current_z
    z_peak = current_z + roof_h
    
    # Coordenadas (Centradas en 0,0)
    # Gable mirando al frente (Eje Y es profundidad)
    # Triangulo visible en cara Frontal (-Y) y Trasera (+Y)
    # Cumbrera a lo largo de Y? No, cumbrera a lo largo de X (Izquierda a Derecha)
    
    # Opción A: Cumbrera Side-to-Side (Eje X). Triangulos en caras Left/Right.
    # Casa normal: Entrada al frente. Tejado cae hacia frente y atras? O hacia lados?
    # Lo más bonito es Gable Frontal (Triangulo encima de la puerta).
    # Entonces Cumbrera va Back-to-Front (Eje Y).
    
    # Vamos a hacer Cumbrera a lo largo del eje Y (Profundidad).
    # Vertices Base: 4 esquinas
    # Vertices Pico: 2 puntos (Front y Back)
    
    # Coordenadas Base
    x0 = -rw/2
    x1 = rw/2
    y0 = -rd/2
    y1 = rd/2
    
    mesh = bpy.data.meshes.new("RoofMesh")
    roof_obj = bpy.data.objects.new("Roof_Main", mesh)
    bpy.context.collection.objects.link(roof_obj)
    
    bm = bmesh.new()
    
    # Vertices
    # Base (Rectangulo en altura Z_BASE)
    v_fl = bm.verts.new((x0, y0, z_base)) # Front-Left
    v_fr = bm.verts.new((x1, y0, z_base)) # Front-Right
    v_br = bm.verts.new((x1, y1, z_base)) # Back-Right
    v_bl = bm.verts.new((x0, y1, z_base)) # Back-Left
    
    # Pico (Cumbrera a lo largo de eje Y, en X=0)
    # Front Peak
    v_fp = bm.verts.new((0, y0, z_peak))
    # Back Peak
    v_bp = bm.verts.new((0, y1, z_peak))
    
    bm.verts.ensure_lookup_table()
    
    # Caras
    # Triangulo Frontal
    bm.faces.new((v_fl, v_fr, v_fp))
    # Triangulo Trasero
    bm.faces.new((v_br, v_bl, v_bp))
    # Pendiente Izquierda
    bm.faces.new((v_bl, v_fl, v_fp, v_bp))
    # Pendiente Derecha
    bm.faces.new((v_fr, v_br, v_bp, v_fp))
    # Base (Suelo del tejado, opcional pero bueno para cerrar)
    bm.faces.new((v_fl, v_bl, v_br, v_fr))
    
    bm.to_mesh(mesh)
    bm.free()
    
    # Asignar material
    if roof_obj.data.materials: roof_obj.data.materials[0] = mat_roof
    else: roof_obj.data.materials.append(mat_roof)
    
    objects.append(roof_obj)
    
    # Chillenea (Chimney) si Level >= 2
    if level >= 2:
        ch_w = 0.8
        ch_h = roof_h + 1.0
        chimney = add_cube((width/3, depth/4, current_z + ch_h/2 - 0.5), (ch_w, ch_w, ch_h), mat_stone, "Chimney")
        objects.append(chimney)

    # === FINALIZAR ===
    # Unir todo en un solo objeto FBX limpio
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)
    
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    
    final_obj = bpy.context.active_object
    final_obj.name = f"House_Generated_L{level}"
    
    # Reset Origin to bottom center (0,0,0) helps Unity placement
    # El origen ya debería estar bien porque construimos desde Z=0 hacia arriba
    # Pero por si acaso:
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN') 
    # (Asumiendo cursor en 0,0,0)
    
    return final_obj

