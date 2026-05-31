# Ralph Plan — Jade Glass Control

## 目标
对 Jade Glass Control WebGL 半透明控件项目进行重新评估，发现问题并修复，建立完整的项目文档体系。

## 项目背景
- 汽车座舱风格玉石质感 UI 控件渲染器
- WebGL 1.0 实现，包含 Fresnel/Snell/SSS/Phong 光照模型
- 30 个实时参数滑杆，89/89 测试通过
- 当前问题：SPEC.md 过期，移动端体验差，无预设系统，无 WebGL 2.0

## 特性依赖图

| 特性 | 依赖 | 完成标准 |
|------|------|----------|
| 特性1：更新 SPEC.md + 建立完整文档 | 无 | SPEC.md 准确反映当前实现状态，所有参数与代码一致 |
| 特性2：预设系统（Preset Save/Load） | 无 | 用户可保存当前参数为预设，可从预设恢复，支持至少 5 个预设位 |
| 特性3：移动端触摸优化 | 无 | 滑杆在 iOS/Android 触摸操作正常，双击滑杆可重置默认值 |
| 特性4：WebGL 2.0 自动降级 | 特性1 | 检测 WebGL 2.0，可使用时启用 MSAA + MRT，无 WebGL 2.0 时优雅降级到 WebGL 1.0 |
|| 特性5：PNG 导出功能 | 特性2 | 一键将当前 Canvas 导出为 PNG 文件下载 |
| 特性6：玉石材质视觉检测 | 无 | 使用已知参数的基准图像验证 jade 渲染输出是否正确（SDF/法线/SSS/rim 光照效果可量化检测）|

## 并行层级

- **L1**：特性1（文档更新）+ 特性2（预设系统）+ 特性3（移动端优化）+ 特性6（玉石视觉检测）← 当前
- **L2**：特性4（WebGL 2.0）+ 特性5（PNG 导出）

## 每个特性的实现步骤

### 特性1：更新 SPEC.md + 建立完整文档
- 步骤1：读取 index.html 中的所有 30 个参数名称、范围、默认值
- 步骤2：对比现有 SPEC.md，标记哪些描述已过时
- 步骤3：更新 SPEC.md 的参数表格，使与代码一致
- 步骤4：更新 README.md 的 Implementation Status 部分
- 步骤5：建立 CHANGELOG.md 记录本次迭代的改动
- 完成标准：任何人读 SPEC.md 都能准确了解当前实现状态

### 特性2：预设系统（Preset Save/Load）
- 步骤1：设计预设数据结构（JSON，包含 30 个参数值 + 预设名称）
- 步骤2：在 UI 中添加预设管理区域（保存/加载/删除按钮）
- 步骤3：使用 localStorage 持久化存储预设
- 步骤4：预设切换时平滑动画过渡（0.3s lerp）
- 步骤5：提供 3 个内置默认预设（"翠绿玉石"/"深海玻璃"/"琥珀透光"）
- 完成标准：用户可保存当前参数，可从预设恢复，刷新页面后预设仍然存在

### 特性3：移动端触摸优化
- 步骤1：测试 iOS Safari/Android Chrome 上的滑杆行为
- 步骤2：给 `<input type="range">` 添加 `touch-action: manipulation` CSS
- 步骤3：实现双击滑杆重置默认值的功能（prevent double-tap zoom 同时实现双击）
- 步骤4：增大滑杆 thumb 的触摸区域（至少 44x44pt）
- 步骤5：验证触摸操作不触发页面缩放
- 完成标准：在 iOS Safari 和 Android Chrome 上滑杆操作流畅，无误触发缩放

### 特性4：WebGL 2.0 自动降级
- 步骤1：在 index.html 头部添加 WebGL 版本检测
- 步骤2：如果 WebGL 2.0 可用，使用 `gl.getExtension('OES_texture_float_linear')` 和 4x MSAA
- 步骤3：如果只有 WebGL 1.0，使用现有的单采样路径
- 步骤4：在 UI 底部显示当前 WebGL 版本标识
- 步骤5：确保两种模式的渲染结果视觉一致（允许性能差异）
- 完成标准：有 WebGL 2.0 的设备自动使用 2.0，fallback 设备使用 1.0，无任何用户可感知的行为差异

### 特性5：PNG 导出功能
- 步骤1：在 UI 添加 "Export PNG" 按钮
- 步骤2：使用 `canvas.toDataURL('image/png')` 获取图像数据
- 步骤3：创建隐藏的 `<a download="jade-glass.png">` 并触发点击
- 步骤4：文件名包含当前参数预设名或时间戳
- 步骤5：添加复制到剪贴板功能（使用 Clipboard API）
- 完成标准：点击导出按钮，PNG 文件自动下载到本地

### 特性6：玉石材质视觉检测
- 步骤1：建立标准测试场景（参数已知，预期输出可计算）
  - 使用默认参数渲染 → 保存基准图像 jade_baseline.png
  - 建立 `tests/test_jade_material.py`，包含：
    - 中心点亮度检测（玉石应有高光亮点）
    - 边缘 rim 光检测（边缘应比中心暗/亮，有明确 rim 边界）
    - SSS 透光检测（设置 SSS=2.0，颜色极端值，验证边缘是否透出 SSS 色彩）
    - Corner radius 检测（圆角半径调到 0.25，验证四角是否平滑）
    - Jade hue 旋转检测（hue=+180°，颜色应反转）
- 步骤2：使用 `gl.readPixels` 读取关键像素值（中心点、边缘点、角点）
- 步骤3：与 PyTorch 参考实现（jade_demo.py）输出对比，误差 < 5%
- 步骤4：将基准图像和参数快照 commit 到 git
- 完成标准：`pytest tests/test_jade_material.py` 通过，jade 渲染效果可量化验证