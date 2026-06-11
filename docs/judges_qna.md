# SmartKUET Sentinel - Judges Q&A Preparation

This document prepares answers for likely questions raised by innovation competition judges.

---

### 1. Why is this useful for KUET?
> **Answer**: KUET checkpoints (like the Main Gate) experience high traffic and crowding, especially during shift changes or events. Standard CCTV is passive. SmartKUET Sentinel assists campus security by providing real-time local alarms when crowding or loitering occurs. Similarly, for exams, it provides a prototype framework for assisting invigilators in checking candidate desks locally.

### 2. Does it identify students?
> **Answer**: No, this prototype does not identify specific students or verify their names. It assigns temporary track IDs (e.g., `ID 1`, `ID 2`) to boxes while they are visible on camera to trace their motion paths. All identities are completely anonymous, protecting student privacy.

### 3. Is it privacy-safe?
> **Answer**: Yes. Traditional smart security systems stream video feeds to cloud services, which is a major privacy risk. SmartKUET Sentinel is fully offline-first: all YOLO object detection, tracking, and rules engine logic run locally on the host machine. No video stream, database record, or image snapshot ever leaves the local network.

### 4. Does it work without internet?
> **Answer**: Yes, it works fully without internet. All dependencies, models (`models/yolov8n.pt`), databases (`smartkuet.db`), and dashboard files are stored locally on the drive. It can run on a closed local network (LAN) inside KUET, remaining completely secure against external connection dropouts.

### 5. What happens if the AI is wrong?
> **Answer**: As with all computer vision systems, false positives (e.g., misclassifying an object) or false negatives (e.g., missing a phone) can happen. To mitigate this risk, the system uses a **Human-in-the-Loop** model. The AI never takes automated actions like locking gates or penalizing candidates; it only highlights warnings on the console. The human security guard or examiner retains final authority.

### 6. What is the role of the guard?
> **Answer**: The guard monitors the mobile-responsive Guard View. When a yellow, orange, or red warning fires (such as camera loss or crowd blockages), the guard receives recommended instructions. The guard then assesses the situation visually and performs manual overrides using ALLOW, DENY, or VERIFY ID buttons, ensuring a human makes all critical security decisions.

### 7. Why not use cloud CCTV analytics?
> **Answer**: 
> 1. **Data Sovereignty**: Educational institutions must avoid streaming student movements to public clouds.
> 2. **Network Resilience**: Campus gates must remain monitored even during network downtime.
> 3. **Operational Cost**: Cloud APIs charge recurring usage fees. SmartKUET Sentinel has zero cloud bills because it runs on standard local CPU/GPU hardware.

### 8. What is currently implemented vs future work?
> **Answer**:
> * **Implemented**: Real-time YOLOv8 object detection (persons, phones, vehicles), motion tracking, rules engine, SQLite incident database, evidence snapshot captures, central admin dashboard, guard gate console, examiner mock console, and automated validation benchmarking.
> * **Future Work**: Local opt-in student face check-in database (under student consent), training localized cheat-behavior spatial-temporal models, and scale-out multi-camera network integrations.

### 9. How much would deployment cost?
> **Answer**: The software uses a fully open-source stack (FastAPI, OpenCV, PyTorch, Ultralytics YOLO) with zero licensing costs. Deployment only requires local hardware (such as standard laptops or mini-PCs costing around 40,000–60,000 BDT) connected to existing IP security cameras.

### 10. How can this scale to gates, halls, and exams?
> **Answer**: The core is structured as a multi-layered pipeline. Multiple cameras can feed local frames into a multi-threaded processing worker. High-traffic areas (gates) run the Security Rules Engine, while classroom cameras run the Exam Integrity rules, reporting back to the Central Dashboard.

### 11. What are the limitations?
> **Answer**: 
> 1. **CPU Speed**: Without a dedicated GPU, processing frame rates on standard laptops are around 15–20 FPS (when analyzing all frames). We optimized this by running YOLO every 3rd frame with tracking interpolation, reaching ~45 FPS on CPU.
> 2. **Tracking Drifts**: Temporary IDs can occasionally change if targets are heavily obstructed.
> 3. **Exam Scopes**: Cheating behaviors are mock signals for the prototype, representing concept layout designs.

### 12. What is innovative here?
> **Answer**: The innovation lies in the combination of **offline-first local edge deep learning** with a **deterministic security rules engine** designed for universities. Instead of expensive cloud infrastructure, we deliver low-latency, privacy-safe, and highly resilient campus monitoring using standard computer hardware.
