using UnityEngine;
using UnityEditor;

public class VibeAssetImporter : AssetPostprocessor
{
    void OnPreprocessModel()
    {
        if (assetPath.Contains("Generated/Models"))
        {
            ModelImporter modelImporter = assetImporter as ModelImporter;
            if (modelImporter != null)
            {
                // === FIX ESCALA & ROTACIÓN ===
                modelImporter.globalScale = 1.0f;
                modelImporter.useFileScale = true; 
                modelImporter.bakeAxisConversion = true;
                
                modelImporter.addCollider = true;
                modelImporter.materialImportMode = ModelImporterMaterialImportMode.ImportStandard;
                modelImporter.materialLocation = ModelImporterMaterialLocation.InPrefab;
            }
        }
    }

    // === FIX MATERIALES (Auto-Paint) ===
    void OnPostprocessModel(GameObject g)
    {
        if (!assetPath.Contains("Generated/Models")) return;

        Renderer[] renderers = g.GetComponentsInChildren<Renderer>();
        foreach (Renderer r in renderers)
        {
            foreach (Material mat in r.sharedMaterials)
            {
                if (mat == null) continue;
                
                // Color Mágico basado en nombre
                Color color = Color.white;
                if (mat.name.Contains("Walls")) color = new Color(0.9f, 0.85f, 0.7f); // Beige
                else if (mat.name.Contains("Roof")) color = new Color(0.6f, 0.2f, 0.1f);  // Rojo Teja
                else if (mat.name.Contains("Wood")) color = new Color(0.4f, 0.25f, 0.1f); // Marrón Oscuro
                else if (mat.name.Contains("Door")) color = new Color(0.25f, 0.15f, 0.1f); // Madera Puerta
                else if (mat.name.Contains("Window")) color = new Color(0.4f, 0.7f, 0.9f, 0.5f); // Azul Cristal
                else if (mat.name.Contains("Stone")) color = new Color(0.5f, 0.5f, 0.55f); // Gris Piedra
                else if (mat.name.Contains("Grass") || mat.name.Contains("Leaves")) color = new Color(0.1f, 0.6f, 0.1f); // Verde Bosque
                else if (mat.name.Contains("Skin"))  color = new Color(0.85f, 0.65f, 0.5f);  // Piel
                else if (mat.name.Contains("Cloth")) color = new Color(0.3f,  0.45f, 0.6f);  // Tela Azul
                
                mat.color = color;
                if (mat.HasProperty("_BaseColor")) mat.SetColor("_BaseColor", color);
            }
        }
    }
    
    static void OnPostprocessAllAssets(string[] importedAssets, string[] deletedAssets, string[] movedAssets, string[] movedFromAssetPaths)
    {
        foreach (string str in importedAssets)
        {
            if (str.Contains("Generated/Models") && str.EndsWith(".fbx"))
            {
                Debug.Log($"[VibeLink] Importing & Spawning: {str}");
                
                // Cargar el asset recién importado
                GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(str);
                if (prefab != null)
                {
                    // Instanciar en la escena
                    GameObject instance = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
                    instance.name = prefab.name;
                    
                    // Posición por tipo de asset
                    Vector3 spawnPos = Vector3.zero;

                    // Casas evolutivas (L1-L5)
                    if      (prefab.name.Contains("_L1_")) spawnPos = new Vector3(0,  0, 0);
                    else if (prefab.name.Contains("_L2_")) spawnPos = new Vector3(12, 0, 0);
                    else if (prefab.name.Contains("_L3_")) spawnPos = new Vector3(24, 0, 0);
                    else if (prefab.name.Contains("_L4_")) spawnPos = new Vector3(38, 0, 0);
                    else if (prefab.name.Contains("_L5_")) spawnPos = new Vector3(54, 0, 0);

                    // Humanoides (por estilo)
                    else if (prefab.name.Contains("Villager")) spawnPos = new Vector3(0, 0, 10);
                    else if (prefab.name.Contains("Guard"))    spawnPos = new Vector3(4, 0, 10);
                    else if (prefab.name.Contains("Elder"))    spawnPos = new Vector3(8, 0, 10);

                    instance.transform.position = spawnPos;

                    // Auto-attach HumanoidAnimator si es un humanoide
                    if (prefab.name.Contains("Humanoid"))
                    {
                        if (instance.GetComponent<HumanoidAnimator>() == null)
                            instance.AddComponent<HumanoidAnimator>();
                    }

                    Selection.activeGameObject = instance;
                    SceneView.FrameLastActiveSceneView();
                }
            }
        }
    }
}
