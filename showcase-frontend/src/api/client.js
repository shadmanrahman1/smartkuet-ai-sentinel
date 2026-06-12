/**
 * SmartKUET Sentinel — API client
 * Fetches from FastAPI backend (proxied via Vite dev server on /api).
 * Falls back to polished demo data when backend is offline.
 */

const BASE = '';  // Vite dev proxy handles /api → http://127.0.0.1:8002

async function safeFetch(path, fallback) {
  try {
    const res = await fetch(`${BASE}${path}`, { signal: AbortSignal.timeout(4000) });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return { data: await res.json(), online: true };
  } catch {
    return { data: fallback, online: false };
  }
}

// ── Fallback demo data ───────────────────────────────────────────
export const DEMO_RUNTIME = {
  python_version: '3.13.5',
  torch_version: '2.11.0+cu128',
  cuda_available: true,
  cuda_device_name: 'NVIDIA GeForce RTX 3050 Laptop GPU',
  opencv_version: '4.13.0',
  ultralytics_available: true,
};

export const DEMO_SECURITY = {
  rules_enabled: true,
  latest_level: 'green',
  latest_event_type: 'NORMAL_ACTIVITY',
  latest_instruction: 'Monitor normally.',
  gate_zone_enabled: true,
  crowding_person_threshold: 4,
  loiter_seconds: 15,
  latest_events: [
    {
      event_type: 'NORMAL_ACTIVITY',
      level: 'green',
      title: 'Normal activity',
      instruction: 'Monitor normally.',
      confidence: 0.7,
      location: 'KUET Main Gate',
      related_track_ids: [1, 2],
      evidence: { active_track_count: 2, active_tracks_in_gate_zone: 2 },
      timestamp: new Date().toISOString(),
    },
  ],
};

export const DEMO_TRACKING = {
  enabled: true,
  tracker_type: 'iou_fallback',
  active_track_count: 2,
  total_tracks_seen: 14,
  active_tracks: [
    { track_id: 1, class_name: 'person', confidence: 0.88, age_seconds: 4.2, missed_frames: 0 },
    { track_id: 2, class_name: 'person', confidence: 0.76, age_seconds: 1.8, missed_frames: 0 },
  ],
};

// ── API helpers ──────────────────────────────────────────────────
export async function fetchRuntimeStatus() {
  const { data, online } = await safeFetch('/api/runtime/status', {
    runtime: DEMO_RUNTIME,
    video: { avg_inference_ms: 11.69, effective_fps: 85.8, selected_device: 'cuda:0' },
    camera: { is_opened: false, source_type: 'demo' },
  });
  return { data, online };
}

export async function fetchSecurityStatus() {
  return safeFetch('/api/security/status', DEMO_SECURITY);
}

export async function fetchTrackingLatest() {
  return safeFetch('/api/tracking/latest', DEMO_TRACKING);
}

export const DEMO_OBJECT_CUES = {
  enabled: false,
  configured: false,
  model_path: 'models/object_cues/best.pt',
  status: 'DISABLED',
  supported_cues: ['id_card', 'lanyard', 'visitor_badge', 'bag', 'helmet'],
  instruction: 'Object cue detection is disabled. Enable in config/env.',
};

export async function fetchObjectCuesStatus() {
  return safeFetch('/api/object-cues/status', DEMO_OBJECT_CUES);
}

export const VIDEO_FEED_URL = 'http://127.0.0.1:8002/api/video_feed';
