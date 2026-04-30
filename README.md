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
- `demo_offset_shell.py`：Offset 壳体 PoC（支持 `normal` 法线位移与更严格 `boolean` 布尔法）
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

### 2) Offset 壳体生成（支持 normal / boolean）

严格布尔法（推荐，几何更严格）：

```bash
python3 demo_offset_shell.py --shape box --offset 2.0 --method boolean
```

圆柱体（布尔法）：

```bash
python3 demo_offset_shell.py --shape cylinder --radius 8 --height 20 --offset 1.5 --method boolean
```

法线位移法（快速对照）：

```bash
python3 demo_offset_shell.py --shape box --offset 2.0 --method normal
```

可视化对比：

```bash
python3 demo_offset_shell.py --shape box --offset 2.0 --method boolean --show
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

- `normal` 方法：沿顶点法线位移，速度快，适合快速验证思路。  
- `boolean` 方法：通过 `outer - base` 生成壳体，几何更严格，推荐用于当前概念验证。
- 布尔法会额外导出壳体网格，例如：
  - `offset_outputs/box_shell_boolean_2.000.stl`
  - `offset_outputs/cylinder_shell_boolean_1.500.stl`
