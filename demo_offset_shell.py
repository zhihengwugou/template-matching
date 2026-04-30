from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import trimesh


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="参数化建模最简 PoC：对立方体/圆柱体做等距偏移（Offset）演示。"
    )
    parser.add_argument(
        "--method",
        choices=["normal", "boolean"],
        default="boolean",
        help="Offset 方法：normal=法线位移（快速），boolean=布尔法（更严格）。",
    )
    parser.add_argument(
        "--shape",
        choices=["box", "cylinder"],
        default="box",
        help="基础几何体类型：box=立方体，cylinder=圆柱体。",
    )
    parser.add_argument(
        "--offset",
        type=float,
        default=2.0,
        help="偏移距离（单位与模型一致，需为正数）。",
    )
    parser.add_argument(
        "--box-size",
        type=float,
        default=20.0,
        help="立方体边长（shape=box 时生效）。",
    )
    parser.add_argument(
        "--radius",
        type=float,
        default=8.0,
        help="圆柱半径（shape=cylinder 时生效）。",
    )
    parser.add_argument(
        "--height",
        type=float,
        default=20.0,
        help="圆柱高度（shape=cylinder 时生效）。",
    )
    parser.add_argument(
        "--sections",
        type=int,
        default=64,
        help="圆柱离散分段数（越大越圆滑）。",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="显示原始网格与偏移后网格。",
    )
    parser.add_argument(
        "--export-dir",
        type=Path,
        default=Path("offset_outputs"),
        help="导出 STL 文件目录。",
    )
    return parser.parse_args()


def create_base_mesh(args: argparse.Namespace) -> trimesh.Trimesh:
    """按参数创建基础几何体网格。"""
    if args.shape == "box":
        return trimesh.creation.box(extents=[args.box_size, args.box_size, args.box_size])

    return trimesh.creation.cylinder(
        radius=args.radius,
        height=args.height,
        sections=args.sections,
    )


def create_outer_mesh(args: argparse.Namespace) -> trimesh.Trimesh:
    """
    为布尔壳体法创建“外层”网格。

    说明：
    - box: 边长增加 2 * offset
    - cylinder: 半径增加 offset，高度增加 2 * offset
    """
    if args.shape == "box":
        outer_size = args.box_size + 2.0 * args.offset
        return trimesh.creation.box(extents=[outer_size, outer_size, outer_size])

    return trimesh.creation.cylinder(
        radius=args.radius + args.offset,
        height=args.height + 2.0 * args.offset,
        sections=args.sections,
    )


def offset_by_vertex_normals(mesh: trimesh.Trimesh, distance: float) -> trimesh.Trimesh:
    """
    最简 Offset：沿顶点法线方向平移顶点。

    说明：
    - 这是非常轻量的概念验证写法。
    - 在尖角/高曲率区域不保证严格“等距”，但便于快速理解 Offset 思路。
    """
    offset_mesh = mesh.copy()
    normals = offset_mesh.vertex_normals
    offset_mesh.vertices = offset_mesh.vertices + normals * distance
    return offset_mesh


def build_shell_by_boolean(
    base_mesh: trimesh.Trimesh,
    outer_mesh: trimesh.Trimesh,
) -> trimesh.Trimesh:
    """
    布尔法壳体：shell = outer - base。

    需要布尔引擎支持（此项目安装了 manifold3d，可作为 engine='manifold'）。
    """
    shell_mesh = trimesh.boolean.difference([outer_mesh, base_mesh], engine="manifold")
    if shell_mesh is None:
        raise RuntimeError("布尔差集返回空结果，请检查网格或布尔引擎。")
    if not isinstance(shell_mesh, trimesh.Trimesh):
        raise TypeError("布尔差集结果不是单个 Trimesh 对象。")
    return shell_mesh


