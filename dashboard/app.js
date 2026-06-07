function wsUrl(path) {
  const scheme = window.location.protocol === "https:" ? "wss" : "ws";
  return `${scheme}://${window.location.host}${path}`;
}

function colorClass(value) {
  return String(value || "green").toLowerCase();
}

function setText(id, value) {
  const element = document.getElementById(id);
  if (element) element.textContent = value ?? "Waiting for event...";
}

function setStatusCard(id, color) {
  const element = document.getElementById(id);
  if (!element) return;
  element.classList.remove("green", "yellow", "orange", "red");
  element.classList.add(colorClass(color));
}

function badge(color) {
  const clean = colorClass(color);
  return `<span class="badge ${clean}">${clean}</span>`;
}

function formatTime(timestamp) {
  if (!timestamp) return "";
  return new Date(timestamp).toLocaleTimeString();
}

function prependEvent(containerId, html) {
  const container = document.getElementById(containerId);
  if (!container) return;
  const wrapper = document.createElement("div");
  wrapper.className = "event-row";
  wrapper.innerHTML = html;
  container.prepend(wrapper);
  while (container.children.length > 8) container.lastElementChild.remove();
}

function prependColoredEvent(containerId, html, color) {
  const container = document.getElementById(containerId);
  if (!container) return;
  const wrapper = document.createElement("div");
  wrapper.className = `event-row ${colorClass(color)}`;
  wrapper.innerHTML = html;
  container.prepend(wrapper);
  while (container.children.length > 8) container.lastElementChild.remove();
}

function updateDetectionSummary(summary = {}) {
  setText("detection-persons", summary.person_count ?? 0);
  setText("detection-phones", summary.phone_count ?? 0);
  setText("detection-vehicles", summary.vehicle_count ?? 0);
  setText("detection-total", summary.total ?? 0);

  const status = summary.enabled === false
    ? "YOLO disabled"
    : summary.error
      ? "YOLO unavailable"
      : "YOLO enabled";
  setText("detection-status", status);
  setText("detection-error", summary.error || "Annotated stream ready when camera frames are available.");
}

function formatResolution(camera = {}) {
  if (!camera.width || !camera.height) return "--";
  return `${camera.width} x ${camera.height}`;
}

function updateRuntimeStatus(status = {}) {
  const camera = status.camera || {};
  const runtime = status.runtime || {};
  const video = status.video_processor || {};
  const summary = status.detections || video.latest_summary || {};
  const tracking = status.tracking || video.latest_tracking_summary || {};
  const security = status.security_status || video.security_status || {};

  updateDetectionSummary(summary);
  updateTrackingSummary(tracking);
  updateSecurityStatus(security, summary, tracking);
  setText("diag-camera-source", camera.source || "--");
  setText("diag-camera-opened", camera.is_opened ? "opened" : "not opened");
  setText("diag-source-type", camera.source_type || "--");
  setText("diag-resolution", formatResolution(camera));
  setText("diag-camera-fps", camera.fps_estimate ?? "--");
  setText("diag-yolo-status", video.model_error ? "unavailable" : video.yolo_enabled ? "enabled" : "disabled");
  setText("diag-requested-device", video.device || "--");
  setText("diag-selected-device", video.selected_device || "--");
  setText("diag-cuda", runtime.cuda_available ? "yes" : "no");
  setText("diag-inference", video.last_inference_ms == null ? "--" : `${video.last_inference_ms} ms`);
  setText("diag-effective-fps", video.effective_fps ?? "--");
  setText("diag-error", video.model_error || camera.last_error || "Runtime diagnostics ready.");
}

function securityPriority(level) {
  return { green: 0, yellow: 1, orange: 2, red: 3 }[colorClass(level)] ?? 0;
}

function pickSecurityEvent(events = []) {
  if (!events.length) return null;
  return events.reduce((best, event) => {
    if (!best) return event;
    const eventScore = securityPriority(event.level);
    const bestScore = securityPriority(best.level);
    if (eventScore !== bestScore) return eventScore > bestScore ? event : best;
    if (event.event_type === "HIGH_RISK_COMBINED") return event;
    return best;
  }, null);
}

