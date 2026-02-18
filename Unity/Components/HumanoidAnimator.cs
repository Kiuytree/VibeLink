using UnityEngine;
using System.Collections.Generic;

/// <summary>
/// Procedural animator for VibeLink-generated humanoid characters.
/// Drives bone rotations via Mathf.Sin/Cos — no AnimationClip needed.
/// 
/// IMPORTANT: Rotations are applied as OFFSETS from the bone's rest pose,
/// so they work correctly regardless of how Blender exported the rig.
/// 
/// States: Idle, Walk, Carry, Sleep, Sit
/// </summary>
public class HumanoidAnimator : MonoBehaviour
{
    public enum AnimState { Idle, Walk, Carry, Sleep, Sit }

    [Header("Current State")]
    public AnimState state = AnimState.Idle;

    [Header("Walk")]
    public float walkSpeed     = 2.5f;
    public float legSwingAngle = 35f;
    public float armSwingAngle = 25f;

    [Header("Idle")]
    public float idleBreathSpeed = 0.8f;
    public float idleBreathAngle = 2f;

    [Header("Carry")]
    public float carryArmAngle = 65f;

    [Header("Transition")]
    public float blendSpeed = 8f;

    // ─── Bone References ─────────────────────────────────────────────────
    Transform boneHips, boneSpine, boneChest, boneHead, boneNeck;
    Transform boneLUA, boneLLA, boneLH;   // Left  Upper/Lower Arm, Hand
    Transform boneRUA, boneRLA, boneRH;   // Right Upper/Lower Arm, Hand
    Transform boneLUL, boneLLL, boneLF;   // Left  Upper/Lower Leg, Foot
    Transform boneRUL, boneRLL, boneRF;   // Right Upper/Lower Leg, Foot

    // ─── Rest Poses (captured at Start) ──────────────────────────────────
    Dictionary<Transform, Quaternion> _restPose = new Dictionary<Transform, Quaternion>();

    float _t;

    // ─────────────────────────────────────────────────────────────────────
    void Start()
    {
        FindBones();
        CaptureRestPose();
    }

    void Update()
    {
        _t += Time.deltaTime;
        switch (state)
        {
            case AnimState.Idle:  AnimIdle();  break;
            case AnimState.Walk:  AnimWalk();  break;
            case AnimState.Carry: AnimCarry(); break;
            case AnimState.Sleep: AnimSleep(); break;
            case AnimState.Sit:   AnimSit();   break;
        }
    }

    // ─── Bone Discovery ──────────────────────────────────────────────────
    void FindBones()
    {
        boneHips  = Find("Hips");
        boneSpine = Find("Spine");
        boneChest = Find("Chest");
        boneNeck  = Find("Neck");
        boneHead  = Find("Head");

        boneLUA = Find("LeftUpperArm");
        boneLLA = Find("LeftLowerArm");
        boneLH  = Find("LeftHand");
        boneRUA = Find("RightUpperArm");
        boneRLA = Find("RightLowerArm");
        boneRH  = Find("RightHand");

        boneLUL = Find("LeftUpperLeg");
        boneLLL = Find("LeftLowerLeg");
        boneLF  = Find("LeftFoot");
        boneRUL = Find("RightUpperLeg");
        boneRLL = Find("RightLowerLeg");
        boneRF  = Find("RightFoot");
    }

    Transform Find(string boneName)
    {
        foreach (Transform t in GetComponentsInChildren<Transform>())
            if (t.name == boneName) return t;
        return null;
    }

    // ─── Rest Pose Capture ───────────────────────────────────────────────
    void CaptureRestPose()
    {
        foreach (Transform t in GetComponentsInChildren<Transform>())
            _restPose[t] = t.localRotation;
    }

    Quaternion Rest(Transform t)
    {
        if (t == null) return Quaternion.identity;
        return _restPose.TryGetValue(t, out var r) ? r : t.localRotation;
    }

    // ─── Core: Apply offset FROM rest pose ───────────────────────────────
    /// <summary>
    /// Rotates a bone by 'offset' degrees relative to its rest pose.
    /// This is axis-agnostic — works regardless of Blender export orientation.
    /// </summary>
    void Rotate(Transform bone, float x, float y, float z)
    {
        if (bone == null) return;
        Quaternion target = Rest(bone) * Quaternion.Euler(x, y, z);
        bone.localRotation = Quaternion.Slerp(bone.localRotation, target, Time.deltaTime * blendSpeed);
    }

    void ResetBone(Transform bone)
    {
        if (bone == null) return;
        bone.localRotation = Quaternion.Slerp(bone.localRotation, Rest(bone), Time.deltaTime * blendSpeed);
    }

