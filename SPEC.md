# Jade Glass Control — Interactive WebGL Spec

## 1. Concept & Vision

一个汽车座舱风格的玉石质感 UI 控件渲染器。用户可以实时调参，观察不同材质/几何参数对最终视觉效果的影响。目标是**所见即所得**的材质预览工具，界面本身也要有设计感。

整体氛围：深夜工业风 + 玉石温润感，像是一个精密仪器的中控面板。

---

## 2. Design Language

### Aesthetic
- 深色技术感 + 玉石高光点缀
- 参考：Tesla FSD UI / 天际线汽车仪表盘
- 冷静克制，关键地方有光感

### Color Palette
```
--bg:          #080a0e   深空背景
--panel:       #111318   控件面板
--panel-hover: #151820   面板悬停
--border:      #1e2432   边框/分隔
--border-bright:#2a3548  亮边框
--text:        #b8c4d4   主文字
--text-dim:    #4a5568   次要文字
--jade:        #2aaa50   玉石高光/强调
--jade-bright: #40e070   亮色高光
--jade-dark:   #1a7034   深色玉石
--accent:      #80ffcc   玻璃 rim/accent
--track:       #1a2030   滑杆轨道
--track-fill:  #1e3828   滑杆填充
```

### Typography
- 标题：系统衬线，15px，letter-spacing 0.04em
- 标签：系统无衬线，10px uppercase，letter-spacing 0.08em
- 数值：monospace，12px，jade-glow 色

### Layout
```
┌─────────────────────────────────┐
│  Title bar: 名称 + 简短描述       │
├─────────────────────────────────┤
│                                 │
│     WebGL Canvas (720×450)      │
│     自适应宽度，最大 720px         │
│                                 │
├─────────────────────────────────┤
│  [分组标签] Geometry | Material | │
│  [分组标签] Lighting | Advanced   │
├─────────────────────────────────┤
│  参数面板（分组显示）              │
│  每组 2 列 grid                  │
└─────────────────────────────────┘
```

---

## 3. Parameter Groups

### 3.1 Geometry（几何）— 6 parameters
| 参数 | 范围 | 默认 | 说明 |
|------|------|------|------|
| Aspect Ratio | 0.5–4.0 | 1.96 | 控件宽高比 |
| Control Scale | 0.3–2.0 | 1.00 | 控件相对画幅大小 |
| Corner Radius | 0.005–0.25 | 0.055 | 圆角半径 |
| Border Width | 0.0–0.025 | 0.0 | 控件边框宽度（预留） |
| Canvas Width | 320–1280 px | 720 | 画幅宽 |
| Canvas Height | 200–800 px | 450 | 画幅高 |

### 3.2 Material（材质）— 6 parameters
| 参数 | 范围 | 默认 | 说明 |
|------|------|------|------|
| IOR | 1.20–2.00 | 1.52 | 折射率 |
| Thickness | 0.005–0.20 | 0.060 | 中心厚度 |
| Jade Hue | -180–+180° | 0° | 玉石色相偏移 |
| Jade Saturation | 0.0–1.0 | 0.75 | 玉石饱和度 |
| Jade Lightness | 0.0–0.6 | 0.30 | 玉石明度 |
| Glassiness | 0.0–1.0 | 0.50 | 透射/反射比例 |

### 3.3 Lighting（光照）— 9 parameters
| 参数 | 范围 | 默认 | 说明 |
|------|------|------|------|
| SSS Strength | 0.0–2.0 | 0.65 | 次表面散射强度 |
| SSS Color R | 0–255 | 140 | SSS 红色通道 |
| SSS Color G | 0–255 | 211 | SSS 绿色通道 |
| SSS Color B | 0–255 | 50 | SSS 蓝色通道 |
| Specular Power | 4–128 | 32 | 高光锐度 |
| Specular Intensity | 0.0–1.0 | 0.30 | 高光强度 |
| Rim Intensity | 0.0–1.5 | 0.40 | 边缘光强度 |
| Light X | -1.0–1.0 | 0.55 | 光源 X 方向 |
| Light Y | -1.0–1.0 | 0.65 | 光源 Y 方向 |

