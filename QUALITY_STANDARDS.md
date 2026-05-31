# Jade Glass Control — Quality Standards

## 1. Performance Standards

### 1.1 Frame Rate
| Metric | Target | Minimum | Critical |
|--------|--------|---------|----------|
| Idle FPS | ≥60 fps | ≥45 fps | <30 fps |
| Slider drag FPS | ≥60 fps | ≥40 fps | <30 fps |
| Initial render time | <100ms | <200ms | ≥500ms |

测量方法：开启 WebGL inspector，监控 `gl.getParameter(gl.GPUInfo.RENDERER)` 并使用 `requestAnimationFrame` 计数。

### 1.2 Memory
| Metric | Target | Maximum |
|--------|--------|---------|
| JS heap (idle) | <50 MB | 100 MB |
| GPU memory | <20 MB | 50 MB |
| Texture upload | <2 MB/frame | 5 MB/frame |

### 1.3 Load Performance
| Metric | Target | Maximum |
|--------|--------|---------|
| First paint | <500ms | 1000ms |
| WebGL init | <200ms | 500ms |
| Full interactive | <1000ms | 2000ms |

---

## 2. Visual Quality Standards

### 2.1 Rendering Accuracy
WebGL shader 输出必须与 PyTorch 参考实现（`jade_demo.py`）在相同参数下视觉一致。

**验收标准（肉眼看不出差异）：**
- 背景渐变：无色带（banding）
- 控件边缘：抗锯齿 smoothstep，过渡柔和
- Fresnel 效果：边缘反射强度正确（越靠近掠射角反射越强）
- SSS 效果：透射光柔和，无硬边界
- 高光：中心亮、边缘暗的 Phong 高光形状正确

### 2.2 Color Accuracy
| 参数 | 预期效果 |
|------|---------|
| Jade Hue=0° | 纯绿色 |
| SSS Color | 透射光颜色正确反映 RGB 三通道 |
| Rim Light | 边缘发出翡翠色发光 |

### 2.3 Shader Correctness
- 无 WebGL console 错误
- 无 shader 编译警告
- uniform 绑定正确（无 `gl.INVALID_VALUE`）
- 纹理采样坐标 Y 轴翻转正确（WebGL bottom-up）

### 2.4 Edge Cases
| 场景 | 预期行为 |
|------|---------|
| 极端 aspect ratio (0.5 或 4.0) | 控件不变形，渲染正常 |
| Corner radius = 0 | 正常矩形，无 crash |
| IOR = 1.0 (无折射) | 折射偏移为 0，渲染稳定 |
| SSS Strength = 0 | 无透射光，控件正常显示 |
| BG 上传失败 | 回退到 procedural 背景，不 crash |

---

## 3. UI/UX Standards

### 3.1 Responsiveness
- 窗口 resize 后 100ms 内重绘
- 滑杆拖动时实时重绘（无延迟感）
- Tab 切换 <50ms

### 3.2 Accessibility
- 所有滑杆有对应的 `<label>` 或 `aria-label`
- 颜色对比度 ≥4.5:1（深色主题本身满足）
- 支持键盘导航（Tab 切换控件）

### 3.3 Browser Compatibility
| Browser | 最低版本 | 测试项 |
|---------|---------|--------|
| Chrome | 90+ | 完整功能 |
| Firefox | 88+ | 完整功能 |
| Safari | 14+ | 完整功能（macOS） |
| Mobile Chrome | 90+ | 基础功能（不要求完美） |

---

## 4. Code Quality Standards

### 4.1 JavaScript
- **无 lint 错误**（使用 ES5 兼容语法，WebGL 1.0）
- **无全局变量污染**（所有变量用 `const`/`let`，避免隐式全局）
- **uniform 绑定验证**：每个 uniform 在 render() 前必须存在
- **texture 绑定**：每次 render 前正确绑定纹理单元

### 4.2 GLSL Shader
- **编译零错误**：`getShaderParameter(gl.COMPILE_STATUS)` 必须为 true
- **无精度警告**：对 `highp` float 使用有充分理由
- **除零保护**：所有分母有 `max(..., 0.001)` 保护

### 4.3 HTML/CSS
- **有效 HTML**：无未闭合标签
- **CSS 变量**：所有颜色使用 CSS 变量，便于主题替换
- **响应式**：500px 以下宽度单列布局

---

## 5. Regression Gates

每次更新必须通过以下检查项才能合并/发布：

```
✅ Performance:
   - Idle FPS ≥ 45 (在 720×450 canvas 下测量)
   - Slider drag FPS ≥ 40
   - Initial render < 200ms

✅ Visual:
   - Shader compiles without errors
   - No WebGL errors in console
   - BG image upload → works, no CORS errors
   - BG image clear → returns to procedural

✅ Functionality:
   - All 30 sliders update render in real-time
   - Tab switching works (4 tabs)
   - Canvas resize (cw/ch sliders) works
   - BG file input works

✅ Code:
   - No syntax errors
   - All uniform locations resolved (not null)
   - Texture bound before sampling
```

---

## 6. Optimization Targets

### 6.1 Shader Optimization
- **指令数** < 500 GLSL instructions（fragment shader）
- **纹理采样** 每人像素 ≤ 2 次（BG texture only）
- **分支** 避免在 inner loop 中使用 if

### 6.2 JS Optimization
- **无每帧 GC**：避免在 render loop 中创建新对象
- **uniform 缓存**：避免每帧 `getUniformLocation` 调用
- **批量绑定**：同类 uniform 批量 set

### 6.3 Target FPS Profile
```
Canvas 720×450, Apple M1:
  Idle:  60 fps (16.7ms frame budget)
  Drag:  60 fps (16.7ms frame budget)

Canvas 1280×800:
  Idle:  60 fps
  Drag:  ≥45 fps
```

---

## 7. Test Artifacts

测试输出保存在 `test_results/` 目录：
```
test_results/
├── performance/
│   ├── fps_log.json          # FPS 测量数据
│   └── profile.json          # 性能 profile
├── visual/
│   ├── screenshot_baseline/ # 参考截图
│   └── screenshot_latest/    # 最新截图
└── reports/
    ├── quality_report.html   # 质量报告
    └── regression_log.txt    # 回归记录
```

---

*Last updated: 2026-05-31*