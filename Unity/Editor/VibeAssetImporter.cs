using UnityEngine;
using UnityEditor;

public class VibeAssetImporter : AssetPostprocessor
{
    static int _villagerCount = 0;

    void OnPreprocessModel()
    {
        if (assetPath.Contains("Generated/Models"))
        {
            ModelImporter modelImporter = assetImporter as ModelImporter;
            if (modelImporter != null)
            {
                modelImporter.globalScale = 1.0f;
                modelImporter.useFileScale = true;
                modelImporter.addCollider = false; // Humanoids need no collider on import
                modelImporter.materialImportMode = ModelImporterMaterialImportMode.ImportStandard;
                modelImporter.materialLocation = ModelImporterMaterialLocation.InPrefab;

                // Humanoid: use Generic rig so our bones are accessible by name
                if (assetPath.Contains("Humanoid"))
                {
                    modelImporter.animationType = ModelImporterAnimationType.Generic;
                    modelImporter.bakeAxisConversion = true; // Let Unity handle Blender Z-up → Y-up
                }
                else
                {
                    modelImporter.bakeAxisConversion = true;
                }
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

                // 1. Intentar extraer color HEX del nombre (formato: Mat_..._RRGGBB_...)
                // Ej: Mat_F_Skin_EAC8A4_12345
                var hexMatch = System.Text.RegularExpressions.Regex.Match(mat.name, @"_([0-9A-Fa-f]{6})_");
                if (hexMatch.Success)
                {
                    if (ColorUtility.TryParseHtmlString("#" + hexMatch.Groups[1].Value, out Color extractedColor))
                    {
                        mat.color = extractedColor;
                        if (mat.HasProperty("_BaseColor")) mat.SetColor("_BaseColor", extractedColor);
                        // Asegurar que usa un shader que soporte color
                        if (mat.shader.name == "Standard" || mat.shader.name == "Hidden/InternalErrorShader") 
                        {
                            // Intentar cambiar a URP Lit si es posible, o dejar Standard
                             mat.shader = Shader.Find("Universal Render Pipeline/Lit") ?? Shader.Find("Standard");
                        }
                        continue;
                    }
                }

                // 2. Si tiene dígitos pero no HEX (legacy procedural), no tocar
                bool isProcedural = System.Text.RegularExpressions.Regex.IsMatch(mat.name, @"\d");
                if (isProcedural) continue;

                // 3. Reglas por defecto para assets estáticos (Casas, etc)
                Color? overrideColor = null;

                if (mat.name.Contains("Walls"))      overrideColor = new Color(0.9f, 0.85f, 0.7f); // Beige
                else if (mat.name.Contains("Roof"))  overrideColor = new Color(0.6f, 0.2f, 0.1f);  // Rojo Teja
                else if (mat.name.Contains("Wood"))  overrideColor = new Color(0.4f, 0.25f, 0.1f); // Marrón Oscuro
                else if (mat.name.Contains("Door"))  overrideColor = new Color(0.25f, 0.15f, 0.1f); // Madera Puerta
                else if (mat.name.Contains("Window")) overrideColor = new Color(0.4f, 0.7f, 0.9f, 0.5f); // Azul Cristal
                else if (mat.name.Contains("Stone")) overrideColor = new Color(0.5f, 0.5f, 0.55f); // Gris Piedra
                else if (mat.name.Contains("Grass") || mat.name.Contains("Leaves")) overrideColor = new Color(0.1f, 0.6f, 0.1f); // Verde Bosque
                else if (mat.name.Contains("Skin"))  overrideColor = new Color(0.85f, 0.65f, 0.5f);  // Piel base
                else if (mat.name.Contains("Cloth")) overrideColor = new Color(0.3f,  0.45f, 0.6f);  // Tela Azul base

                // Solo aplicar si hay una regla específica
                if (overrideColor.HasValue)
                {
                    mat.color = overrideColor.Value;
                    if (mat.HasProperty("_BaseColor")) mat.SetColor("_BaseColor", overrideColor.Value);
                }
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

                    // Villagers: posición automática en fila
                    if (prefab.name.StartsWith("Villager"))
                    {
                        instance.transform.rotation = Quaternion.identity;
                        instance.transform.position = new Vector3(_villagerCount * 3f, 0, 15f);
                        _villagerCount++;
                    }

                    Selection.activeGameObject = instance;
                    SceneView.FrameLastActiveSceneView();
                }
            }
        }
    }
}
