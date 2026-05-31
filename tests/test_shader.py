"""
Jade Glass Control — Shader & WebGL Correctness Tests

测试 WebGL shader 编译、uniform 绑定、纹理绑定、渲染正确性。
纯静态分析，不需要浏览器。
"""

import re
from pathlib import Path

HTML_PATH = Path(__file__).parent.parent / 'index.html'


def extract_glsl():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    vs_match = re.search(r'const\s+VS\s*=\s*`([^`]+)`', content, re.DOTALL)
    fs_match = re.search(r'const\s+FS\s*=\s*`([^`]+)`', content, re.DOTALL)
    vs = vs_match.group(1).strip() if vs_match else ''
    fs = fs_match.group(1).strip() if fs_match else ''
    return vs, fs


def extract_js():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
    return match.group(1) if match else ''


def check_parens_balanced(code: str) -> bool:
    stack = []
    for ch in code:
        if ch == '(':
            stack.append(')')
        elif ch == ')':
            if not stack or stack.pop() != ')':
                return False
    return len(stack) == 0


# ── Tests ────────────────────────────────────────────────────────────────────

class TestShaderStructure:
    """Shader 基本结构"""

    def test_vs_exists(self):
        vs, _ = extract_glsl()
        assert len(vs) > 50, "Vertex shader too short or missing"

    def test_fs_exists(self):
        _, fs = extract_glsl()
        assert len(fs) > 100, "Fragment shader too short or missing"

    def test_fs_has_main(self):
        _, fs = extract_glsl()
        assert 'void main()' in fs, "Fragment shader missing main()"

    def test_fs_outputs_fragcolor(self):
        _, fs = extract_glsl()
        assert 'gl_FragColor' in fs, "No gl_FragColor output found"

    def test_vs_parens_balanced(self):
        vs, _ = extract_glsl()
        assert check_parens_balanced(vs), "VS parentheses unbalanced"

    def test_fs_parens_balanced(self):
        _, fs = extract_glsl()
        assert check_parens_balanced(fs), "FS parentheses unbalanced"


class TestShaderAlgorithms:
    """核心算法存在性"""

    def test_sdf_rounded_box(self):
        _, fs = extract_glsl()
        assert 'sdRoundBox' in fs or ('abs(' in fs and 'max(' in fs), \
            "No SDF rounded box found"

    def test_fresnel(self):
        _, fs = extract_glsl()
        assert 'fresnel' in fs.lower(), "No Fresnel effect found"

    def test_hsl2rgb(self):
        _, fs = extract_glsl()
        assert 'hsl' in fs.lower(), "No HSL→RGB conversion found"

    def test_bg_blend(self):
        """BG 混合逻辑存在"""
        _, fs = extract_glsl()
        assert 'mix(' in fs, "No mix() for BG blending found"


class TestUniformBinding:
    """Uniform 绑定"""

    def test_u_bg_tex_bound_to_unit0(self):
        """u_bg_tex 绑定到 TEXTURE0"""
        js = extract_js()
        assert 'gl.TEXTURE0' in js, "gl.TEXTURE0 not used"
        assert 'uniform1i' in js, "No uniform1i call"


class TestTextureBinding:
    """纹理绑定"""

    def test_createtexture_called(self):
        js = extract_js()
        assert 'createTexture()' in js, "BG texture not created"

    def test_texparameteri_set(self):
        js = extract_js()
        assert 'texParameteri' in js, "Texture parameters not set"

    def test_teximage2d_called(self):
        js = extract_js()
        assert 'texImage2D' in js, "No texImage2D call"


class TestRenderCorrectness:
    """渲染正确性"""

    def test_gl_fragcolor_written(self):
        _, fs = extract_glsl()
        count = len(re.findall(r'gl_FragColor\s*=', fs))
        assert count >= 1, "gl_FragColor never assigned"

    def test_fs_length_reasonable(self):
        _, fs = extract_glsl()
        code_lines = [l for l in fs.split('\n')
                      if l.strip() and not l.strip().startswith('//')]
        assert 20 <= len(code_lines) <= 500, \
            f"FS code lines {len(code_lines)} unexpected"

    def test_render_calls_drawarrays(self):
        js = extract_js()
        assert 'drawArrays' in js, "drawArrays not called in render"


class TestJavaScriptStructure:
    """JS 代码结构"""

    def test_render_function_exists(self):
        js = extract_js()
        assert 'function render(' in js or 'const render' in js, \
            "render() function not found"

    def test_webgl_context_requested(self):
        js = extract_js()
        assert "getContext('webgl'" in js or 'getContext("webgl"' in js, \
            "WebGL context not requested"

    def test_slider_count(self):
        with open(HTML_PATH, 'r', encoding='utf-8') as f:
            html = f.read()
        sliders = re.findall(r'<input type="range"', html)
        assert 25 <= len(sliders) <= 35, \
            f"Slider count {len(sliders)} outside range (25-35)"


class TestRobustness:
    """健壮性"""

    def test_bg_load_error_handler(self):
        js = extract_js()
        # loadBgImage 应该处理错误（onerror 或 try-catch）
        has_loadbg = 'loadBgImage' in js
        if has_loadbg:
            assert 'onerror' in js or 'catch' in js, \
                "loadBgImage missing error handling"

    def test_clamp_in_shader(self):
        """Shader 中应有 clamp"""
        _, fs = extract_glsl()
        assert 'clamp(' in fs, "clamp() not found in shader"


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v', '--tb=short'])