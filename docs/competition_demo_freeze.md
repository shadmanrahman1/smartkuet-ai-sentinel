# Competition Demo Freeze & Presentation Pack — SmartKUET Sentinel

This document defines the stable demonstration path, page checklists, API verification routes, and judges' Q&A guidance for the SmartKUET Sentinel project presentation.

---

## 1. The Demo Narrative

The presentation must follow a clear story showing how SmartKUET Sentinel secures the campus gate locally:
1. **The Base State**: Campus gate is quiet. YOLO tracks 1-2 people. The security rule is in a safe `green` state (Normal Activity).
2. **The Security Event**: A person lingers (loiters) near the entrance or crowd levels rise. An alert is instantly triggered on the dashboard.
3. **Face Verification Check**: The guard selects an enrolled demo member A/B/C. ArcFace locally matches a known demo member from the open-source LFW demo gallery (simulating verification via a future KUET-approved local database).
4. **Multi-Modal Risk Fusion**: The system combines camera health, time, rules, face verification status, and object cues into a single advisory score. The guard allows entry, and the audit trail is updated.
5. **Privacy Statement**: The presenter emphasizes that all operations run locally on the edge, keeping student data secure and private.

---

## 2. Page & Endpoint Checklists

Before presenting to the judges, open the following pages in the browser (default host `127.0.0.1:8002`):

### A. Classic Dashboards (HTML/CSS/JS)
* **Main Monitoring Console**: [http://127.0.0.1:8002/](http://127.0.0.1:8002/)  
  *Showcase*: Real-time incident logs, CCTV feed overlay, and active YOLO track metrics.
* **Guard Mobile View**: [http://127.0.0.1:8002/guard](http://127.0.0.1:8002/guard)  
  *Showcase*: Mobile assistant with Allow/Verify/Deny actions and current gate rule.
* **Exam Invigilation Mock**: [http://127.0.0.1:8002/exam](http://127.0.0.1:8002/exam)  
  *Showcase*: Concept mockup of suspicious student behaviors and seating logs.

### B. React Showcase (Vite Production/Fallback)
* **Landing Page**: [http://127.0.0.1:5173/#/](http://127.0.0.1:5173/#/) (or `localhost:8002/dashboard/#/` if built static)  
  *Showcase*: Premium innovation pitch, core features grid, and offline edge architecture.
* **Security Dashboard**: [http://127.0.0.1:5173/#/security](http://127.0.0.1:5173/#/security)  
  *Showcase*: Central command card, active tracks list, YOLO detection logs, and the **Multi-Modal Risk Fusion** panel.
* **Guard Workspace**: [http://127.0.0.1:5173/#/guard](http://127.0.0.1:5173/#/guard)  
  *Showcase*: Fused risk advisory gauges, signal verification chips, and on-demand face verification panels.
* **Exam Monitoring Workspace**: [http://127.0.0.1:5173/#/exam](http://127.0.0.1:5173/#/exam)  
  *Showcase*: suspicious student behavior mockup.

### C. Live Backend Status APIs (Exposed JSON)
Show judges that the AI engine outputs pure structured data:
* **System Vital Diagnostics**: `/api/runtime/status` — Displays Python, OpenCV, Torch versions, and CUDA device configurations.
* **Security Event Rules**: `/api/security/status` — Exposes active spatial-temporal rule states and cooldowns.
* **Face Verification Status**: `/api/face/status` — Reports ArcFace model preparation state and database enrollment counts.
* **Object-Cue Scaffold**: `/api/object-cues/status` — Checks local YOLO object class configurations.
* **Fused Threat advisory**: `/api/risk-fusion/status` — Returns the combined risk score, recommended action, and reasons list.

---

## 3. What to Say to Judges (Key Pitch Points)

* **Explainable Advisory**: *"Our system doesn't automate gate lockouts. It generates a fused threat score with a clear audit reasoning trace, assisting the human guard (human-in-the-loop) who holds the final decision."*
* **100% Offline & Local**: *"SmartKUET Sentinel runs entirely on the campus edge. Biometric embeddings are calculated and saved locally. We do not transmit faces or data to any external cloud, preserving student privacy."*
* **Multi-Modal Fusion**: *"We don't rely solely on face verification. We combine camera availability, loitering tracking, after-hours time, and visual cues (like lanyards or visitor badges) to produce a robust safety verdict."*
* **Innovation & Research**: *"Our contribution lies in combining real-time edge tracking with deterministic risk fusion rules, presenting a structured research prototype tailored for gate security."*

---

## 4. What NOT to Claim (Absolute Constraints)

* **No Real Student Database**: Do not claim the system is currently connected to the actual KUET student profile database. Explain that the face verification is a prototype demonstration only, using LFW/open-source demo identities for compliance and safety. 
* **Demo Identity Verification**: Emphasize that the active system matches a "known demo member" or "LFW/open-source demo identity" from academic datasets, and that integration with a "future KUET-approved local database" is a design proposal rather than a present capability.
* **No Cloud Dependency**: Do not claim the system queries online APIs or downloads external data on the fly. Emphasize that it is designed to operate completely offline.
* **No Automated Decisions**: Do not claim the system automatically denies entry or locks doors. Clarify that it is purely advisory to keep guards in control.
* **No Model Training in Real-time**: Do not claim the system trains weights or updates models during runtime.
