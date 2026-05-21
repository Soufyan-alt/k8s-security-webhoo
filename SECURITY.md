# 🛡️ Workload Security & Policy Enforcement Report (SECURITY.md)

This document structuralizes the defensive parameters, evaluated vulnerability vectors, and programmatic mitigation layers implemented via the Custom Validating Admission Controller to protect the Kubernetes API cluster plane.

---

## 1. ⚠️ The Security Vulnerabilities & Vector Assessment

This architecture targets and neutralizes two distinct configurations that violate production security baselines:

### 🛑 Vector A: Container Root Execution (`CWE-276 / MITRE ATT&CK T1068`)
* **The Threat:** Workloads running without explicitly forbidding root execution states (`runAsUser: 0`).
* **The Critical Impact:** If an application inside the container is compromised via a remote code execution (RCE) flaw, the hacker instantly inherits root privileges. This permits container breakouts, kernel file-system manipulation on the host node, and full cluster compromise.

### 🛑 Vector B: Supply Chain Poisoning via Untrusted Registries (`MITRE ATT&CK T1195`)
* **The Threat:** Developers pulling images from arbitrary public open registries (e.g., untrusted Docker Hub repositories or external nodes).
* **The Critical Impact:** Public images are prone to typosquatting or deliberate malware injection (crypto-miners, embedded backdoors). Allowing unauthorized registries bypasses the corporate security compliance pipeline.

---

## 2. ☸️ Programmatic Automated Detection (Admission Layer Interception)

Unlike traditional runtime agents that detect a threat *after* execution, this architecture leverages the **Kubernetes Validation Admission Lifecycle** to catch vulnerabilities *before* they are written to disk:

* **Synchronous JSON Parsing:** When a user triggers `kubectl apply`, the `kube-apiserver` intercepts the manifest and forwards a cryptographically signed `AdmissionReview` request over HTTPS to our Python gateway.
* **Algorithmic Validation:** The Custom Webhook dynamically inspects the inner block of the object payload:
  * It scans the `securityContext` parameters string checking for `runAsNonRoot: true` and `runAsUser > 0`.
  * It intercepts the string structure of the `image` field to ensure alignment with the authorized corporate prefix registry (`mycompany.azurecr.io`).

```text
📊 [INCOMING APISERVER PAYLOAD] ──> [WEBHOOK PARSING ENGINE] ──> STATUS: REJECTED (allowed: false)
