using UnityEngine;
using System.Collections.Generic;
using System.Linq;

public static class HierarchyDumper
{
    [System.Serializable]
    public class SceneDump
    {
        public string sceneName;
        public List<ObjectDump> objects = new List<ObjectDump>();
    }

    [System.Serializable]
    public class ObjectDump
    {
        public string name;
        public int id;
        public int parentId;
        public bool active;
        public bool isStatic;
        public string tag;
        public string layer;
        
        // Transform Info
        public Vector3 pos;
        public Vector3 rot;
        public Vector3 scale;
        
        public List<string> components;
    }

    public static string DumpScene()
    {
        SceneDump dump = new SceneDump();
        var activeScene = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
        dump.sceneName = activeScene.IsValid() ? activeScene.name : "No Active Scene";
        
        var rootObjects = activeScene.GetRootGameObjects();
        foreach (var root in rootObjects)
        {
            ProcessTransform(root.transform, dump, 0);
        }

        return JsonUtility.ToJson(dump, true);
    }

    private static void ProcessTransform(Transform t, SceneDump dump, int parentId)
    {
        ObjectDump obj = new ObjectDump();
        obj.name = t.name;
        obj.id = t.gameObject.GetInstanceID();
        obj.parentId = parentId;
        obj.active = t.gameObject.activeInHierarchy;
        obj.isStatic = t.gameObject.isStatic;
        obj.tag = t.tag;
        obj.layer = LayerMask.LayerToName(t.gameObject.layer);
        
        // Transform Data (World Space para pos/rot, Local para scale suele ser más útil pero damos raw data)
        obj.pos = t.position;
        obj.rot = t.eulerAngles;
        obj.scale = t.lossyScale; // lossyScale es la escala global aproximada

        // Recuperar componentes
        var comps = t.GetComponents<Component>();
        obj.components = new List<string>();
        foreach(var c in comps)
        {
            if (c == null) continue; // Missing scripts
            
            string compName = c.GetType().Name;
            // Intentar ver si está habilitado (para Behaviours/Renderers)
            if (c is Behaviour b) 
                compName += b.enabled ? "" : " (Disabled)";
            else if (c is Renderer r)
                compName += r.enabled ? "" : " (Disabled)";
            else if (c is Collider col)
                compName += col.enabled ? "" : " (Disabled)";
                
            obj.components.Add(compName);
        }

        dump.objects.Add(obj);

        foreach (Transform child in t)
        {
            ProcessTransform(child, dump, obj.id);
        }
    }
}
