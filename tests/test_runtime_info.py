from core.config import get_runtime_info


def test_runtime_info_returns_expected_keys():
    info = get_runtime_info()

    expected = {
        "python_version",
        "platform",
        "torch_available",
        "torch_version",
        "cuda_available",
        "cuda_version",
        "cuda_device_count",
        "cuda_device_name",
        "ultralytics_available",
        "opencv_version",
    }

    assert expected.issubset(info)
