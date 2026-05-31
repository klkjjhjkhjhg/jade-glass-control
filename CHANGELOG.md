# Changelog — Jade Glass Control

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] — 2026-05-31

### Added
- **30 interactive parameter sliders** across 4 tab panels (Geometry, Material, Lighting, Advanced)
- **WebGL fragment shader** implementing jade glass rendering:
  - SDF-based rounded box geometry
  - Fresnel reflection (Schlick approximation)
  - Snell refraction with Beer-Lambert absorption
  - Subsurface scattering (SSS) with configurable color
  - Phong specular highlights
  - Fresnel-based rim lighting
  - Vignette and gamma correction
- **Tab-based UI** with 4 parameter groups
- **Background image upload** via file input (WebGL texture)
- **Procedural dark background** fallback with gradient and center glow
- **Canvas resize controls** (Width/Height sliders)
- **Slider track fill** visualization (CSS gradient)
- **Responsive layout** with 2-column grid (collapses to 1 column on mobile)

### Parameters Added This Iteration
- Geometry: Aspect Ratio, Control Scale, Corner Radius, Border Width, Canvas Width, Canvas Height
- Material: IOR, Thickness, Jade Hue, Jade Saturation, Jade Lightness, Glassiness
- Lighting: SSS Strength, SSS Color (R/G/B), Specular Power, Specular Intensity, Rim Intensity, Light X, Light Y
- Advanced: R/G/B Absorption, Refraction Scale, Vignette, BG Brightness

### Documentation
- `SPEC.md` — Complete design specification with all 30 parameters documented
- `README.md` — Full project documentation with implementation status
- `CHANGELOG.md` — This file

### Fixed
- SPEC.md Implementation Phases section now correctly shows all 6 phases as ✅ DONE
- Parameter ranges corrected to match actual implementation:
  - Canvas Width: 320–1280 (was 100–800)
  - Canvas Height: 200–800 (was 62–500)
  - Border Width: 0.0–0.025 (was 0.0–0.02)
  - Rim Intensity: 0.0–1.5 (was 0.0–1.0)
  - SSS Color: properly documented as 0–255 per channel (was 0.0–1.0)
- Canvas Width/Height parameters added to documentation (were missing)
- Correct parameter counts per group (6/6/9/6 = 27, plus 3 BG controls = 30 total)

### Known Limitations
- Border Width slider is non-functional (reserved for future stroke rendering feature)
- WebGL 1.0 only — no WebGL 2.0 features
- No preset save/load system (planned for future)
- No PNG export (planned for future)