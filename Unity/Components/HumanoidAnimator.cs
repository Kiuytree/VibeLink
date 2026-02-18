using UnityEngine;

/// <summary>
/// Procedural animator for VibeLink-generated humanoid characters.
/// Drives bone rotations via Mathf.Sin/Cos curves — no AnimationClip needed.
/// 
/// States: Idle, Walk, Carry, Sleep, Sit
/// </summary>
public class HumanoidAnimator : MonoBehaviour
{
    // ─── State ───────────────────────────────────────────────────────────
    public enum AnimState { Idle, Walk, Carry, Sleep, Sit }
    [Header("Current State")]
    public AnimState state = AnimState.Idle;

    // ─── Bone References (auto-found by name) ────────────────────────────
    [Header("Bones (auto-assigned on Start)")]
    public Transform boneHips;
    public Transform boneSpine;
    public Transform boneChest;
    public Transform boneHead;
    public Transform boneLeftUpperArm;
    public Transform boneLeftLowerArm;
    public Transform boneRightUpperArm;
    public Transform boneRightLowerArm;
    public Transform boneLeftUpperLeg;
    public Transform boneLeftLowerLeg;
    public Transform boneRightUpperLeg;
    public Transform boneRightLowerLeg;

    // ─── Tuning ──────────────────────────────────────────────────────────
    [Header("Walk")]
    public float walkSpeed     = 2.5f;
    public float legSwingAngle = 35f;
    public float armSwingAngle = 25f;

    [Header("Idle")]
    public float idleBreathSpeed = 0.8f;
    public float idleBreathAngle = 2f;
    public float idleHeadBobAngle = 1.5f;

    [Header("Carry")]
    public float carryArmAngle = 70f;   // Arms raised forward

    [Header("Transition")]
    public float blendSpeed = 6f;

    // ─── Internal ────────────────────────────────────────────────────────
    private float _t;           // Animation time accumulator
    private AnimState _prevState;

    // Blended rotation targets
    private Quaternion _qLeftUpperArm, _qRightUpperArm;
    private Quaternion _qLeftUpperLeg, _qRightUpperLeg;
    private Quaternion _qLeftLowerLeg, _qRightLowerLeg;
    private Quaternion _qSpine, _qHead;

    // ─────────────────────────────────────────────────────────────────────
    void Start()
    {
        AutoFindBones();
        _prevState = state;
    }

    void Update()
    {
        _t += Time.deltaTime;
        UpdateAnimation();
    }

    // ─── Bone Auto-Discovery ─────────────────────────────────────────────
    void AutoFindBones()
    {
        boneHips          = FindBone("Hips");
        boneSpine         = FindBone("Spine");
        boneChest         = FindBone("Chest");
        boneHead          = FindBone("Head");
        boneLeftUpperArm  = FindBone("LeftUpperArm");
        boneLeftLowerArm  = FindBone("LeftLowerArm");
        boneRightUpperArm = FindBone("RightUpperArm");
        boneRightLowerArm = FindBone("RightLowerArm");
        boneLeftUpperLeg  = FindBone("LeftUpperLeg");
        boneLeftLowerLeg  = FindBone("LeftLowerLeg");
        boneRightUpperLeg = FindBone("RightUpperLeg");
        boneRightLowerLeg = FindBone("RightLowerLeg");
    }

    Transform FindBone(string boneName)
    {
        // Search all children recursively
        foreach (Transform t in GetComponentsInChildren<Transform>())
            if (t.name == boneName) return t;
        return null;
    }

    // ─── Animation Dispatcher ────────────────────────────────────────────
    void UpdateAnimation()
    {
        switch (state)
        {
            case AnimState.Idle:   AnimateIdle();   break;
            case AnimState.Walk:   AnimateWalk();   break;
            case AnimState.Carry:  AnimateCarry();  break;
            case AnimState.Sleep:  AnimateSleep();  break;
            case AnimState.Sit:    AnimateSit();    break;
        }
    }

    // ─── IDLE ────────────────────────────────────────────────────────────
    void AnimateIdle()
    {
        float breath = Mathf.Sin(_t * idleBreathSpeed) * idleBreathAngle;
        float headBob = Mathf.Sin(_t * idleBreathSpeed * 0.7f) * idleHeadBobAngle;

        // Subtle chest breathing
        SetBoneRotation(boneSpine, breath, 0, 0);
        SetBoneRotation(boneHead, headBob, 0, 0);

        // Arms hang naturally with slight sway
        float sway = Mathf.Sin(_t * 0.5f) * 3f;
        SetBoneRotation(boneLeftUpperArm,  5f + sway, 0, -10f);
        SetBoneRotation(boneRightUpperArm, 5f - sway, 0,  10f);

        // Legs straight
        SetBoneRotation(boneLeftUpperLeg,  0, 0, 0);
        SetBoneRotation(boneRightUpperLeg, 0, 0, 0);
        SetBoneRotation(boneLeftLowerLeg,  0, 0, 0);
        SetBoneRotation(boneRightLowerLeg, 0, 0, 0);
    }

