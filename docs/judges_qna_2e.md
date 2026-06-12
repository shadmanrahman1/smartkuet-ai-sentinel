# SmartKUET Sentinel: Judges Q&A Guide (Milestone 2E)

This guide prepares the presentation team for technical, research, and ethical questions from competition judges and reviewers.

---

### Q1: What problem does SmartKUET Sentinel solve?
**A**: Traditional campus gates rely on manual ID checks or cloud-based AI cameras. Manual checks are slow and error-prone, while cloud-based AI introduces high latency, internet dependencies, and critical biometric privacy risks. SmartKUET Sentinel provides an offline, edge-AI gate surveillance system that tracks movement, verifies mock authorized credentials locally, and feeds an explainable risk engine to assist security guards in real-time.

### Q2: Is the system fully offline?
**A**: Yes. The system has zero external dependencies during runtime. YOLO detection, ByteTrack tracking, InsightFace biometric matching, and the Multi-Modal Risk Fusion Engine run entirely on local host resources. There are no API requests sent to external servers or cloud providers.

### Q3: Does it identify real KUET students?
**A**: No. To protect student privacy and ensure a controlled test environment, the current build uses a mock local gallery built on open-source LFW (Labeled Faces in the Wild) identities. No real student biometric data is stored or queried. The system is designed to demonstrate biometric pipeline capability without exposing actual student profiles.

### Q4: Why use the LFW dataset for testing?
**A**: LFW is the industry-standard benchmark for face verification. Using it allows us to validate the accuracy, speed, and threshold boundaries (e.g. cosine similarity metrics) of the InsightFace (buffalo_s) ONNX model in a standardized, academically-recognized environment, proving the viability of our local verification pipelines.

### Q5: What does the Roboflow / Object Cue layer do?
**A**: The object cue layer is designed to detect support markers, such as student lanyards, lanyards with cards, name badges, and helmets. In the current freeze package, this is implemented as a deterministic code-scaffold (disabled in the config) that outlines classes and integrates with the risk score calculator, awaiting custom model training on local campus gate imagery.

### Q6: What is the Multi-Modal Risk Fusion Engine?
**A**: It is a deterministic, rule-based expert engine that aggregates signals from different sensors (YOLO tracks, gate zone ROI breaches, biometric verification matching, camera status, and after-hours schedules) into a single unified security risk level (LOW, MEDIUM, HIGH, CRITICAL) accompanied by actionable instructions for guards. 

### Q7: What happens if the system makes an incorrect prediction?
**A**: The system operates strictly as an advisory "human-in-the-loop" model. The API outputs `human_review_required: true` for all states. The system does not autonomously lock gates or deny entry; it alerts the operator and provides reasoning traces (e.g., "unknown face in gate zone after-hours"), leaving the final security decision to the human guard.

### Q8: What are the measured local performance results?
**A**: When benchmarked locally using `sample_videos/demo.mp4`, the system achieved:
* **Approximate Speed**: **98.5 FPS**
* **Average Inference Latency**: **11.22 ms** (YOLO detection)
* **Test Suite Correctness**: **95 out of 95 tests passing**
* **Vite React Compile Time**: **173 ms**
*All parameters measured on the local host machine (RTX 3050 Laptop GPU / Python 3.13.5).*

### Q9: What are the main limitations of the current freeze state?
**A**:
1. **Gallery Scale**: The local demo gallery contains 3 mock identities. Expanding to thousands of students would require migrating to an optimized vector database index (e.g., Milvus or FAISS) to maintain sub-20ms lookup times.
2. **Scaffolded Object Cues**: The object cue detector is a placeholder scaffold and is disabled in production settings until real lanyard and badge imagery is trained.
3. **Single Camera Flow**: The current backend is optimized for processing one video stream. Multi-camera inputs require concurrent processing threads or an asynchronous worker manager.

### Q10: How can this work be turned into a research paper?
**A**: We can target IEEE or local computer science journals by framing this as:
> *"A Local-First, Privacy-Preserving Multi-Modal Risk Fusion System for Academic Campus Access Control."*
We can publish our mathematical formulations of the risk score fusion, local GPU inference performance benchmarks (under varying tracking density and scale of vector galleries), and a comparative study between cloud-dependent security cameras and local edge deployments.

### Q11: How can KUET deploy this system ethically?
**A**:
1. **Consent-Based Opt-In**: Students can opt-in to register their face features locally, while others use traditional RF cards.
2. **Local Vector Security**: Store face features only as mathematical embeddings (vectors), never as raw image files, and encrypt the local SQLite database.
3. **No Centralized Biometric DB**: Run all matching processes at the local gate processor, discarding feature representations immediately after verification.
