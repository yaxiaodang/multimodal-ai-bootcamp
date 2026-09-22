import platform
import sys
from importlib.metadata import PackageNotFoundError, version


print("python:", sys.version.split()[0])
print("operating_system:", platform.system())
print("platform:", platform.platform())

for package_name in ("Pillow", "pytest"):
    try:
        print(f"{package_name}:", version(package_name))
    except PackageNotFoundError:
        print(f"{package_name}: not installed")