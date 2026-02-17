import bpy
import json
import threading
import queue
import time
import socket
import struct
import os

# Cola thread-safe para ejecutar en el Main Thread de Blender
execution_queue = queue.Queue()

GENERATED_PATH = "" # Se setea dinamicamente

def log(msg):
    print(f"[VibeLink] {msg}")

# --- WebSocket Client (Raw Socket implementation) ---
# Usamos socket puro porque no podemos garantizar que 'websockets' pip package esté instalado en Blender user.
class UnityClient:
    def __init__(self, host="127.0.0.1", port=8085):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.lock = threading.Lock()
        self.thread = None

    def start(self):
        if self.running: return
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.socket:
            try: self.socket.close() 
            except: pass
        if self.thread:
            self.thread.join(timeout=1.0)
        log("Client stopped")

    def _run_loop(self):
        while self.running:
            try:
                self._connect()
                self._listen()
            except Exception as e:
                log(f"Connection lost: {e}")
                time.sleep(2) # Reconnect delay

    def _connect(self):
        log(f"Connecting to ws://{self.host}:{self.port}...")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        
        # Handshake manual WebSocket (simplificado, si el server es estricto requerirá Sec-WebSocket-Key)
        # Para VibeLinkServer (TcpListener), basta con "GET / HTTP/1.1" y Upgrade headers.
        import base64
        key = base64.b64encode(os.urandom(16)).decode('utf-8')
        
        request = (
            f"GET / HTTP/1.1\r\n"
            f"Host: {self.host}:{self.port}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n"
            f"\r\n"
        )
        self.socket.send(request.encode())
        
        # Leer respuesta handshake
        response = self.socket.recv(4096)
        if b"101 Switching Protocols" in response:
            log("Connected!")
        else:
            raise Exception("Handshake failed")

    def _listen(self):
        while self.running:
            # Leer Frame Header (2 bytes minimos)
            header = self.socket.recv(2)
            if not header: break
            
            b1, b2 = header
            fin = b1 & 0x80
            opcode = b1 & 0x0F
            if opcode == 8: break # Close frame
            
            payload_len = b2 & 0x7F
            if payload_len == 126:
                payload_len = struct.unpack(">H", self.socket.recv(2))[0]
            elif payload_len == 127:
                payload_len = struct.unpack(">Q", self.socket.recv(8))[0]
            
            # Leer payload
            payload = b""
            while len(payload) < payload_len:
                chunk = self.socket.recv(payload_len - len(payload))
                if not chunk: break
                payload += chunk
                
            msg = payload.decode('utf-8')
            # Encolar para Main Thread
            execution_queue.put(msg)

    def send(self, data_str):
        # Enviar frame texto (0x81) sin mask (cliente -> server debe llevar mask segun RFC, pero VibeLinkServer puede ser permisivo)
        # Para cumplir RFC, hay que enmascarar.
        payload = data_str.encode('utf-8')
        length = len(payload)
        
        frame = bytearray([0x81])
        
        if length <= 125:
            frame.append(0x80 | length) # Mask bit set
        elif length <= 65535:
            frame.append(0x80 | 126)
            frame.extend(struct.pack(">H", length))
        else:
            frame.append(0x80 | 127)
            frame.extend(struct.pack(">Q", length))
            
        mask_key = os.urandom(4)
        frame.extend(mask_key)
        
        masked_payload = bytearray(length)
        for i in range(length):
            masked_payload[i] = payload[i] ^ mask_key[i % 4]
            
        frame.extend(masked_payload)
        
        try:
            with self.lock:
                self.socket.send(frame)
        except:
            pass

# --- Blender Main Thread Loop ---
# Esta función es llamada por el Timer de Blender (bpy.app.timers)
def process_queue():
    while not execution_queue.empty():
        msg = execution_queue.get()
        handle_message(msg)
    return 0.5 # Ejecutar cada 0.5 segundos

from .generators import house_generator
from .generators import nature_generator


def export_to_unity(obj, params, prefix="Object"):
    """
    Exporta un objeto de Blender a Unity como FBX.
    
    Args:
        obj: Objeto de Blender a exportar
        params: Diccionario con 'export_path', 'level', 'seed', 'style'
        prefix: Prefijo del archivo (ej: "House", "Tree", "Stone")
    
    Returns:
        str: Ruta completa del archivo exportado
    """
    # Resolver ruta de Unity (con persistencia)
    unity_assets_path = params.get("export_path", "")
    
    if unity_assets_path:
        bpy.context.scene["vibelink_last_path"] = unity_assets_path
    else:
        unity_assets_path = bpy.context.scene.get("vibelink_last_path", "")

    if not unity_assets_path:
        log("Warning: No 'export_path' provided and no history. Using temp.")
        import tempfile
        unity_assets_path = tempfile.gettempdir()
    
    # Construir ruta de exportación
    export_subpath = os.path.join("_Project", "Generated", "Models")
    export_dir = os.path.join(unity_assets_path, export_subpath)
    os.makedirs(export_dir, exist_ok=True)
    
    # Generar nombre de archivo
    lvl = params.get("level", 1)
    seed = params.get("seed", 0)
    style = params.get("style", "basic")
    filename = f"{prefix}_{style}_L{lvl}_{seed}.fbx"
    filepath = os.path.join(export_dir, filename)
    
    # Seleccionar solo el objeto a exportar
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    
    log(f"Exporting to: {filepath}")
    
    # Exportar con configuración optimizada
    bpy.ops.export_scene.fbx(
        filepath=filepath, 
        use_selection=True, 
        axis_forward='-Z', 
        axis_up='Y',
        apply_scale_options='FBX_SCALE_ALL',
        use_mesh_modifiers=True
    )
    
    log("Export Success!")
    return filepath

def handle_message(json_str):
    try:
        data = json.loads(json_str)
        cmd = data.get("cmd")
        
        if cmd == "generate_house":
            log(f"Generating House: {data}")
            
            # Limpiar escena (Factory Mode)
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete()
            
            # Parsear parámetros
            params = data.get("params", {})
            if "level" in data: params["level"] = data["level"]
            if "seed" in data: params["seed"] = data["seed"]

            # Generar y exportar
            house_obj = house_generator.generate(params)
            export_to_unity(house_obj, params, prefix="House")

        elif cmd == "generate_nature":
            log(f"Generating Nature: {data}")
            
            # Limpiar escena
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete()
            
            # Parsear parámetros
            params = data.get("params", {})
            if "seed" in data: params["seed"] = data["seed"]
            # type: "tree" or "rock"
            
            nature_obj = nature_generator.generate(params)
            
            # Prefix: "Tree" or "Rock"
            type_name = params.get("type", "nature").capitalize()
            export_to_unity(nature_obj, params, prefix=type_name)
            
    except Exception as e:
        log(f"Error processing: {e}")
        import traceback
        traceback.print_exc()
