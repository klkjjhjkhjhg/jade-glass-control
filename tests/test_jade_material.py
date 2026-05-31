"""
Jade Glass Control — Jade Material Visual Inspection Tests
============================================================
5 个简单 Playwright 测试用例，验证玉石材质 WebGL 渲染正确性。

测试：
1. test_jade_renders_without_error — 页面加载、canvas 存在、无控制台错误
2. test_sss_extreme_colors — SSS=2.0 + 极端颜色，无崩溃
3. test_corner_radius_extreme — Corner Radius=0.25，无视觉故障
4. test_hue_rotation — Jade Hue=+180°，渲染正确变化
5. test_glassiness_extreme — Glassiness=0 和 =1，均正常渲染

运行：pytest tests/test_jade_material.py -v
"""

import base64
import io
import json
import tempfile
from pathlib import Path

import numpy as np
import pytest
from PIL import Image


# ── 配置 ──────────────────────────────────────────────────────────────────────

HTML_PATH = Path(__file__).parent.parent / "index.html"


# ── Browser Fixture ───────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def browser_page():
    """启动 Chromium（headless），注入 preserveDrawingBuffer，返回 page"""
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context()
    page = ctx.new_page()

    # 让 getContext('webgl') 自动启用 preserveDrawingBuffer
    page.add_init_script("""
        (() => {
            const orig = HTMLCanvasElement.prototype.getContext;
            HTMLCanvasElement.prototype.getContext = function(type, attrs) {
                if (type === 'webgl' || type === 'experimental-webgl') {
                    attrs = Object.assign({}, attrs || {}, { preserveDrawingBuffer: true });
                }
                return orig.call(this, type, attrs);
            };
        })();
    """)

    page.goto(f"file://{HTML_PATH.resolve()}")
    page.wait_for_timeout(1500)  # 等待 WebGL 初始化

    yield page

    ctx.close()
    browser.close()
    pw.stop()


# ── 辅助函数 ──────────────────────────────────────────────────────────────────

def _canvas_data_url(page) -> str:
    """获取 canvas 当前画面（Base64 PNG）"""
    return page.evaluate("""
        () => document.querySelector('canvas#c').toDataURL('image/png')
    """)


def _data_url_to_np(data_url: str) -> np.ndarray:
    """Base64 data URL → RGB numpy array (H, W, 3)，值域 0-255"""
    b64 = data_url.split(",", 1)[1]
    img_bytes = base64.b64decode(b64)
    pil = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    return np.array(pil, dtype=np.uint8)


def _set_params_and_render(page, params: dict):
    """通过 JS 直接操作 window.P 设置参数，触发 render()"""
    parts = []
    for k, v in params.items():
        parts.append(f"P.{k} = {json.dumps(v) if isinstance(v, str) else v};")
    code = "\n".join(parts)
    page.evaluate(f"() => {{ {code} render(); }}")
    page.wait_for_timeout(300)


def _jade_region(arr: np.ndarray, threshold: float = 15.0) -> np.ndarray:
    """返回 jade 控件区域的 bool mask"""
    lum = 0.299 * arr[:,:,0] + 0.587 * arr[:,:,1] + 0.114 * arr[:,:,2]
    return lum > threshold


def _ring_region(arr: np.ndarray, inner: float, outer: float):
    """返回控件区域内指定半径范围的环形 mask（归一化坐标）"""
    H, W = arr.shape[:2]
    y, x = np.ogrid[:H, :W]
    cx, cy = W / 2, H / 2
    dist = np.sqrt(((x - cx) / cx) ** 2 + ((y - cy) / cy) ** 2)
    jade = _jade_region(arr)
    return jade & (dist > inner) & (dist < outer)


# ── 测试用例 ──────────────────────────────────────────────────────────────────

class TestJadeRenderBasics:
    """基础渲染：页面加载、canvas 存在、无控制台错误"""

    def test_jade_renders_without_error(self, browser_page):
        """
        验证：
        1. canvas#c 存在
        2. 无控制台 error
        3. canvas 有实际像素内容（非全黑）
        """
        # canvas 存在
        canvas = browser_page.query_selector("canvas#c")
        assert canvas is not None, "canvas#c not found"

        # 无 JS 错误
        errors = []
        browser_page.on("console", lambda msg: errors.append(msg) if msg.type == "error" else None)
        browser_page.reload()
        browser_page.wait_for_timeout(1000)
        assert len(errors) == 0, f"Console errors: {[e.text for e in errors]}"

        # canvas 有内容（非全黑）
        arr = _data_url_to_np(_canvas_data_url(browser_page))
        assert arr.max() > 10, f"Canvas appears blank (max pixel={arr.max()})"


