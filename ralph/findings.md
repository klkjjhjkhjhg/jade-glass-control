# Ralph Findings — Jade Glass Control

## 特性1：更新 SPEC.md + 建立完整文档

### 评估结果：✅ 完成

### 发现

**文档过期问题**：原有 SPEC.md 的 "Implementation Phases" 部分将 Phase 2–6 标记为未实现，但实际代码已完整实现所有 6 个阶段。

**参数不完整**：原有文档缺失 Canvas Width/Height 参数，且多个参数的范围/默认值与实际代码不符：
- Canvas Width: 文档写 100–800，实际 320–1280
- Canvas Height: 文档写 62–500，实际 200–800
- Border Width: 文档写 0.0–0.02，实际 0.0–0.025
- Rim Intensity: 文档写 0.0–1.0，实际 0.0–1.5
- SSS Color: 文档写 0.0–1.0 per channel，实际 0–255

**缺少 CHANGELOG.md**：项目没有变更日志文件。

### 执行的修复

1. **SPEC.md** — 全面更新：
   - Implementation Phases 全部标记为 ✅ DONE
   - 校正所有 30 个参数的范围、默认值
   - 新增 Canvas Width/Height 参数
   - 补充 Advanced 参数组说明
   - 新增 Shader Uniforms 表格

2. **README.md** — 更新实现状态：
   - 校正 Phase 状态为全部 DONE
   - 修正参数表格中的错误信息
   - 更新技术细节说明
   - 修正文件路径

3. **CHANGELOG.md** — 新建：
   - 记录本次迭代所有变更
   - 列出新增的 30 个参数
   - 记录已知问题

4. **tasks.md** — 更新特性1状态为 ✅完成

### 结论

文档现已准确反映当前实现状态。代码与文档一致，无需进一步修改。

---

## 特性2：预设系统（Preset Save/Load）

### 评估结果：✅ 完成

### 实现的功能

**1. 预设数据结构**
- 每个预设包含：`id`、`name`、`builtin`（布尔）、`params`（30个参数值的对象）
- 参数覆盖所有滑杆：几何（5）、材质（6）、光照（8）、高级（7）、画布（2）

**2. 3个内置不可删除预设**
| 名称 | 特点 |
|------|------|
| 翠绿玉石 | 默认参数，IOR=1.52，翠绿饱和色，SSS偏黄绿 |
| 深海玻璃 | IOR=1.33（玻璃），高SSS=1.2，冷蓝色调 |
| 琥珀透光 | IOR=1.6，暖色调，hue=+120°，琥珀橙黄色 |

**3. 用户自定义预设**
- 点击"💾 保存当前"弹出模态框，输入名称确认保存
- 保存时捕获当前所有30个参数值
- 存储在 localStorage，key = `jade-glass-presets`
- 预设列表中每个用户预设显示"加载"+"删除"按钮

**4. 平滑过渡动画**
- 预设加载时使用 300ms ease-out cubic 插值过渡
- 所有参数同步 lerp 变化，视觉平滑
- 使用 `requestAnimationFrame` 驱动动画循环

**5. UI设计**
- 新增"Preset"标签页，紧跟在 Lighting 之后
- 深色主题，与整体风格一致（jade-glow 绿色强调）
- 预设选择下拉菜单 + 加载/保存/删除按钮
- 保存模态框（点击遮罩关闭，支持回车保存）

### 技术实现

- **localStorage 持久化**：用户预设 JSON 序列化存储，无限寿命
- **动画**：ease-out cubic 缓动 (`t = 1 - (1-p)^3`)，比线性更自然
- **滑杆同步**：过渡过程中 `syncSlidersFromP()` 同步更新 UI 状态
- ** Delegated events**：预设列表使用事件委托，避免重复绑定

### 结论

预设系统完整实现所有需求：内置预设、用户保存/删除、localStorage 持久化、平滑过渡动画。代码结构清晰，可维护性强。

---

## 特性4：WebGL 2.0 自动降级

### 评估结果：✅ 完成

### 实现的功能

**1. WebGL 2.0 自动检测与降级**
- 首次尝试创建 `webgl2` context（wrapped in try/catch，防止浏览器安全限制抛异常）
- 如果成功：使用 WebGL 2.0，并检测 `OES_texture_float_linear` 扩展
- 如果失败：自动回退到 `webgl1` context
- 两种模式使用完全相同的 fragment shader 逻辑，渲染效果一致

**2. 版本标识 Badge**
- UI 顶部标题栏右侧显示 WebGL 版本徽标
- WebGL 2.0：绿色徽标显示 "WebGL 2.0"（有 float 扩展时显示 "+ float"）
- WebGL 1.0：灰蓝色徽标显示 "WebGL 1.0"

### 技术实现

- **检测逻辑**：`canvas.getContext('webgl2')` 优先，失败则回退 `webgl`
- **全局变量**：`glVersion`（1 或 2）、`ext_float`（boolean）供后续扩展使用
- **样式**：`.header-badge` 定位在 header 右侧，带边框圆角深色样式，v1 模式灰蓝色调
- **不破坏现有渲染**：fragment shader 在两种模式下完全相同，无行为差异

### 结论

WebGL 2.0 自动降级功能完整实现。设备支持 2.0 时自动启用并检测 float 线性扩展，不支持时平滑降级到 1.0。用户可通过 UI badge 直接看到当前运行模式。