### 3.4 Advanced（高级）— 6 parameters
| 参数 | 范围 | 默认 | 说明 |
|------|------|------|------|
| R Absorption | 0.0–8.0 | 3.20 | Beer-Lambert 红光吸收系数 |
| G Absorption | 0.0–8.0 | 0.45 | Beer-Lambert 绿光吸收系数 |
| B Absorption | 0.0–8.0 | 2.40 | Beer-Lambert 蓝光吸收系数 |
| Refraction Scale | 0.0–0.5 | 0.18 | 折射偏移缩放 |
| Vignette | 0.0–1.0 | 0.30 | 暗角强度 |
| BG Brightness | 0.0–2.0 | 1.00 | 背景亮度 |

---

## 4. Technical Architecture

### Rendering Pipeline
```
1. Procedural dark background (gradient + center light blob)
   OR user-uploaded image via texture sampler
2. Rounded-box SDF evaluation (sdRoundBox)
3. 2D normal from SDF gradient (central difference)
4. Fresnel (Schlick approximation)
5. Reflection ray → sample background
6. Refraction ray (Snell 2D) → sample background + Beer-Lambert
7. SSS thickness attenuation
8. Phong specular
9. Rim light (Fresnel-based edge glow)
10. Ambient + tone remap + gamma correction
```

### UI Architecture
- 纯原生 HTML/CSS/JS，单文件，无构建步骤
- 参数分组通过 Tab 切换面板实现
- 每个滑杆：`<input type="range">` + 数值显示
- Canvas resize：监听 canvas width/height 滑杆，shader 自适应分辨率
- 渲染：滑杆 change 时即时重绘（requestAnimationFrame 防抖）

### File Structure
```
jade-glass-control/
├── index.html    # 完整单文件实现 (1047 lines)
├── SPEC.md       # 本文档
├── README.md     # 项目文档
└── CHANGELOG.md  # 变更日志
```

---

## 5. Implementation Phases

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1 | 界面框架 + 深色主题 + Canvas 基础渲染 | ✅ DONE |
| Phase 2 | Geometry 参数组（6个滑杆）+ SDF/法线计算 | ✅ DONE |
| Phase 3 | Material 参数组（6个滑杆）+ Fresnel/Beer-Lambert | ✅ DONE |
| Phase 4 | Lighting 参数组（9个滑杆）+ SSS/Specular/Rim | ✅ DONE |
| Phase 5 | Advanced 参数组（6个滑杆）+ 精细调优 | ✅ DONE |
| Phase 6 | Tab 切换 + 响应式布局 + 细节打磨 | ✅ DONE |

**All 6 phases are fully implemented.** Total: 30 sliders (6+6+9+6+3 background controls).

---

## 6. Shader Uniforms

The WebGL fragment shader receives these uniforms:

| Uniform | Type | Source |
|---------|------|--------|
| u_res | vec2 | Canvas pixel resolution |
| u_ar | float | Aspect ratio |
| u_scale | float | Control scale |
| u_radius | float | Corner radius |
| u_border | float | Border width (reserved) |
| u_ior | float | IOR |
| u_hue | float | Jade hue shift |
| u_sat | float | Jade saturation |
| u_light | float | Jade lightness |
| u_thick | float | Thickness |
| u_glass | float | Glassiness |
| u_sss | float | SSS strength |
| u_sss_color | vec3 | SSS color (normalized 0-1) |
| u_spec_p | float | Specular power |
| u_spec_i | float | Specular intensity |
| u_rim | float | Rim intensity |
| u_lx | float | Light X direction |
| u_ly | float | Light Y direction |
| u_abs_r | float | R absorption |
| u_abs_g | float | G absorption |
| u_abs_b | float | B absorption |
| u_refr | float | Refraction scale |
| u_vign | float | Vignette |
| u_bgb | float | Background brightness |
| u_seed | float | Random seed (for dithering) |
| u_bg_tex | sampler2D | Background image texture |
| u_bg_type | float | BG type: 0=procedural, 1=texture |