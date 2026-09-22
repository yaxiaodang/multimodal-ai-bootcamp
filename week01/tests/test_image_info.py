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