    // ─── WALK ────────────────────────────────────────────────────────────
    void AnimateWalk()
    {
        float cycle = _t * walkSpeed;
        float legL  =  Mathf.Sin(cycle) * legSwingAngle;
        float legR  = -Mathf.Sin(cycle) * legSwingAngle;
        float armL  = -Mathf.Sin(cycle) * armSwingAngle;  // Opposite to legs
        float armR  =  Mathf.Sin(cycle) * armSwingAngle;

        // Knee bend: only bend when leg swings back
        float kneeBendL = Mathf.Max(0, -Mathf.Sin(cycle)) * 30f;
        float kneeBendR = Mathf.Max(0,  Mathf.Sin(cycle)) * 30f;

        // Hip sway
        float hipSway = Mathf.Sin(cycle * 2) * 4f;

        SetBoneRotation(boneHips,         0, 0, hipSway);
        SetBoneRotation(boneSpine,        Mathf.Sin(cycle * 2) * 3f, 0, 0);
        SetBoneRotation(boneHead,         0, Mathf.Sin(cycle) * 5f, 0);

        SetBoneRotation(boneLeftUpperLeg,  legL, 0, 0);
        SetBoneRotation(boneRightUpperLeg, legR, 0, 0);
        SetBoneRotation(boneLeftLowerLeg,  kneeBendL, 0, 0);
        SetBoneRotation(boneRightLowerLeg, kneeBendR, 0, 0);

        SetBoneRotation(boneLeftUpperArm,  armL, 0, -8f);
        SetBoneRotation(boneRightUpperArm, armR, 0,  8f);
        SetBoneRotation(boneLeftLowerArm,  Mathf.Max(0, armL) * 0.5f, 0, 0);
        SetBoneRotation(boneRightLowerArm, Mathf.Max(0, armR) * 0.5f, 0, 0);
    }

    // ─── CARRY ───────────────────────────────────────────────────────────
    void AnimateCarry()
    {
        float cycle = _t * walkSpeed;
        float legL  =  Mathf.Sin(cycle) * legSwingAngle * 0.6f;
        float legR  = -Mathf.Sin(cycle) * legSwingAngle * 0.6f;

        // Arms raised forward holding something
        float carryBob = Mathf.Sin(_t * 1.5f) * 3f;

        SetBoneRotation(boneSpine,        10f, 0, 0);  // Lean forward slightly
        SetBoneRotation(boneHead,         -5f, 0, 0);  // Look down at load

        SetBoneRotation(boneLeftUpperArm,  -(carryArmAngle + carryBob), 0, -15f);
        SetBoneRotation(boneRightUpperArm, -(carryArmAngle + carryBob), 0,  15f);
        SetBoneRotation(boneLeftLowerArm,  -60f, 0, 0);  // Bent at elbow
        SetBoneRotation(boneRightLowerArm, -60f, 0, 0);

        SetBoneRotation(boneLeftUpperLeg,  legL, 0, 0);
        SetBoneRotation(boneRightUpperLeg, legR, 0, 0);
        SetBoneRotation(boneLeftLowerLeg,  Mathf.Max(0, -legL) * 0.5f, 0, 0);
        SetBoneRotation(boneRightLowerLeg, Mathf.Max(0, -legR) * 0.5f, 0, 0);
    }

    // ─── SLEEP ───────────────────────────────────────────────────────────
    void AnimateSleep()
    {
        float breath = Mathf.Sin(_t * 0.4f) * 3f;  // Slow breathing

        // Lay flat: rotate entire character -90 on X (done via Hips)
        SetBoneRotation(boneHips,  0, 0, 0);
        SetBoneRotation(boneSpine, breath, 0, 0);
        SetBoneRotation(boneHead,  -10f, 10f, 0);  // Head tilted to side

        // Arms relaxed at sides
        SetBoneRotation(boneLeftUpperArm,  20f, 0, -30f);
        SetBoneRotation(boneRightUpperArm, 20f, 0,  30f);
        SetBoneRotation(boneLeftLowerArm,  15f, 0, 0);
        SetBoneRotation(boneRightLowerArm, 15f, 0, 0);

        // Legs slightly bent
        SetBoneRotation(boneLeftUpperLeg,  15f, 0, 5f);
        SetBoneRotation(boneRightUpperLeg, 15f, 0, -5f);
        SetBoneRotation(boneLeftLowerLeg,  20f, 0, 0);
        SetBoneRotation(boneRightLowerLeg, 20f, 0, 0);
    }

    // ─── SIT ─────────────────────────────────────────────────────────────
    void AnimateSit()
    {
        float breath = Mathf.Sin(_t * idleBreathSpeed) * idleBreathAngle;

        SetBoneRotation(boneSpine, -5f + breath, 0, 0);
        SetBoneRotation(boneHead,  5f, 0, 0);

        // Thighs horizontal (90 degrees forward)
        SetBoneRotation(boneLeftUpperLeg,  -85f, 0, 5f);
        SetBoneRotation(boneRightUpperLeg, -85f, 0, -5f);

        // Knees bent (lower legs hang down)
        SetBoneRotation(boneLeftLowerLeg,  85f, 0, 0);
        SetBoneRotation(boneRightLowerLeg, 85f, 0, 0);

        // Arms resting on knees
        SetBoneRotation(boneLeftUpperArm,  -60f, 0, -20f);
        SetBoneRotation(boneRightUpperArm, -60f, 0,  20f);
        SetBoneRotation(boneLeftLowerArm,  -30f, 0, 0);
        SetBoneRotation(boneRightLowerArm, -30f, 0, 0);
    }

    // ─── Utility ─────────────────────────────────────────────────────────
    void SetBoneRotation(Transform bone, float x, float y, float z)
    {
        if (bone == null) return;
        Quaternion target = Quaternion.Euler(x, y, z);
        bone.localRotation = Quaternion.Slerp(bone.localRotation, target,
                                               Time.deltaTime * blendSpeed);
    }

    // ─── Public API ──────────────────────────────────────────────────────
    public void SetState(AnimState newState)
    {
        state = newState;
    }

    public void SetState(string stateName)
    {
        if (System.Enum.TryParse(stateName, true, out AnimState s))
            state = s;
    }
}
