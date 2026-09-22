from pathlib import Path

from PIL import Image


output_path = Path("samples/demo.png")
output_path.parent.mkdir(parents=True, exist_ok=True)

image = Image.new("RGB", (640, 480), color=(70, 130, 180))
image.save(output_path)

print(f"created: {output_path}")
print("size: 640x480")