function formatTrackIds(ids = []) {
  return ids.length ? ids.map((id) => `ID ${id}`).join(", ") : "--";
}

function updateSecurityStatus(status = {}, summary = {}, tracking = {}, event = null) {
  const selected = event || pickSecurityEvent(status.latest_events || []);
  const evidence = selected?.evidence || {};
  const level = selected?.level || status.latest_level || "green";
  const eventType = selected?.event_type || status.latest_event_type || "NORMAL_ACTIVITY";
  const instruction = selected?.instruction || status.latest_instruction || "Monitor normally.";
  const relatedTrackIds = selected?.related_track_ids || [];
  const activeTracks = evidence.active_track_count ?? tracking.active_track_count ?? 0;
  const phoneCount = evidence.phone_count ?? summary.phone_count ?? 0;
  const vehicleCount = evidence.vehicle_count ?? summary.vehicle_count ?? 0;
  const maxTrackAge = Number(evidence.max_track_age_seconds || 0).toFixed(1);

  setStatusCard("security-card", level);
  setText("security-status", eventType);
  setText("security-event-type", eventType);
  setText("security-level", colorClass(level).toUpperCase());
  setText("security-instruction", instruction);
  setText("security-location", selected?.location || status.location || "KUET Main Gate");
  setText("security-confidence", `${Math.round(Number(selected?.confidence || 0) * 100)}%`);
  setText("security-related-tracks", formatTrackIds(relatedTrackIds));
  setText("security-active-tracks", activeTracks);
  setText("security-phones", phoneCount);
  setText("security-vehicles", vehicleCount);
  setText("security-crowding-threshold", status.crowding_person_threshold ?? "--");
  setText("security-loiter-threshold", status.loiter_seconds == null ? "--" : `${status.loiter_seconds}s`);
  setText("security-after-hours", evidence.after_hours == null ? "--" : evidence.after_hours ? "yes" : "no");
  setText(
    "security-evidence-summary",
    `Tracks ${activeTracks} | max age ${maxTrackAge}s | phones ${phoneCount} | vehicles ${vehicleCount}`
  );
}

function updateTrackingSummary(tracking = {}) {
  const tracks = tracking.active_tracks || [];
  setText("tracking-enabled", tracking.enabled === false ? "disabled" : "enabled");
  setText("tracking-type", tracking.tracker_type || "--");
  setText("tracking-active", tracking.active_track_count ?? tracks.length ?? 0);
  setText("tracking-total", tracking.total_tracks_seen ?? 0);
  setText("guard-track-count", tracking.active_track_count ?? tracks.length ?? 0);
  setText("guard-track-ids", tracks.length ? tracks.map((track) => `ID ${track.track_id}`).join(", ") : "--");
  setText("tracking-error", tracking.error || "Tracking ready.");

  const list = document.getElementById("tracking-list");
  if (!list) return;
  list.innerHTML = "";
  if (!tracks.length) {
    const empty = document.createElement("div");
    empty.className = "event-row";
    empty.innerHTML = '<span class="muted">No active person tracks.</span>';
    list.appendChild(empty);
    return;
  }

  for (const track of tracks) {
    const row = document.createElement("div");
    row.className = "event-row";
    row.innerHTML = `<div class="event-meta"><strong>ID ${track.track_id}</strong><span class="muted">${Number(track.confidence || 0).toFixed(2)}</span></div>
      <span class="muted">Age ${Number(track.age_seconds || 0).toFixed(1)}s - ${track.class_name}</span>`;
    list.appendChild(row);
  }
}

async function pollDetectionSummary(intervalMs = 1500) {
  try {
    const response = await fetch("/api/detections/latest", { cache: "no-store" });
    if (response.ok) {
      updateDetectionSummary(await response.json());
    }
  } catch {
    updateDetectionSummary({
      enabled: true,
      error: "Detection API unavailable",
      total: 0,
      person_count: 0,
      phone_count: 0,
      vehicle_count: 0,
      classes: {},
    });
  } finally {
    window.setTimeout(() => pollDetectionSummary(intervalMs), intervalMs);
  }
}

