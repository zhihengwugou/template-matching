from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import cKDTree
from trimesh.transformations import euler_matrix, translation_matrix


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="使用 trimesh ICP 的最小 STL 模板匹配示例。"
    )
    parser.add_argument(
        "--stl",
        type=Path,
        default=Path("封     雅文.stl"),
        help="模板 STL 文件路径。",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=5000,
        help="用于配准的每个网格采样点数量。",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="在可视化窗口中显示 source/target/aligned 三个网格。",
    )
    return parser.parse_args()


def build_known_transform() -> np.ndarray:
    # 构造“已知真值”刚体变换：先旋转再平移，用于生成待匹配模型。
    rotation = euler_matrix(
        np.deg2rad(25.0),
        np.deg2rad(-15.0),
        np.deg2rad(35.0),
        "sxyz",
    )
    translation = translation_matrix([40.0, -25.0, 30.0])
    return translation @ rotation


def rmse_nn(points_a: np.ndarray, points_b: np.ndarray) -> float:
    # 通过最近邻距离计算点集 A 到点集 B 的 RMSE。
    tree = cKDTree(points_b)
    distances, _ = tree.query(points_a, k=1)
    return float(np.sqrt(np.mean(distances**2)))


def main() -> None:
    args = parse_args()
    if not args.stl.exists():
        raise FileNotFoundError(f"未找到 STL 文件: {args.stl}")

    target_mesh = trimesh.load_mesh(args.stl)
    if not isinstance(target_mesh, trimesh.Trimesh):
        raise TypeError("加载结果不是单个 Trimesh 网格对象。")

    print("=== 网格信息 ===")
    print(f"模板文件: {args.stl}")
    print(f"顶点数: {len(target_mesh.vertices)}")
    print(f"面片数: {len(target_mesh.faces)}")
    print(f"是否封闭 (watertight): {target_mesh.is_watertight}")

    # 通过已知变换把模板变成“待匹配 source”，原网格保留为 target。
    known_transform = build_known_transform()
    source_mesh = target_mesh.copy()
    source_mesh.apply_transform(known_transform)

    # 从 source/target 表面采样点云，作为 ICP 输入。
    target_points = target_mesh.sample(args.samples)
    source_points = source_mesh.sample(args.samples)

    before_rmse = rmse_nn(source_points, target_points)

    estimated_transform, transformed_points, cost = trimesh.registration.icp(
        source_points,
        target_points,
        max_iterations=100,
        scale=False,
    )
    # 本示例不直接使用 transformed_points，保留变量便于后续扩展调试。
    _ = transformed_points

    # 将估计变换作用到 source，得到对齐后的网格。
    aligned_mesh = source_mesh.copy()
    aligned_mesh.apply_transform(estimated_transform)
    aligned_points = aligned_mesh.sample(args.samples)
    after_rmse = rmse_nn(aligned_points, target_points)

    # 对比“估计变换”与“真实逆变换”的矩阵差异。
    expected_recovery = np.linalg.inv(known_transform)
    delta = np.linalg.norm(expected_recovery - estimated_transform)

    print("\n=== 配准结果 ===")
    print(f"ICP 前 RMSE: {before_rmse:.6f}")
    print(f"ICP 后 RMSE: {after_rmse:.6f}")
    print(f"ICP 残差 cost: {float(cost):.6f}")
    print(f"||inv(known) - estimated||_F: {delta:.6f}")

    print("\n期望恢复变换（已知变换的逆矩阵）:")
    print(expected_recovery)
    print("\nICP 估计变换:")
    print(estimated_transform)

    if args.show:
        # 绿色: target，红色: 原始 source，蓝色: ICP 对齐后结果。
        target_vis = target_mesh.copy()
        source_vis = source_mesh.copy()
        aligned_vis = aligned_mesh.copy()

        target_vis.visual.face_colors = [0, 255, 0, 80]
        source_vis.visual.face_colors = [255, 0, 0, 80]
        aligned_vis.visual.face_colors = [0, 0, 255, 80]

        scene = trimesh.Scene()
        scene.add_geometry(target_vis, node_name="target_green")
        scene.add_geometry(source_vis, node_name="source_red")
        scene.add_geometry(aligned_vis, node_name="aligned_blue")
        scene.show()


if __name__ == "__main__":
    main()