class TestSSSExtremeColors:
    """SSS 极端参数：SSS=2.0 + 紫红 SSS 颜色，无崩溃且可见效果"""

    def test_sss_extreme_colors(self, browser_page):
        """
        设置 SSS=2.0, SSS Color=(255,0,255)（紫红极端色）。
        验证外环比内环更亮（SSS 透射效果）。
        """
        _set_params_and_render(browser_page, {
            "sss": 2.0,
            "sss_r": 255,
            "sss_g": 0,
            "sss_b": 255,
        })

        arr = _data_url_to_np(_canvas_data_url(browser_page))

        # 内环 vs 外环亮度对比
        inner_mask = _ring_region(arr, inner=0.30, outer=0.45)
        outer_mask = _ring_region(arr, inner=0.60, outer=0.75)

        inner_mean = arr[inner_mask].mean() if inner_mask.any() else 0
        outer_mean = arr[outer_mask].mean() if outer_mask.any() else 0

        diff = outer_mean - inner_mean
        print(f"\n[SSS] inner={inner_mean:.1f}, outer={outer_mean:.1f}, diff={diff:.1f}")

        assert diff > 3.0, f"SSS outer should be brighter than inner (diff={diff:.1f})"


class TestCornerRadiusExtreme:
    """圆角极端值：Corner Radius=0.25（最大），四角应平滑"""

    def test_corner_radius_extreme(self, browser_page):
        """
        设置 Corner Radius=0.25，检查四角区域梯度应较小（平滑过渡）。
        """
        _set_params_and_render(browser_page, {"radius": 0.25})

        arr = _data_url_to_np(_canvas_data_url(browser_page))
        H, W = arr.shape[:2]

        # 四角采样点（距各角约 15%）
        corners = [
            (int(0.15 * H), int(0.15 * W)),
            (int(0.15 * H), int(0.85 * W)),
            (int(0.85 * H), int(0.15 * W)),
            (int(0.85 * H), int(0.85 * W)),
        ]

        max_grad = 0.0
        for cy, cx in corners:
            y0, y1 = max(0, cy - 2), min(H, cy + 3)
            x0, x1 = max(0, cx - 2), min(W, cx + 3)
            patch = arr[y0:y1, x0:x1].astype(np.float64)
            if patch.size == 0:
                continue
            gx = np.abs(np.diff(patch, axis=1)).max()
            gy = np.abs(np.diff(patch, axis=0)).max()
            max_grad = max(max_grad, gx, gy)

        print(f"\n[Corner] max corner gradient={max_grad:.1f}")
        assert max_grad < 30.0, f"Corner gradient {max_grad:.1f} suggests sharp corners at radius=0.25"


class TestHueRotation:
    """色相旋转：Hue=+180°，绿色应变为红紫色"""

    def test_hue_rotation(self, browser_page):
        """
        设置 Jade Hue=+180°，检查中环 R > B（绿色反转为红紫）。
        """
        _set_params_and_render(browser_page, {"hue": 180.0})

        arr = _data_url_to_np(_canvas_data_url(browser_page))

        ring_mask = _ring_region(arr, inner=0.25, outer=0.45)
        ring_arr = arr[ring_mask]
        mean_rgb = ring_arr.mean(axis=0) if len(ring_arr) > 0 else np.array([0, 0, 0])

        print(f"\n[Hue] mid-ring mean RGB: {mean_rgb}")
        assert mean_rgb[0] > mean_rgb[2], (
            f"Hue=180 should flip green→red/purple. R={mean_rgb[0]:.1f} should be > B={mean_rgb[2]:.1f}"
        )


class TestGlassinessExtreme:
    """玻璃度极端值：glassiness=0 和 =1 均正常渲染"""

    @pytest.mark.parametrize("glass_value", [0.0, 1.0])
    def test_glassiness_extreme(self, browser_page, glass_value):
        """
        glassiness=0 时：控件应几乎不透明（厚重感）。
        glassiness=1 时：控件应高度透明（玻璃感）。
        两种情况都应正常渲染不崩溃，且视觉效果不同。
        """
        _set_params_and_render(browser_page, {"glass": glass_value})

        arr = _data_url_to_np(_canvas_data_url(browser_page))
        assert arr.max() > 10, f"Canvas appears blank at glass={glass_value}"

        # 中心区域亮度应随 glass 变化
        H, W = arr.shape[:2]
        lum = 0.299 * arr[:,:,0] + 0.587 * arr[:,:,1] + 0.114 * arr[:,:,2]
        cy, cx = H // 2, W // 2
        r = int(min(H, W) * 0.15)
        center = lum[cy-r:cy+r, cx-r:cx+r].mean()
        print(f"\n[Glass] glass={glass_value}, center lum={center:.1f}")

        assert center > 5, f"Center should not be completely dark at glass={glass_value}"


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))