def print_mesh_info(title: str, mesh: trimesh.Trimesh) -> None:
    bbox_min, bbox_max = mesh.bounds
    extents = mesh.extents
    print(f"\n=== {title} ===")
    print(f"顶点数: {len(mesh.vertices)}")
    print(f"面片数: {len(mesh.faces)}")
    print(f"是否封闭 (watertight): {mesh.is_watertight}")
    print(f"包围盒最小点: {np.round(bbox_min, 4)}")
    print(f"包围盒最大点: {np.round(bbox_max, 4)}")
    print(f"包围盒尺寸: {np.round(extents, 4)}")


def export_meshes(
    export_dir: Path,
    shape: str,
    offset: float,
    method: str,
    base_mesh: trimesh.Trimesh,
    offset_mesh: trimesh.Trimesh,
    shell_mesh: trimesh.Trimesh | None = None,
) -> None:
    export_dir.mkdir(parents=True, exist_ok=True)
    base_path = export_dir / f"{shape}_base.stl"
    offset_path = export_dir / f"{shape}_offset_{method}_{offset:.3f}.stl"
    base_mesh.export(base_path)
    offset_mesh.export(offset_path)
    print("\n=== 文件导出 ===")
    print(f"原始网格已导出: {base_path}")
    print(f"偏移网格已导出: {offset_path}")
    if shell_mesh is not None:
        shell_path = export_dir / f"{shape}_shell_boolean_{offset:.3f}.stl"
        shell_mesh.export(shell_path)
        print(f"壳体网格已导出: {shell_path}")


def show_scene(
    base_mesh: trimesh.Trimesh,
    offset_mesh: trimesh.Trimesh,
    shell_mesh: trimesh.Trimesh | None = None,
) -> None:
    base_vis = base_mesh.copy()
    offset_vis = offset_mesh.copy()
    base_vis.visual.face_colors = [0, 200, 0, 120]      # 绿色：原始网格
    offset_vis.visual.face_colors = [30, 100, 255, 120]  # 蓝色：偏移后网格
    scene = trimesh.Scene()
    scene.add_geometry(base_vis, node_name="原始网格")
    scene.add_geometry(offset_vis, node_name="偏移网格")
    if shell_mesh is not None:
        shell_vis = shell_mesh.copy()
        shell_vis.visual.face_colors = [255, 140, 0, 120]  # 橙色：布尔壳体
        scene.add_geometry(shell_vis, node_name="布尔壳体")
    scene.show()


def main() -> None:
    args = parse_args()

    if args.offset <= 0:
        raise ValueError("offset 必须大于 0。")

    print("开始执行：参数化建模 Offset 最简概念验证")
    print(f"基础几何体: {args.shape}")
    print(f"偏移距离: {args.offset}")
    print(f"Offset 方法: {args.method}")

    # 第一步：创建基础几何体网格（box 或 cylinder）
    base_mesh = create_base_mesh(args)
    print_mesh_info("原始网格信息", base_mesh)

    shell_mesh: trimesh.Trimesh | None = None

    # 第二步：根据方法生成偏移网格
    if args.method == "normal":
        offset_mesh = offset_by_vertex_normals(base_mesh, args.offset)
        print("\n提示：当前使用法线位移，速度快但几何严格性较弱。")
    else:
        # 布尔法：先构造外层网格，再做差集得到壳体。
        outer_mesh = create_outer_mesh(args)
        shell_mesh = build_shell_by_boolean(base_mesh, outer_mesh)
        offset_mesh = outer_mesh
        print("\n提示：当前使用布尔法，几何结果更严格。")
        print_mesh_info("布尔壳体网格信息", shell_mesh)

    print_mesh_info("偏移后网格信息", offset_mesh)

    if args.method == "normal":
        print("在尖角位置它不一定是严格数学等距壳体；建议使用 boolean 方法。")
    else:
        print("布尔壳体方式更适合工程上的壳体生成概念验证。")

    # 第三步：导出结果，便于在外部 CAD/3D 工具中检查
    export_meshes(
        args.export_dir,
        args.shape,
        args.offset,
        args.method,
        base_mesh,
        offset_mesh,
        shell_mesh,
    )

    # 第四步（可选）：可视化对比
    if args.show:
        show_scene(base_mesh, offset_mesh, shell_mesh)


if __name__ == "__main__":
    main()
