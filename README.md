# template-matching

一个用于学习与验证 3D 模型处理流程的微型项目，包含：

- 基于 `trimesh` 的 STL 模板匹配（ICP）最简 Demo
- 参数化建模概念验证：立方体/圆柱体的最简 Offset（壳体生成）Demo
- STL 可视化查看脚本

## 环境要求

- Python 3.10+（3.11 已验证）

## 安装依赖

```bash
python3 -m pip install -r requirements.txt
```

## 项目文件说明

- `demo_icp.py`：模板匹配与基础对齐示例
- `demo_offset_shell.py`：Offset 壳体最简 PoC（法线位移）
- `view_stl.py`：查看 STL 文件
- `封     雅文.stl`：模板 STL

## 运行方式

### 1) 模板匹配（ICP）

```bash
python3 demo_icp.py
```

可视化对比：

```bash
python3 demo_icp.py --show
```

### 2) Offset 壳体生成（最简）

立方体：

```bash
python3 demo_offset_shell.py --shape box --offset 2.0
```

圆柱体：

```bash
python3 demo_offset_shell.py --shape cylinder --radius 8 --height 20 --offset 1.5
```

可视化对比：

```bash
python3 demo_offset_shell.py --shape box --offset 2.0 --show
```

### 3) 查看导出的 STL

默认查看：

```bash
python3 view_stl.py
```

指定文件查看：

```bash
python3 view_stl.py --stl offset_outputs/box_base.stl
```

## 说明

当前 Offset 实现为“沿顶点法线位移”的最简概念验证，适合快速验证思路。  
在尖角或高曲率区域，它不一定是严格数学意义上的等距壳体；后续可升级为 SDF 或布尔运算方案。
