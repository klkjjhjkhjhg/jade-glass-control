# Jade Glass Control — WebGL Deployment Guide

## Local Usage

Open the file directly in any modern browser:

```
file:///Users/klkjjhjkhjhg/.hermes/hermes-agent/jade_web/index.html
```

Or serve it locally:

```bash
cd /Users/klkjjhjkhjhg/.hermes/hermes-agent/jade_web
python3 -m http.server 8080
# Then open http://localhost:8080
```

---

## GitHub Pages Deployment

### Option A: Direct Upload (easiest)

1. Create a new **public** GitHub repository, e.g. `jade-webgl`
2. Go to **Settings → Pages → Source**
3. Select **Deploy from a branch** → `main` → `/ (root)`
4. Upload `index.html` to the `main` branch root
5. Wait 2 minutes — your page will be at:
   `https://YOUR_USERNAME.github.io/jade-webgl/`

### Option B: Existing Repo (gh-pages branch)

```bash
cd /path/to/your/repo

# Create gh-pages branch from main
git checkout -b gh-pages

# Copy the HTML file here (if not already in repo)
cp /Users/klkjjhjkhjhg/.hermes/hermes-agent/jade_web/index.html .

git add index.html
git commit -m "Add jade glass control WebGL demo"
git push origin gh-pages

# Enable GitHub Pages: Settings → Pages → Source = gh-pages branch
# URL: https://YOUR_USERNAME.github.io/REPO_NAME/
```

### Option C: GitHub Actions (automatic on every push)

Create `.github/workflows/deploy.yml` in your repo:

```yaml
name: Deploy Jade WebGL to GitHub Pages
on:
  push:
    branches: [main]
permissions:
  pages: write
  id-token: write
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to GitHub Pages
        uses: actions/configure-pages@v4
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: '.'
      - name: Deploy to GitHub Pages
        uses: actions/deploy-pages@v4
```

Then push `index.html` to `main` — GitHub Actions handles the rest.

---

## File Location

```
/Users/klkjjhjkhjhg/.hermes/hermes-agent/jade_web/index.html   ← single self-contained file
```

## Controls

| Slider         | Range            | Default | Description                      |
|---------------|-----------------|---------|----------------------------------|
| Aspect Ratio  | 0.5 – 4.0       | 1.96    | Control width / height ratio     |
| Control Scale | 0.3 – 2.0       | 1.00    | Relative size of the jade piece  |
| Corner Radius | 0.01 – 0.20     | 0.055   | Rounded corner radius             |
| IOR           | 1.20 – 2.00     | 1.52    | Index of refraction              |
| Jade Hue      | −180° – +180°   | 0°      | Hue shift of jade color          |
| Thickness     | 0.005 – 0.12    | 0.060   | Center thickness                 |
| SSS Strength  | 0.0 – 1.5       | 0.65    | Subsurface scattering intensity  |
| Glassiness    | 0.0 – 1.0       | 0.50    | Transmission / refraction mix    |

## Technical Notes

- Pure WebGL 1.0 — no external dependencies, no CDN required
- Fragment shader replicates the PyTorch pipeline: SDF, Fresnel, Beer-Lambert absorption, SSS, Phong specular
- Procedural background (no image assets needed)
- Real-time updates on every slider change
- Responsive: canvas auto-resizes to fit container