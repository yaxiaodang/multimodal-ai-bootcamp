import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

from src.image_info import get_image_info


def test_valid_png_returns_correct_dimensions(tmp_path):
    image_path = tmp_path / "valid.png"
    Image.new("RGB", (32, 24), color="white").save(image_path)

    result = get_image_info(str(image_path))

    assert result["width"] == 32
    assert result["height"] == 24
    assert result["format"] == "PNG"


def test_missing_file_raises_clear_error(tmp_path):
    missing_path = tmp_path / "missing.png"

    with pytest.raises(FileNotFoundError, match="文件不存在"):
        get_image_info(str(missing_path))


def test_non_image_file_raises_clear_error(tmp_path):
    text_path = tmp_path / "not-an-image.txt"
    text_path.write_text("hello", encoding="utf-8")

    with pytest.raises(ValueError, match="无法识别"):
        get_image_info(str(text_path))


def test_valid_jpeg_returns_correct_dimensions(tmp_path):
    image_path = tmp_path / "valid.jpg"
    Image.new("RGB", (48, 36), color="white").save(image_path, format="JPEG")

    result = get_image_info(str(image_path))

    assert result["width"] == 48
    assert result["height"] == 36
    assert result["format"] == "JPEG"


def test_minimum_size_png_returns_one_by_one(tmp_path):
    image_path = tmp_path / "tiny.png"
    Image.new("RGB", (1, 1), color="black").save(image_path, format="PNG")

    result = get_image_info(str(image_path))

    assert result["width"] == 1
    assert result["height"] == 1
    assert result["format"] == "PNG"


def test_real_bmp_raises_value_error_for_unsupported_format(tmp_path):
    image_path = tmp_path / "unsupported.bmp"
    Image.new("RGB", (8, 8), color="blue").save(image_path, format="BMP")

    with pytest.raises(ValueError, match="不支持"):
        get_image_info(str(image_path))


def test_cli_bmp_exit_code_non_zero_and_error_output_mentions_unsupported(tmp_path):
    image_path = tmp_path / "unsupported.bmp"
    Image.new("RGB", (8, 8), color="blue").save(image_path, format="BMP")

    project_root = Path(__file__).resolve().parents[1]
    completed = subprocess.run(
        [sys.executable, "src/image_info.py", str(image_path)],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )

    assert completed.returncode != 0
    assert "file:" not in completed.stdout
    assert "width:" not in completed.stdout
    assert "height:" not in completed.stdout
    assert "format:" not in completed.stdout
    assert "不支持" in completed.stderr


def test_bmp_content_with_png_extension_is_rejected(tmp_path):
    image_path = tmp_path / "disguised.png"

    # 文件名看起来是 PNG，但明确将实际内容保存为 BMP。
    Image.new("RGB", (8, 8), color="blue").save(image_path, format="BMP")

    with pytest.raises(ValueError, match="不支持"):
        get_image_info(str(image_path))


def test_text_content_with_png_extension_is_unrecognized(tmp_path):
    image_path = tmp_path / "not-an-image.png"

    # 文件名看起来是 PNG，但实际内容只是普通文本。
    image_path.write_text("not an image", encoding="utf-8")

    with pytest.raises(ValueError, match="无法识别"):
        get_image_info(str(image_path))