async function pollRuntimeStatus(intervalMs = 1500) {
  try {
    const response = await fetch("/api/runtime/status", { cache: "no-store" });
    if (response.ok) {
      updateRuntimeStatus(await response.json());
    }
  } catch {
    setText("diag-error", "Runtime API unavailable");
  } finally {
    window.setTimeout(() => pollRuntimeStatus(intervalMs), intervalMs);
  }
}

async function saveEvidenceSnapshot() {
  setText("snapshot-result", "Saving snapshot...");
  try {
    const response = await fetch("/api/evidence/snapshot", { method: "POST" });
    const result = await response.json();
    if (result.saved) {
      setText("snapshot-result", `Saved: ${result.path}`);
    } else {
      setText("snapshot-result", `Not saved: ${result.reason || "No frame available"}`);
    }
  } catch {
    setText("snapshot-result", "Snapshot API unavailable");
  }
}

async function resetTracker() {
  setText("tracking-error", "Resetting tracker...");
  try {
    const response = await fetch("/api/tracking/reset", { method: "POST" });
    const result = await response.json();
    setText("tracking-error", result.reset ? "Tracker reset." : "Tracker reset failed.");
  } catch {
    setText("tracking-error", "Tracking API unavailable");
  }
}

async function resetSecurityRules() {
  setText("security-rule-reset-result", "Resetting rule cooldowns...");
  try {
    const response = await fetch("/api/security/rules/reset", { method: "POST" });
    const result = await response.json();
    if (result.security_status) updateSecurityStatus(result.security_status);
    setText("security-rule-reset-result", result.reset ? "Security rule cooldowns reset." : "Security rule reset failed.");
  } catch {
    setText("security-rule-reset-result", "Security rules API unavailable");
  }
}

function connectSecurity(options = {}) {
  const socket = new WebSocket(wsUrl("/ws/security"));
  socket.onmessage = (message) => {
    const event = JSON.parse(message.data);
    const color = colorClass(event.level || event.status_color);
    const eventType = event.event_type || event.detected_name;
    setStatusCard(options.cardId || "security-card", color);
    setText(options.statusId || "security-status", eventType);
    setText(options.instructionId || "security-instruction", event.instruction);
    setText(options.locationId || "security-location", event.location);
    setText(options.confidenceId || "security-confidence", `${Math.round(event.confidence * 100)}%`);
    if (event.detection_summary) updateDetectionSummary(event.detection_summary);
    if (event.tracking_summary) updateTrackingSummary(event.tracking_summary);
    if (event.security_status) {
      updateSecurityStatus(
        event.security_status,
        event.detection_summary || {},
        event.tracking_summary || {},
        event
      );
    }

    prependColoredEvent(
      options.listId || "security-events",
      `<div class="event-meta"><strong>${eventType}</strong>${badge(color)}</div>
       <span class="muted">${event.instruction} - ${formatTime(event.timestamp)}</span>`,
      color
    );
  };
}

function connectExam(options = {}) {
  const socket = new WebSocket(wsUrl("/ws/exam"));
  socket.onmessage = (message) => {
    const event = JSON.parse(message.data);
    const color = colorClass(event.color_level);
    setStatusCard(options.cardId || "exam-card", color);
    setText(options.statusId || "exam-status", event.behavior_type);
    setText(options.seatId || "exam-seat", event.seat_no);
    setText(options.scoreId || "exam-score", Number(event.current_score).toFixed(1));
    setText(options.addedId || "exam-added", `+${Number(event.score_added).toFixed(1)}`);

    prependEvent(
      options.listId || "exam-events",
      `<div class="event-meta"><strong>${event.seat_no} - ${event.behavior_type}</strong>${badge(color)}</div>
       <span class="muted">Score ${Number(event.current_score).toFixed(1)} - ${formatTime(event.timestamp)}</span>`
    );
  };
}

function localAction(text) {
  setText("local-action", text);
}