---

## 特性6：玉石材质视觉检测

### 评估结果：✅ 完成

### 实现的功能

**测试文件**：`tests/test_jade_material.py`（基于 Playwright + PIL 像素分析）

**5 个测试用例**：

| 测试 | 方法 | 验证目标 |
|------|------|----------|
| `test_jade_renders_without_error` | 加载页面，检查 canvas 存在、无控制台错误、canvas 非全黑 | 基础渲染正常 |
| `test_sss_extreme_colors` | SSS=2.0 + SSS Color=(255,0,255)，对比内环/外环亮度 | SSS 透射效果可见 |
| `test_corner_radius_extreme` | Corner Radius=0.25，检测四角像素梯度 | 圆角平滑无锐角 |
| `test_hue_rotation` | Jade Hue=+180°，对比中环 R/B 比值 | 色相旋转正确（R>B） |
| `test_glassiness_extreme` | glassiness=0 和 =1（参数化测试），检测中心亮度 | 两种模式均正常渲染 |

**技术实现**：
- `preserveDrawingBuffer` 注入：拦截 `HTMLCanvasElement.prototype.getContext`，自动添加 `preserveDrawingBuffer: true` 到 WebGL 属性
- 像素分析：使用 `canvas.toDataURL()` + PIL/numpy 量化 RGB 数据
- 参数控制：通过 JS 直接操作 `window.P` 对象 + `render()` 触发重绘
- 区域采样：环形 mask（`_ring_region`）用于提取内环/外环/中环对比

### 技术细节

- **SSS 透射检测**：外环（60%-75%）亮度 - 内环（30%-45%）亮度 > 3.0
- **圆角平滑检测**：四角梯度最大值 < 30（梯度越小越平滑）
- **色相旋转检测**：Hue=180° 时中环（25%-45%）R > B
- **玻璃度检测**：两种模式均渲染非全黑（max > 10），中心亮度 > 5

### 结论

玉石材质视觉检测框架已建立。测试覆盖 SSS 透射、圆角渲染、色相旋转、玻璃度极端值等核心效果，方法为像素量化对比（非 baseline 图比较），能有效检测渲染错误和极端参数组合崩溃。

---

## 特性5：PNG 导出功能

### 评估结果：✅ 完成

### 实现的功能

**1. Export PNG 按钮**
- 位于 BG Image 行下方，与现有按钮风格一致（深色主题，jade-glow 绿色强调）
- 使用 `canvas.toDataURL('image/png')` 获取图像数据
- 创建隐藏的 `<a download="jade-glass-{timestamp}.png">` 并触发点击下载
- 文件名带时间戳避免覆盖

**2. Copy to Clipboard 按钮**
- 使用 Clipboard API (`navigator.clipboard.write([new ClipboardItem(...)])`)
- `canvas.toBlob()` 异步获取 PNG blob
- **graceful fallback**：如果 Clipboard API 不可用或失败，自动降级到 PNG 下载

### 技术实现

- **CSS**：复用了 `.bg-url-row` + `.bg-url-label` 样式（通过逗号分隔选择器），新增 `.export-row` + `.export-label`
- **按钮样式**：直接复用 `.bg-load-btn`（与 Reset 按钮一致，jade-dark 背景 jade-bright 文字）
- **HTML**：两个按钮紧跟在 BG Image 行之后，Export 标签区分功能组
- **降级机制**：catch 块捕获 Clipboard API 错误（常见于非 HTTPS 或浏览器限制），静默降级到下载而非抛错

### 结论

PNG 导出 + 剪贴板复制功能完整实现。UI 风格与现有设计一致，Clipboard API 不可用时平滑降级到下载，用户体验无断点。

---

## 特性3：移动端触摸优化

### 评估结果：✅ 完成

### 实现的功能

**1. touch-action CSS 优化**
- 给所有 `<input type="range">` 添加 `touch-action: manipulation`
- 防止双击缩放同时允许触摸滑动
- 应用于滑杆主元素（第 191 行）

**2. 双击滑杆重置功能**
- 给每个滑杆添加 `dblclick` 事件监听器
- 双击时将滑杆值重置为 `defaultValue`（HTML defaultValue 属性）
- 同时更新 P 对象、同步 label 文本、重绘 track fill、触发 render
- 复用相同的 canvas resize 逻辑处理 cw/ch 变化

**3. 增大触摸区域**
- WebKit thumb: `width: 24px; height: 24px`（从 13px 增大）
- margin-top 调整: `-10px`（从 `-5px`，保持 thumb 居中）
- `-webkit-tap-highlight-color: transparent` 消除触摸高亮
- Firefox thumb: 同步增大至 24×24

### 技术实现

- **CSS 变量**: thumb 尺寸增大约 85%，视觉上仍保持与深色主题一致
- **defaultValue**: HTMLInputElement 的 defaultValue 属性，保留 HTML 中定义的默认值
- **事件冒泡**: dblclick 事件在移动端通过 300ms 双击触发，与预设的 300ms 动画无冲突

### 结论

移动端触摸优化三项需求全部实现：touch-action CSS 防止缩放干扰、双击重置默认值、增大 thumb 触摸区域。优化不引入任何视觉变化，保持深色主题风格。