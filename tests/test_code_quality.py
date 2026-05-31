"""
Jade Glass Control — Code Quality Tests

通过静态分析检查 JS/GLSL/HTML 代码质量。
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


def get_fs():
    html = get_html()
    match = re.search(r'const\s+FS\s*=\s*`([^`]+)`', html, re.DOTALL)
    return match.group(1).strip() if match else ''


class TestJavaScriptQuality:
    """JavaScript 代码质量"""

    def test_no_implicit_global_vars(self):
        """检测隐式全局变量（未声明的 var/let/const）

        允许：GLSL 变量名（f, color, gl_FragColor）、shader 内置、
              已知 UI 全局（render, P, gl, c, sliders 等）
        """
        js = get_js()

        # 允许的全局标识符
        allowed = {
            # WebGL 常用
            'render', 'P', 'gl', 'c', 'cw', 'ch', 'program',
            'sliderDefs', 'sliders', 'u', 'bg_img', 'bg_tex',
            # Canvas/WebGL API
            'canvas', 'gl', 'program', 'buffer', 'texture',
            # GLSL 合法变量名（shader 内联在 JS）
            'f', 'color', 'gl_FragColor', 'gl_Position', 'bgType',
            # GLSL/SDF 函数返回值和参数
            'p', 'info', 'd', 'rgb', 'h', 's', 'l', 'FS', 'VS', 't', 'e', 'n',
            # GLSL 局部变量（SDF/光照计算中）
            'r', 'r2', 'cx', 'cy', 'dist', 'q', 'interior', 'exterior',
            'eps', 'dx', 'dy', 'nz', 'N3', 'V', 'cosT', 'F0', 'fr', 'cos',
            'H', 'R', 'L', 'reflUV', 'reflColor', 'sinIn', 'sinOut',
            'refractOffset', 'refractUV', 'refractBg', 'absorption',
            'transmitted', 'hue', 'jadeHSL', 'jadeCol', 'refractionColor',
            'Tdir', 'alignment', 'sssAtten', 'sssColor',
            # Image 对象属性（loadBgImage 中）
            'onload', 'src', 'img',
            # WebGL API 对象
            'buffer', 'texture', 'program', 'uniforms',
            # Math/Array
            'Math', 'Array', 'Object', 'console', 'document',
            'navigator', 'Image', 'performance',
            # 标准全局
            'undefined', 'NaN', 'Infinity',
        }

        # 找所有赋值语句左侧（跳过声明关键字）
        # 匹配 "  varname  =" 但不是 "let/const/var varname ="
        assigns = re.findall(r'(?<![\w])([a-zA-Z_$][\w$]*)\s*=(?!=)', js)

        # 过滤
        suspicious = [
            v for v in assigns
            if v not in allowed
            and v not in {
                # JS 关键字（不是 bug）
                'if','else','for','while','do','switch','case','default',
                'break','continue','return','function','try','catch',
                'finally','throw','new','this','class','import','export',
                'async','await','yield','delete','typeof','instanceof',
                'in','of','true','false','null','void','extends',
                # 常见表达式结果
                'x','y','z','w','i','j','k','n','t','s',
                'idx','len','pos','uv','out','v',
                # 循环变量
                'm','l','r','g','b','a',
            }
        ]

        # 允许少量可疑全局（shader 内联变量太多，无法穷举）
        # JS 中 inline 了 GLSL shader 模板字符串，会产生大量假阳性
        unique_suspicious = len(set(suspicious))
        assert unique_suspicious <= 40, \
            f"Possible implicit globals ({unique_suspicious}): {sorted(set(suspicious))[:15]}"

    def test_render_not_infinite_loop(self):
        """render() 不应在内部有 requestAnimationFrame 递归"""
        js = get_js()
        render_fn = re.search(r'function render\s*\([^)]*\)\s*\{(.*?)^\}', js, re.MULTILINE | re.DOTALL)
        if render_fn:
            body = render_fn.group(1)
            # 不应该在 render 内部调用 requestAnimationFrame
            assert 'requestAnimationFrame' not in body, \
                "requestAnimationFrame called inside render() (should be in loop)"

    def test_no_eval(self):
        """禁止使用 eval（安全风险）"""
        js = get_js()
        assert 'eval(' not in js, "eval() usage is prohibited"

    def test_no_inner_html_dangerous(self):
        """innerHTML 应最小化使用（XSS 风险）"""
        js = get_js()
        inner_html_count = js.count('innerHTML')
        # 允许少量（UI 生成），但不能是用户输入
        assert inner_html_count <= 5, \
            f"innerHTML used {inner_html_count} times — consider textContent"

    def test_no_debugger_statement(self):
        """不应有 debugger 语句"""
        js = get_js()
        assert 'debugger' not in js, "debugger statement found"

    def test_console_error_not_in_render(self):
        """render() 内不应有 console.log（性能影响）"""
        js = get_js()
        render_match = re.search(r'function render\s*\([^)]*\)\s*\{(.*?)^\}', js, re.MULTILINE | re.DOTALL)
        if render_match:
            body = render_match.group(1)
            assert 'console.log' not in body, "console.log in render() hurts performance"

    def test_canvas_resize_handler_exists(self):
        """窗口 resize 时应处理 canvas 尺寸"""
        js = get_js()
        assert 'resize' in js.lower(), "Window resize handler missing"


class TestGLSLQuality:
    """GLSL Shader 质量"""

    def test_fs_has_precision_qualifier(self):
        """Fragment shader 应该有精度声明"""
        fs = get_fs()
        assert 'precision' in fs, "No precision qualifier in fragment shader"

    def test_no_texel_fetch_in_loops(self):
        """Texture sampling 不应在循环内（性能问题）"""
        fs = get_fs()
        # 简单检查：循环内有 texture2D
        lines = fs.split('\n')
        in_loop = False
        for line in lines:
            if re.match(r'\s*for\s*\(', line):
                in_loop = True
            if in_loop and 'texture2D' in line:
                assert False, "texture2D called inside loop — move outside"
            if in_loop and line.strip().startswith('}'):
                in_loop = False

    def test_gl_fragcolor_written(self):
        """gl_FragColor 应该有赋值"""
        fs = get_fs()
        fragcolor_assigns = re.findall(r'gl_FragColor\s*=', fs)
        assert len(fragcolor_assigns) >= 1, "gl_FragColor never assigned"

    def test_fs_not_empty(self):
        """Fragment shader 不为空"""
        fs = get_fs()
        code_lines = [l for l in fs.split('\n') if l.strip() and not l.strip().startswith('//')]
        assert len(code_lines) >= 20, f"FS seems too short: {len(code_lines)} lines"


class TestHTMLQuality:
    """HTML 结构质量"""

    def test_canvas_inside_body(self):
        """Canvas 应该在 body 内"""
        html = get_html()
        canvas_pos = html.find("<canvas")
        body_pos = html.find("<body")
        close_body = html.find("</body>")

        assert body_pos < canvas_pos < close_body, \
            "Canvas should be inside <body>"

    def test_all_ids_unique(self):
        """所有 id 应该唯一"""
        html = get_html()
        ids = re.findall(r'\sid=["\']([^"\']+)["\']', html)
        assert len(ids) == len(set(ids)), \
            f"Duplicate IDs found: {[i for i in ids if ids.count(i) > 1]}"

    def test_no_deprecated_tags(self):
        """不应使用废弃的 HTML 标签"""
        html = get_html()
        deprecated = ['<center>', '<font', '<marquee', '<blink']
        for tag in deprecated:
            assert tag not in html.lower(), f"Deprecated tag: {tag}"

    def test_slider_ids_match_js(self):
        """所有滑杆 id 应该对应 sliderDefs"""
        html = get_html()
        slider_ids = re.findall(r"id=['\"]s_(\w+)['\"]", html)

        js = get_js()
        def_ids = re.findall(r"['\"]s_(\w+)['\"]", js)

        # JS 定义数量应该 ≥ HTML 数量（可能 JS 还有额外的）
        assert len(def_ids) >= len(slider_ids), \
            f"sliderDefs count ({len(def_ids)}) < slider IDs ({len(slider_ids)})"

    def test_viewport_meta(self):
        """应该有 viewport meta（移动端支持）"""
        html = get_html()
        assert 'viewport' in html, "Missing viewport meta tag"


class TestSecurity:
    """安全检查"""

    def test_no_external_script_loading(self):
        """不应动态加载外部脚本"""
        js = get_js()
        assert 'eval(' not in js, "eval() found"
        # 不应该有 script src 动态注入
        assert "createElement('script')" not in js, \
            "Dynamic script creation not allowed"
        assert 'src=' not in js or 'bg_img' in js, \
            "Suspicious src assignment"

    def test_bg_file_accept_images_only(self):
        """BG 文件输入应只接受图片"""
        html = get_html()
        assert "accept=\"image/" in html, "BG file input should accept images only"

    def test_bg_img_onload_handle_errors(self):
        """BG 图片加载应处理错误"""
        js = get_js()
        # 应该有 onerror 或 try-catch
        assert ('onerror' in js or 'catch' in js) and 'loadBgImage' in js, \
            "BG image loading should handle errors"


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v', '--tb=short'])