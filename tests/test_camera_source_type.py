from core.camera import classify_camera_source


def test_classify_webcam_source():
    assert classify_camera_source("0") == "webcam"
    assert classify_camera_source(0) == "webcam"


def test_classify_video_file_source():
    assert classify_camera_source("sample_videos/demo.mp4") == "video_file"


def test_classify_ip_camera_source():
    assert classify_camera_source("http://192.168.1.10:8080/video") == "ip_camera"


def test_classify_rtsp_source():
    assert classify_camera_source("rtsp://example.com/stream") == "rtsp"
