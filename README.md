# Jade Glass Control — Project Documentation

## Project Overview

**Jade Glass Control** is a real-time WebGL renderer for semi-transparent/translucent UI controls with jade-like glass appearance. It simulates physically-based glass rendering including Fresnel reflection, Snell refraction, Beer-Lambert absorption, subsurface scattering (SSS), and Phong specular — all customizable via live parameter sliders.

Target use case: automotive cockpit-style UI material preview tool (e.g., Xiaomi's in-car infotainment system controls), where controls need to look premium with translucent jade/glass aesthetics.

---

## File Structure

```
jade-glass-control/
├── index.html     — Complete self-contained implementation (HTML/CSS/JS/WebGL, 1047 lines)
├── SPEC.md        — Design specification (source of truth for parameters & design language)
├── README.md      — This file
└── CHANGELOG.md   — Version history and change log
```

---

## Implementation Status

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1 | Interface framework + dark theme + Canvas + 30 sliders + BG image upload | ✅ DONE |
| Phase 2 | Geometry parameters + SDF/normal computation | ✅ DONE |
| Phase 3 | Material parameters + Fresnel/Beer-Lambert | ✅ DONE |
| Phase 4 | Lighting parameters + SSS/Specular/Rim | ✅ DONE |
| Phase 5 | Advanced parameters + fine-tuning | ✅ DONE |
| Phase 6 | Tab switching + responsive layout + polish | ✅ DONE |

**All phases are fully implemented.** The documentation has been updated to reflect the current implementation.

---

## Parameter Reference

### Geometry (6 parameters)
| Parameter | Range | Default |
|-----------|-------|---------|
| Aspect Ratio | 0.5–4.0 | 1.96 |
| Control Scale | 0.3–2.0 | 1.00 |
| Corner Radius | 0.005–0.25 | 0.055 |
| Border Width | 0.0–0.025 | 0.0 |
| Canvas Width | 320–1280 px | 720 |
| Canvas Height | 200–800 px | 450 |

### Material (6 parameters)
| Parameter | Range | Default |
|-----------|-------|---------|
| IOR | 1.20–2.00 | 1.52 |
| Thickness | 0.005–0.20 | 0.060 |
| Jade Hue | -180–+180° | 0° |
| Jade Saturation | 0.0–1.0 | 0.75 |
| Jade Lightness | 0.0–0.6 | 0.30 |
| Glassiness | 0.0–1.0 | 0.50 |

### Lighting (9 parameters)
| Parameter | Range | Default |
|-----------|-------|---------|
| SSS Strength | 0.0–2.0 | 0.65 |
| SSS Color R | 0–255 | 140 |
| SSS Color G | 0–255 | 211 |
| SSS Color B | 0–255 | 50 |
| Specular Power | 4–128 | 32 |
| Specular Intensity | 0.0–1.0 | 0.30 |
| Rim Intensity | 0.0–1.5 | 0.40 |
| Light X | -1.0–1.0 | 0.55 |
| Light Y | -1.0–1.0 | 0.65 |

### Advanced (6 parameters)
| Parameter | Range | Default |
|-----------|-------|---------|
| R Absorption | 0.0–8.0 | 3.20 |
| G Absorption | 0.0–8.0 | 0.45 |
| B Absorption | 0.0–8.0 | 2.40 |
| Refraction Scale | 0.0–0.5 | 0.18 |
| Vignette | 0.0–1.0 | 0.30 |
| BG Brightness | 0.0–2.0 | 1.00 |

**Total: 30 parameters** (across 4 tab panels + 3 background controls)

---

## Rendering Pipeline

The WebGL fragment shader executes this pipeline per pixel:

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

---

## Technical Details

- **Rendering**: Pure WebGL 1.0, no external dependencies or CDN
- **Shader**: Single fragment shader, ~200 lines GLSL
- **UI**: Native HTML/CSS/JS, single file, no build step
- **Canvas resize**: Controlled via Canvas Width/Height sliders, shader adapts to resolution
- **Render loop**: `requestAnimationFrame` debounced via slider `input` events
- **Background**: Procedural fallback or user-uploaded image (WebGL texture)
- **Tabs**: 4-tab panel switching (Geometry / Material / Lighting / Advanced)

---

## Running Locally

```bash
cd ~/Codes/jade-glass-control
python3 -m http.server 8080
# Open http://localhost:8080
```

Or open directly:
```
file:///Users/klkjjhjkhjhg/Codes/jade-glass-control/index.html
```

---

## Relationship to CarMaterial Project

This project is a **material preview/visualization tool** for the CarMaterial side project (`~/Codes/CarMaterial`). While CarMaterial focuses on car paint BRDF rendering with Vulkan, Jade Glass Control provides an interactive WebGL-based UI to preview jade/glass translucent material effects in isolation — useful for design iteration before integrating into the Vulkan pipeline.

---

## PyTorch Reference Implementation

A Python/PyTorch reference implementation exists at:
```
~/.hermes/hermes-agent/jade_demo.py
```

This implements the same jade glass rendering in PyTorch (CPU/CUDA/MPS) with the same parameters, useful for:
- Algorithm validation against the WebGL shader
- Batch rendering for documentation/test assets
- GPU-accelerated high-resolution output

```bash
# Run PyTorch version
python jade_demo.py --W 640 --H 400
python jade_demo.py --W 1280 --H 800 --bg your_image.png --out output.png
```

---

## Known Issues / Limitations

1. **WebGL 1.0 only** — no WebGL 2.0 features (no MRT, no MSAA in shader)
2. **Background image upload** — requires CORS-compliant image sources; local file upload via blob URL works
3. **Mobile browsers** — basic support but not optimized for touch (sliders work, but no touch-specific UI)
4. **Border Width** — currently a no-op (reserved for future stroke rendering)

---

## Last Updated

2026-05-31