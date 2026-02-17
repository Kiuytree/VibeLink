bl_info = {
    "name": "VibeLink (Unity Bridge)",
    "author": "Antigravity",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > N-Panel > VibeLink",
    "description": "Connects Blender to Unity via WebSocket for procedural asset generation.",
    "warning": "",
    "doc_url": "",
    "category": "Development",
}

import bpy
import threading
from . import server

# Estado Global del Server
server_instance = None
server_thread = None

class VibeLinkPanel(bpy.types.Panel):
    """Creates a Panel in the 3D Viewport N-Panel"""
    bl_label = "VibeLink Control"
    bl_idname = "VIBELINK_PT_control"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "VibeLink"

    def draw(self, context):
        layout = self.layout

        global server_instance
        is_running = server_instance and server_instance.running

        # Info Server
        row = layout.row()
        row.label(text=f"Status: {'CONNECTED' if is_running else 'STOPPED'}", icon='CHECKMARK' if is_running else 'CANCEL')

        # Botones Start/Stop
        row = layout.row()
        if not is_running:
            row.operator("vibelink.start_server", text="Start Server", icon='PLAY')
        else:
            row.operator("vibelink.stop_server", text="Stop Server", icon='PAUSE')

        # Opciones
        layout.separator()
        layout.prop(context.scene, "vibelink_port")
        layout.prop(context.scene, "vibelink_host")

class START_OT_server(bpy.types.Operator):
    """Start the VibeLink WebSocket Client"""
    bl_idname = "vibelink.start_server"
    bl_label = "Start Server"

    def execute(self, context):
        global server_instance
        
        if server_instance and server_instance.running:
            self.report({'WARNING'}, "Server already running")
            return {'CANCELLED'}

        port = context.scene.vibelink_port
        host = context.scene.vibelink_host

        # Iniciar Instancia
        server_instance = server.UnityClient(host=host, port=port)
        server_instance.start() # Inicia el thread

        # Registrar Timer para procesar cola en Main Thread
        if not bpy.app.timers.is_registered(server.process_queue):
            bpy.app.timers.register(server.process_queue)
            
        self.report({'INFO'}, f"VibeLink started on {host}:{port}")
        return {'FINISHED'}

class STOP_OT_server(bpy.types.Operator):
    """Stop the VibeLink WebSocket Client"""
    bl_idname = "vibelink.stop_server"
    bl_label = "Stop Server"

    def execute(self, context):
        global server_instance
        
        if server_instance:
            server_instance.stop()
            server_instance = None
            
        if bpy.app.timers.is_registered(server.process_queue):
            bpy.app.timers.unregister(server.process_queue)
            
        self.report({'INFO'}, "VibeLink stopped")
        return {'FINISHED'}

# --- Registro ---
classes = (
    VibeLinkPanel,
    START_OT_server,
    STOP_OT_server,
)

def register():
    # Properties
    bpy.types.Scene.vibelink_port = bpy.props.IntProperty(
        name="Port",
        default=8085,
        min=1024,
        max=65535,
        description="Port for Unity WebSocket Server"
    )
    bpy.types.Scene.vibelink_host = bpy.props.StringProperty(
        name="Host",
        default="127.0.0.1",
        description="Host IP (usually localhost/127.0.0.1)"
    )

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    # Parar server si está corriendo al cerrar
    global server_instance
    if server_instance:
        server_instance.stop()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.vibelink_port
    del bpy.types.Scene.vibelink_host

if __name__ == "__main__":
    register()
