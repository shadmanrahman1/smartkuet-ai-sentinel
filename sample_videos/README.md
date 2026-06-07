# Sample Videos

Put CCTV, gate, corridor, classroom, or exam-room demo videos in this folder.

Recommended formats:

- `.mp4`
- `.avi`
- `.mov`

To run SmartKUET Sentinel from a local video file, set this in `.env`:

```txt
CAMERA_SOURCE=sample_videos/your_video.mp4
```

For Android phone IP Webcam, use the phone app's video URL, for example:

```txt
CAMERA_SOURCE=http://PHONE_IP:8080/video
```

For DroidCam, CCTV, or RTSP cameras, use the correct URL from that tool or camera:

```txt
CAMERA_SOURCE=rtsp://example.com/stream
```

Do not place private or sensitive footage here if the project folder will be shared.
