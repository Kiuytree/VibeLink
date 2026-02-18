using UnityEditor;
using UnityEngine;
using Unity.AI.Navigation;

public class VibeLinkEditor : EditorWindow
{
    [MenuItem("Tools/VibeLink Control Panel")]
    public static void ShowWindow()
    {
        GetWindow<VibeLinkEditor>("VibeLink");
    }

    void OnGUI()
    {
        GUILayout.Label("Actions Phase 1", EditorStyles.boldLabel);
        
        if (GUILayout.Button("Setup Basic Scene (Light + Plane)"))
        {
            SetupScene();
        }

        if (GUILayout.Button("Dump Hierarchy to Console"))
        {
            Debug.Log(HierarchyDumper.DumpScene());
        }

        GUILayout.Space(10);
        GUILayout.Label("Server Status", EditorStyles.boldLabel);
        
        if (VibeLinkServer.Instance != null)
        {
             GUILayout.Label($"Running on Port: {VibeLinkServer.Instance.port}");
             if (GUILayout.Button("Force Restart Server"))
             {
                 VibeLinkServer.Instance.StopServer();
                 VibeLinkServer.Instance.StartServer();
             }
        }
        else
        {
            GUILayout.Label("Server not found in scene.");
            if (GUILayout.Button("Add Server to Scene"))
            {
                new GameObject("VibeLinkServer").AddComponent<VibeLinkServer>();
            }
        }
        GUILayout.Space(10);
        GUILayout.Label("Blender Factory (Requires VibeLink Addon)", EditorStyles.boldLabel);
        
        if (VibeLinkServer.Instance != null && GUILayout.Button("Generate House Level 1"))
        {
            // Enviar ruta absoluta de Assets para que Blender sepa donde guardar
            string path = Application.dataPath.Replace("\\", "/");
            string json = "{\"cmd\": \"generate_house\", \"params\": {\"level\": 1, \"width\": 5, \"depth\": 5, \"seed\": " + Random.Range(0, 9999) + ", \"export_path\": \"" + path + "\"}}";
            VibeLinkServer.Instance.Broadcast(json);
            Debug.Log($"[VibeLink] Request Sent: {json}");
        }
        
        if (VibeLinkServer.Instance != null && GUILayout.Button("Generate House Level 2"))
        {
            string path = Application.dataPath.Replace("\\", "/");
            string json = "{\"cmd\": \"generate_house\", \"params\": {\"level\": 2, \"width\": 6, \"depth\": 8, \"seed\": " + Random.Range(0, 9999) + ", \"export_path\": \"" + path + "\"}}";
            VibeLinkServer.Instance.Broadcast(json);
            Debug.Log($"[VibeLink] Request Sent: {json}");
        }

        GUILayout.Space(5);
        if (VibeLinkServer.Instance != null && GUILayout.Button("🧬 Generate Evolution (L1 -> L5)", GUILayout.Height(30)))
        {
            string path = Application.dataPath.Replace("\\", "/");
            for(int i=1; i<=5; i++)
            {
                int w = 5 + (i-1); 
                int d = 5 + (i-1);
                // Seed fijo o aleatorio? Aleatorio para variedad.
                int seed = Random.Range(0, 9999);
                string json = "{\"cmd\": \"generate_house\", \"params\": {\"level\": " + i + ", \"width\": " + w + ", \"depth\": " + d + ", \"seed\": " + seed + ", \"export_path\": \"" + path + "\"}}";
                VibeLinkServer.Instance.Broadcast(json);
            }
            Debug.Log("[VibeLink] Sent 5 Evolution Requests!");
        }

        GUILayout.Space(5);
        if (VibeLinkServer.Instance != null && GUILayout.Button("🌳 Generate Nature Set (Tree + Rock)", GUILayout.Height(30)))
        {
            string path = Application.dataPath.Replace("\\", "/");
            int seed = Random.Range(0, 9999);
            
            // Tree
            string jsonTree = "{\"cmd\": \"generate_nature\", \"params\": {\"type\": \"tree\", \"height\": 4.0, \"seed\": " + seed + ", \"export_path\": \"" + path + "\"}}";
            VibeLinkServer.Instance.Broadcast(jsonTree);
            
            // Rock
            string jsonRock = "{\"cmd\": \"generate_nature\", \"params\": {\"type\": \"rock\", \"scale\": 1.5, \"seed\": " + (seed+1) + ", \"export_path\": \"" + path + "\"}}";
            VibeLinkServer.Instance.Broadcast(jsonRock);
            
            Debug.Log("[VibeLink] Sent Nature Requests!");
        }

        GUILayout.Space(5);
        if (VibeLinkServer.Instance != null && GUILayout.Button("🧑 Generate Villager Set (6 variants)", GUILayout.Height(30)))
        {
            string path = Application.dataPath.Replace("\\", "/");
            // 3 masculinos + 3 femeninos con seeds distintas
            string[] styles = {
                "villager",        // Aldeano M
                "guard",           // Guardia M
                "elder",           // Anciano M
                "female_villager", // Aldeana F
                "female_villager", // Aldeana F (seed distinta)
                "female_elder",    // Anciana F
            };
            for (int i = 0; i < styles.Length; i++)
            {
                int seed = Random.Range(0, 99999);
                string json = $"{{\"cmd\": \"generate_humanoid\", \"params\": {{\"style\": \"{styles[i]}\", \"seed\": {seed}, \"export_path\": \"{path}\"}}}}";
                VibeLinkServer.Instance.Broadcast(json);
            }
            Debug.Log("[VibeLink] Sent 6 Villager Requests!");
        }


    }

    void SetupScene()
    {
        // 1. Crear Plane
        GameObject plane = GameObject.CreatePrimitive(PrimitiveType.Plane);
        plane.name = "Ground";
        plane.transform.localScale = new Vector3(5, 1, 5);
        plane.layer = LayerMask.NameToLayer("Default");
        
        // 2. NavMeshSurface (Moderno)
        // Eliminamos uso de static flags obsoletos
        var surface = plane.GetComponent<NavMeshSurface>();
        if (surface == null) surface = plane.AddComponent<NavMeshSurface>();
        
        surface.useGeometry = UnityEngine.AI.NavMeshCollectGeometry.PhysicsColliders;
        surface.collectObjects = CollectObjects.Children; // O All
        surface.BuildNavMesh(); // Bake inmediato
        
        Debug.Log("[VibeLink] Scene Setup Complete & NavMesh Baked.");
        
        // 3. Crear Luz
        if (Object.FindAnyObjectByType<Light>() == null)
        {
             GameObject light = new GameObject("Directional Light");
             var l = light.AddComponent<Light>();
             l.type = LightType.Directional;
             light.transform.rotation = Quaternion.Euler(50, -30, 0);
        }
        
        // 3. Crear Cámara si no existe
        if (Object.FindAnyObjectByType<Camera>() == null)
        {
            GameObject cam = new GameObject("Main Camera");
            cam.tag = "MainCamera";
            cam.AddComponent<Camera>();
            cam.AddComponent<AudioListener>();
            cam.transform.position = new Vector3(0, 10, -10);
            cam.transform.LookAt(Vector3.zero);
        }
    }
}
