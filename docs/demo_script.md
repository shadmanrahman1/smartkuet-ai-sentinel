# SmartKUET Sentinel - Presentation Demo Script

This script is structured for a 2.5-minute spoken presentation or video recording to pitch the project to competition judges.

---

### [0:00 - 0:15] 1. Introduction (15 Seconds)
*   **Action**: Show the Central Dashboard screen.
*   **Speaker**:
    > "Honorable judges, I am presenting **SmartKUET Sentinel**: an offline Edge-AI campus security and exam integrity assistant designed specifically for KUET. Our goal is to convert standard CCTV networks from passive recording boxes into active, real-time decision-support tools."

### [0:15 - 0:45] 2. The Problem (30 Seconds)
*   **Action**: Show the problem slides or emphasize offline constraints.
*   **Speaker**:
    > "Standard smart security systems rely on third-party cloud AI APIs. But on university campuses, cloud solutions present serious flaws. They stream sensitive student footage outside our servers, violating privacy. They suffer from latency delays, making gate intercepts too slow. And if the campus network drops, the security system is completely disabled. We need a solution that is private, fast, and works entirely without the internet."

### [0:45 - 1:30] 3. System Workflow (45 Seconds)
*   **Action**: Point to the system architecture diagram or dashboard stream.
*   **Speaker**:
    > "SmartKUET Sentinel resolves these issues by running entirely on-premises. First, camera feeds are read locally in a CPU-efficient stream. Second, a local YOLO model runs frame-by-frame, detecting objects like persons and phones. Third, a motion tracker assigns temporary IDs to follow targets without permanent profiling. Finally, a deterministic security rules engine automatically checks behaviors—like loitering, crowding, or device presence in exams—broadcasting live warnings via WebSockets."

### [1:30 - 2:15] 4. Interface Walkthrough (45 Seconds)
*   **Action**: Switch between Central Dashboard, Guard View, and Examiner View.
*   **Speaker**:
    > "We have built three specialized interfaces. Our **Central Dashboard** monitors streams, shows active track logs, and lists incidents with hardware diagnostics. The **Guard View** is mobile-first, presenting gate guards with clear alert cards and action triggers like ALLOW or VERIFY ID. The **Examiner View** demonstrates our future exam invigilation concept, displaying candidate suspicion indexing alongside suspicion level guides."

### [2:15 - 2:45] 5. Validation & Ethics (30 Seconds)
*   **Action**: Point to the Runs/Benchmarks summary or pytest terminal success.
*   **Speaker**:
    > "We validated our prototype on local gate footage. On basic CPU hardware, the pipeline achieves an average YOLO inference latency of just 37 milliseconds, running at over 45 frames per second. Crucially, Sentinel does not perform face identification or student profiling, and does not make automated decisions. AI only assists; the human guard or examiner makes the final call."

### [2:45 - 3:00] 6. Closing (15 Seconds)
*   **Action**: Show final slide with the Git repo URL.
*   **Speaker**:
    > "SmartKUET Sentinel offers a private, secure, and cost-effective AI assistant built for local campus networks. The code, pitch docs, and runbooks are fully verified and open-source. Thank you, and I welcome your questions."
