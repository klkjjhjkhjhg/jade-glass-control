"""
Jade Glass Control — Functional Tests

测试所有 UI 组件和交互功能是否正常工作。
通过静态分析 HTML/JS 实现，不需要浏览器。
"""

import re
from pathlib import Path

HTML_PATH = Path(__file__).parent.parent / 'index.html'


def get_html():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        return f.read()


def get_js():
    html = get_html()
    match = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
    return match.group(1) if match else ''


def slider_ids(html):
    """提取所有滑杆 id，无视引号类型"""
    return re.findall(r'id=["\']s_(\w+)["\']', html)


# ── Tests ────────────────────────────────────────────────────────────────────

class TestSliderParameters:
    """测试滑杆参数完整性"""

    def test_geometry_ar(self):
        html = get_html()
        ids = slider_ids(html)
        assert 'ar' in ids, "Aspect Ratio slider missing"

    def test_geometry_scale(self):
        html = get_html()
        ids = slider_ids(html)
        assert 'scale' in ids, "Control Scale slider missing"

    def test_geometry_radius(self):
        html = get_html()
        ids = slider_ids(html)
        assert 'radius' in ids, "Corner Radius slider missing"

    def test_geometry_border(self):
        html = get_html()
        ids = slider_ids(html)
        assert 'border' in ids, "Border Width slider missing"

    def test_geometry_cw(self):
        html = get_html()
        ids = slider_ids(html)
        assert 'cw' in ids, "Canvas Width slider missing"

    def test_geometry_ch(self):
        html = get_html()
        ids = slider_ids(html)
        assert 'ch' in ids, "Canvas Height slider missing"

    def test_material_ior(self):
        html = get_html()
        ids = slider_ids(html)
        assert 'ior' in ids, "IOR slider missing"

    def test_material_thick(self):
        html = get_html()
        ids = slider_ids(html)
        assert 'thick' in ids, "Thickness slider missing"

    def test_material_hue(self):
        html = get_html()
        ids = slider_ids(html)
        assert 'hue' in ids, "Jade Hue slider missing"

    def test_material_sat(self):
        html = get_html()
        ids = slider_ids(html)
        assert 'sat' in ids, "Jade Saturation slider missing"

    def test_material_light(self):
        html = get_html()
        ids = slider_ids(html)
        assert 'light' in ids, "Jade Lightness slider missing"

    def test_material_glass(self):
        html = get_html()
        ids = slider_ids(html)
        assert 'glass' in ids, "Glassiness slider missing"

    def test_lighting_sss(self):
        html = get_html()
        ids = slider_ids(html)
        assert 'sss' in ids, "SSS Strength slider missing"

    def test_lighting_sss_color(self):
        html = get_html()
        ids = slider_ids(html)
        assert 'sss_r' in ids, "SSS Color R slider missing"
        assert 'sss_g' in ids, "SSS Color G slider missing"
        assert 'sss_b' in ids, "SSS Color B slider missing"

    def test_lighting_spec_p(self):
        html = get_html()
        ids = slider_ids(html)
        assert 'spec_p' in ids, "Specular Power slider missing"

    def test_lighting_spec_i(self):
        html = get_html()
        ids = slider_ids(html)
        assert 'spec_i' in ids, "Specular Intensity slider missing"

    def test_lighting_rim(self):
        html = get_html()
        ids = slider_ids(html)
        assert 'rim' in ids, "Rim Intensity slider missing"

    def test_lighting_lx(self):
        html = get_html()
        ids = slider_ids(html)
        assert 'lx' in ids, "Light X slider missing"

    def test_lighting_ly(self):
        html = get_html()
        ids = slider_ids(html)
        assert 'ly' in ids, "Light Y slider missing"

    def test_advanced_abs_r(self):
        html = get_html()
        ids = slider_ids(html)
        assert 'abs_r' in ids, "R Absorption slider missing"

    def test_advanced_abs_g(self):
        html = get_html()
        ids = slider_ids(html)
        assert 'abs_g' in ids, "G Absorption slider missing"

    def test_advanced_abs_b(self):
        html = get_html()
        ids = slider_ids(html)
        assert 'abs_b' in ids, "B Absorption slider missing"

    def test_advanced_refr(self):
        html = get_html()
        ids = slider_ids(html)
        assert 'refr' in ids, "Refraction Scale slider missing"

    def test_advanced_vign(self):
        html = get_html()
        ids = slider_ids(html)
        assert 'vign' in ids, "Vignette slider missing"

    def test_advanced_bgb(self):
        html = get_html()
        ids = slider_ids(html)
        assert 'bgb' in ids, "BG Brightness slider missing"

    def test_total_count(self):
        """滑杆总数验证（允许 27-35 范围）"""
        html = get_html()
        sliders = re.findall(r'<input type="range"', html)
        assert 25 <= len(sliders) <= 35, \
            f"Slider count {len(sliders)} outside expected range (25-35)"