    // ─── IDLE ─────────────────────────────────────────────────────────────
    void AnimIdle()
    {
        float breath = Mathf.Sin(_t * idleBreathSpeed) * idleBreathAngle;
        float sway   = Mathf.Sin(_t * 0.4f) * 2f;

        Rotate(boneSpine, breath, 0, 0);
        Rotate(boneHead,  Mathf.Sin(_t * 0.6f) * 1.5f, sway, 0);

        // Arms hang with gentle sway
        Rotate(boneLUA, 5f + sway, 0, -8f);
        Rotate(boneRUA, 5f - sway, 0,  8f);
        ResetBone(boneLLA); ResetBone(boneRLA);

        // Legs straight
        ResetBone(boneLUL); ResetBone(boneRUL);
        ResetBone(boneLLL); ResetBone(boneRLL);
    }

    // ─── WALK ─────────────────────────────────────────────────────────────
    void AnimWalk()
    {
        float c     = _t * walkSpeed;
        float legL  =  Mathf.Sin(c) * legSwingAngle;
        float legR  = -Mathf.Sin(c) * legSwingAngle;
        float armL  = -Mathf.Sin(c) * armSwingAngle;
        float armR  =  Mathf.Sin(c) * armSwingAngle;
        float kneeL =  Mathf.Max(0, -Mathf.Sin(c)) * 28f;
        float kneeR =  Mathf.Max(0,  Mathf.Sin(c)) * 28f;
        float hipSw =  Mathf.Sin(c * 2) * 3f;

        Rotate(boneHips,  0, 0, hipSw);
        Rotate(boneSpine, Mathf.Sin(c * 2) * 2f, 0, 0);
        Rotate(boneHead,  0, Mathf.Sin(c) * 4f, 0);

        Rotate(boneLUL, legL, 0, 0);
        Rotate(boneRUL, legR, 0, 0);
        Rotate(boneLLL, kneeL, 0, 0);
        Rotate(boneRLL, kneeR, 0, 0);
        ResetBone(boneLF); ResetBone(boneRF);

        Rotate(boneLUA, armL, 0, -6f);
        Rotate(boneRUA, armR, 0,  6f);
        Rotate(boneLLA, Mathf.Max(0, armL) * 0.4f, 0, 0);
        Rotate(boneRLA, Mathf.Max(0, armR) * 0.4f, 0, 0);
    }

    // ─── CARRY ────────────────────────────────────────────────────────────
    void AnimCarry()
    {
        float c   = _t * walkSpeed * 0.8f;
        float bob = Mathf.Sin(_t * 1.5f) * 2f;
        float legL =  Mathf.Sin(c) * legSwingAngle * 0.5f;
        float legR = -Mathf.Sin(c) * legSwingAngle * 0.5f;

        Rotate(boneSpine, 8f, 0, 0);
        Rotate(boneHead, -4f, 0, 0);

        // Arms raised forward holding load
        Rotate(boneLUA, -(carryArmAngle + bob), 0, -12f);
        Rotate(boneRUA, -(carryArmAngle + bob), 0,  12f);
        Rotate(boneLLA, -55f, 0, 0);
        Rotate(boneRLA, -55f, 0, 0);

        Rotate(boneLUL, legL, 0, 0);
        Rotate(boneRUL, legR, 0, 0);
        Rotate(boneLLL, Mathf.Max(0, -legL) * 0.4f, 0, 0);
        Rotate(boneRLL, Mathf.Max(0, -legR) * 0.4f, 0, 0);
    }

    // ─── SLEEP ────────────────────────────────────────────────────────────
    void AnimSleep()
    {
        float breath = Mathf.Sin(_t * 0.35f) * 2.5f;

        Rotate(boneSpine, breath, 0, 0);
        Rotate(boneHead, -8f, 12f, 0);

        Rotate(boneLUA, 15f, 0, -25f);
        Rotate(boneRUA, 15f, 0,  25f);
        Rotate(boneLLA, 12f, 0, 0);
        Rotate(boneRLA, 12f, 0, 0);

        Rotate(boneLUL, 12f, 0,  4f);
        Rotate(boneRUL, 12f, 0, -4f);
        Rotate(boneLLL, 18f, 0, 0);
        Rotate(boneRLL, 18f, 0, 0);
    }

    // ─── SIT ──────────────────────────────────────────────────────────────
    void AnimSit()
    {
        float breath = Mathf.Sin(_t * idleBreathSpeed) * idleBreathAngle;

        Rotate(boneSpine, -4f + breath, 0, 0);
        Rotate(boneHead,   4f, 0, 0);

        // Thighs ~horizontal
        Rotate(boneLUL, -82f, 0,  4f);
        Rotate(boneRUL, -82f, 0, -4f);
        // Lower legs hang down
        Rotate(boneLLL, 82f, 0, 0);
        Rotate(boneRLL, 82f, 0, 0);
        ResetBone(boneLF); ResetBone(boneRF);

        // Arms resting on knees
        Rotate(boneLUA, -55f, 0, -18f);
        Rotate(boneRUA, -55f, 0,  18f);
        Rotate(boneLLA, -28f, 0, 0);
        Rotate(boneRLA, -28f, 0, 0);
    }

    // ─── Public API ───────────────────────────────────────────────────────
    public void SetState(AnimState newState) => state = newState;

    public void SetState(string stateName)
    {
        if (System.Enum.TryParse(stateName, true, out AnimState s))
            state = s;
    }
}
