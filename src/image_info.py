import argparse
from pathlib import Path

from PIL import Image, UnidentifiedImageError


def get_image_info(file_path: str) -> dict:
    """读取图片并返回尺寸及格式。"""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"文件不存在：{path}")

    if not path.is_file():
        raise ValueError(f"输入路径不是文件：{path}")

    try:
        with Image.open(path) as image:
            return {
                "file": str(path),
                "width": image.width,
                "height": image.height,
                "format": image.format or "unknown",
            }
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError(f"无法识别该图片：{path}") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="image-info",
        description="读取一张图片并输出宽度、高度和文件格式。",
    )
    parser.add_argument("image", help="待检查图片的路径")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        info = get_image_info(args.image)
    except (FileNotFoundError, ValueError, PermissionError) as exc:
        parser.error(str(exc))

    print(f"file: {info['file']}")
    print(f"width: {info['width']}")
    print(f"height: {info['height']}")
    print(f"format: {info['format']}")


if __name__ == "__main__":
    main()