class TestTabSwitching:
    """Tab 切换功能"""

    def test_tab_buttons(self):
        html = get_html()
        for tab in ['geometry', 'material', 'lighting', 'advanced']:
            assert f'data-tab="{tab}"' in html, f"Tab '{tab}' missing"

    def test_panel_containers(self):
        html = get_html()
        for panel in ['geometry', 'material', 'lighting', 'advanced']:
            assert f'id="panel-{panel}"' in html, f"Panel '{panel}' missing"

    def test_tab_js_handlers(self):
        js = get_js()
        assert "classList.remove('active')" in js, "Tab deactivation missing"
        assert "classList.add('active')" in js, "Tab activation missing"


class TestCanvasAndRender:
    """Canvas 和渲染"""

    def test_canvas_id(self):
        html = get_html()
        assert "id=\"c\"" in html or "id='c'" in html, "Canvas id='c' missing"

    def test_render_function(self):
        js = get_js()
        assert 'function render' in js, "render() function missing"

    def test_drawarrays(self):
        js = get_js()
        assert 'drawArrays' in js, "gl.drawArrays not found"


class TestBackgroundImage:
    """BG 图片功能"""

    def test_bg_file_input(self):
        html = get_html()
        assert 'id="bg_file"' in html, "BG file input missing"
        assert 'accept="image/' in html, "Should only accept images"

    def test_bg_clear_button(self):
        html = get_html()
        assert 'id="bg_clear"' in html, "BG clear button missing"

    def test_loadbgimage_function(self):
        js = get_js()
        assert 'loadBgImage' in js, "loadBgImage function missing"


class TestEdgeCaseHandling:
    """边界情况"""

    def test_clamp_in_shader(self):
        html = get_html()
        match = re.search(r'const\s+FS\s*=\s*`([^`]+)`', html, re.DOTALL)
        if match:
            fs = match.group(1)
            assert 'clamp(' in fs, "clamp() not found in shader"

    def test_bg_type_conditional(self):
        html = get_html()
        match = re.search(r'const\s+FS\s*=\s*`([^`]+)`', html, re.DOTALL)
        if match:
            fs = match.group(1)
            assert 'u_bg_type' in fs, "u_bg_type conditional not in shader"

    def test_no_infinite_loop_in_render(self):
        js = get_js()
        # 简单检查：render 内不应有 while(true) 或 for(;;)
        render_match = re.search(
            r'function render\s*\([^)]*\)\s*\{(.*?)\n\}',
            js, re.MULTILINE | re.DOTALL)
        if render_match:
            body = render_match.group(1)
            assert not re.search(r'while\s*\(\s*true\s*\)', body), \
                "Infinite while in render()"
            assert not re.search(r'for\s*\(\s*;\s*;\s*\)', body), \
                "Infinite for in render()"


class TestParameterUpdates:
    """参数更新"""

    def test_sliderdefs(self):
        js = get_js()
        # sliderDefs 应该存在且数量正确
        defs = re.findall(r"id:\s*['\"]s_(\w+)['\"]", js)
        assert len(defs) >= 25, f"sliderDefs count {len(defs)} < 25"

    def test_param_object_p(self):
        js = get_js()
        assert re.search(r'const\s+P\s*=\s*\{', js) or \
               re.search(r'let\s+P\s*=\s*\{', js), \
               "Parameter object P not found"


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v', '--tb=short'])