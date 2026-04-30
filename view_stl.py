import argparse
from pathlib import Path

import trimesh


def main() -> None:
    parser = argparse.ArgumentParser(description="查看 STL 文件的小工具")
    parser.add_argument(
        "--stl",
        type=Path,
        default=Path("offset_outputs/box_offset_2.000.stl"),
        help="要查看的 STL 文件路径",
    )
    args = parser.parse_args()

    if not args.stl.exists():
        raise FileNotFoundError(f"未找到 STL 文件: {args.stl}")

    mesh = trimesh.load(args.stl)
    mesh.show()


if __name__ == "__main__":
    main()
