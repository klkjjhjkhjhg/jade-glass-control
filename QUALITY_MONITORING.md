# Jade Glass Control — Quality Monitoring & Evaluation System

## System Overview

```
┌─────────────────────────────────────────────────────────┐
│              Quality Evaluation Pipeline                │
│                                                         │
│  Code Change → Pre-check → Render Test →               │
│  FPS Test → Visual Check → Report → Auto-fix            │
└─────────────────────────────────────────────────────────┘
```

---

## 1. Evaluation Architecture

### 1.1 Quality Dimensions
| Dimension | Weight | Auto-testable |
|-----------|--------|---------------|
| Performance (FPS) | 25% | ✅ Yes |
| Shader correctness | 20% | ✅ Yes |
| Functional completeness | 20% | ✅ Yes |
| Visual quality | 15% | ⚠️ Screenshot diff |
| Code quality | 10% | ✅ Yes |
| Browser compatibility | 10% | ⚠️ Manual |

### 1.2 Scoring Formula
```
Score = Perf_score × 0.25
      + Shader_score × 0.20
      + Func_score × 0.20
      + Visual_score × 0.15
      + Code_score × 0.10
      + Compat_score × 0.10

Grade:
  A: ≥90  → PASS, auto-merge
  B: 75-89 → PASS with warnings
  C: 60-74 → CONDITIONAL, review required
  D: <60  → FAIL, block merge
```

---

## 2. Test Runner

### 2.1 File Location
```
jade_web/
├── test_runner.py     # 主测试脚本
├── tests/
│   ├── __init__.py
│   ├── test_performance.py    # FPS 测试
│   ├── test_shader.py        # Shader 编译测试
│   ├── test_functional.py    # 功能测试
│   ├── test_visual.py        # 视觉回归测试
│   └── test_code_quality.py  # 代码质量
├── test_results/              # 测试输出
└── QUALITY_REPORT.md          # 最新报告
```

### 2.2 Run Commands

```bash
# 完整测试
python test_runner.py --full

# 快速测试（跳过视觉测试）
python test_runner.py --fast

# 单独测试
python test_runner.py --test performance
python test_runner.py --test shader
python test_runner.py --test functional
python test_runner.py --test visual
python test_runner.py --test code

# 指定输出目录
python test_runner.py --full --output ./test_results/20260531
```

---

## 3. Test Modules

### 3.1 Performance Test (`test_performance.py`)

**测试项目：**

1. **Idle FPS**
   - 打开页面，静置 3 秒
   - 测量 60 帧，计算平均帧时间
   - Target: ≥45 fps

2. **Slider Drag FPS**
   - 模拟连续拖动滑杆
   - 测量拖动期间平均 FPS
   - Target: ≥40 fps

3. **Canvas Resize FPS**
   - 从 720×450 切换到 1280×800
   - 测量重绘 FPS
   - Target: ≥30 fps

4. **Memory Usage**
   - 测量 JS heap 增长
   - Target: <80 MB

**实现方式：** 使用 `playwright` 或 `selenium` 自动化浏览器 + `PerformanceObserver`

**输出格式：**
```json
{
  "test": "performance",
  "timestamp": "2026-05-31T12:00:00Z",
  "results": {
    "idle_fps": 60.0,
    "slider_fps": 58.3,
    "resize_fps": 45.2,
    "memory_mb": 42.1
  },
  "pass": true,
  "score": 95
}
```

### 3.2 Shader Test (`test_shader.py`)

**测试项目：**

1. **Compile Success**
   - 加载 index.html
   - 检查 WebGL context 创建成功
   - 检查 shader 编译无错误
   - `gl.getShaderParameter(shader, gl.COMPILE_STATUS)` === true

2. **Uniform Binding**
   - 检查所有 declared uniforms 有 valid location
   - 无 `null` uniform locations

3. **Texture Binding**
   - BG texture 创建成功
   - 纹理参数正确（LINEAR, REPEAT）

4. **Render Success**
   - 调用 `render()` 无异常
   - Canvas 非空白（有像素变化）

**输出格式：**
```json
{
  "test": "shader",
  "timestamp": "2026-05-31T12:00:00Z",
  "results": {
    "compile_success": true,
    "uniforms_bound": true,
    "texture_bound": true,
    "render_success": true,
    "errors": []
  },
  "pass": true,
  "score": 100
}
```

### 3.3 Functional Test (`test_functional.py`)

**测试项目：**

1. **All 30 Sliders Interactive**
   - 逐个获取 slider 元素
   - 模拟 `input` 事件
   - 验证值更新 + 渲染触发

2. **Tab Switching**
   - 测试 4 个 tab 点击
   - 验证对应 panel 显示/隐藏

3. **Canvas Resize**
   - 调整 cw/ch 滑杆
   - 验证 canvas.width/height 更新

4. **BG Image Upload**
   - 上传测试图片
   - 验证 render 使用 texture 而非 procedural

5. **BG Reset**
   - 点击 Reset 按钮
   - 验证回退到 procedural

6. **Edge Cases**
   - cornerRadius = 0 → 不 crash
   - IOR = 1.0 → 渲染稳定
   - SSS = 0 → 正常显示

**输出格式：**
```json
{
  "test": "functional",
  "timestamp": "2026-05-31T12:00:00Z",
  "results": {
    "sliders_count": 30,
    "sliders_working": 30,
    "tabs_working": 4,
    "canvas_resize_working": true,
    "bg_upload_working": true,
    "bg_reset_working": true,
    "edge_cases_passed": true
  },
  "pass": true,
  "score": 100
}
```

### 3.4 Visual Regression Test (`test_visual.py`)

**测试项目：**

1. **Reference Screenshots**
   - 维护一套参考截图（baseline）
   - 路径: `test_results/screenshots/baseline/`

2. **Screenshot Diff**
   - 对比修改后截图与 baseline
   - 使用 `pixelmatch` 计算差异像素比例
   - Threshold: <1% 差异 = PASS

3. **Visual Quality Checks**
   - 无明显锯齿（anti-aliasing 工作正常）
   - SSS 边缘柔和（无硬边界）
   - Fresnel 边缘亮度正确
   - 无色带（banding）检测

**Baseline 参数组合：**
| # | Aspect | IOR | SSS | CornerRadius |
|---|--------|-----|-----|--------------|
| 1 | 1.96 | 1.52 | 0.65 | 0.055 |
| 2 | 1.0 | 1.5 | 0.0 | 0.1 |
| 3 | 3.0 | 2.0 | 1.0 | 0.02 |
| 4 | 0.5 | 1.3 | 0.5 | 0.15 |

**输出格式：**
```json
{
  "test": "visual",
  "timestamp": "2026-05-31T12:00:00Z",
  "results": {
    "baseline_count": 4,
    "diff_count": 4,
    "max_diff_percent": 0.3,
    "all_passed": true
  },
  "pass": true,
  "score": 100
}
```

### 3.5 Code Quality Test (`test_code_quality.py`)

**测试项目：**

1. **JavaScript Syntax**
   - 使用 `esprima` 或 `acorn` 解析 JS
   - 无 SyntaxError

2. **No Implicit Globals**
   - 扫描 `var` 声明（应使用 let/const）
   - 检测隐式全局变量

3. **GLSL Syntax**
   - 提取 FS 中的 GLSL 代码
   - 基本语法检查（括号匹配、分号结尾）

4. **HTML Validity**
   - 无未闭合标签
   - 所有 `id` 引用存在

**输出格式：**
```json
{
  "test": "code_quality",
  "timestamp": "2026-05-31T12:00:00Z",
  "results": {
    "js_syntax_ok": true,
    "no_implicit_globals": true,
    "glsl_syntax_ok": true,
    "html_valid": true
  },
  "pass": true,
  "score": 100
}
```

---

## 4. Main Test Runner

```python
#!/usr/bin/env python3
"""
Jade Glass Control — Quality Evaluation Runner
用法: python test_runner.py [--full|--fast|--test TEST_NAME] [--output DIR]
"""

import argparse
import json
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

# 颜色输出
GREEN = '\033[92m'
RED   = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def log(msg, level='INFO'):
    prefix = {'INFO': '[INFO]', 'PASS': f'{GREEN}[PASS]{RESET}',
              'FAIL': f'{RED}[FAIL]{RESET}', 'WARN': f'{YELLOW}[WARN]{RESET}'}
    print(f"{prefix.get(level, '[INFO]')} {msg}")

def run_pytest(test_file, markers=''):
    """运行 pytest 测试文件"""
    cmd = ['python', '-m', 'pytest', test_file, '-v', '--tb=short']
    if markers:
        cmd.extend(['-m', markers])
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def generate_report(results: dict, output_dir: Path) -> dict:
    """生成质量报告"""
    total_score = 0
    weights = {
        'performance': 0.25,
        'shader': 0.20,
        'functional': 0.20,
        'visual': 0.15,
        'code_quality': 0.10
    }

    for test_name, result in results.items():
        score = result.get('score', 0)
        total_score += score * weights.get(test_name, 0)

    grade = 'A' if total_score >= 90 else 'B' if total_score >= 75 else 'C' if total_score >= 60 else 'D'

    report = {
        'timestamp': datetime.now().isoformat(),
        'overall_score': round(total_score, 1),
        'grade': grade,
        'all_passed': all(r.get('pass', False) for r in results.values()),
        'details': results
    }

    # 写入 JSON 报告
    report_path = output_dir / 'quality_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    # 写入 Markdown 报告
    md_path = output_dir / 'QUALITY_REPORT.md'
    with open(md_path, 'w') as f:
        f.write(f"# Quality Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"## Overall: {grade} ({total_score:.1f}/100)\n\n")
        f.write("## Test Results\n\n")
        for name, res in results.items():
            status = f"{GREEN}PASS{RESET}" if res['pass'] else f"{RED}FAIL{RESET}"
            f.write(f"- **{name}**: {status} — Score: {res.get('score', 0)}\n")
        f.write(f"\n_Report generated at {datetime.now().isoformat()}_\n")

    return report

def auto_fix(results: dict, html_path: Path) -> bool:
    """自动修复检测到的问题"""
    fixed = False

    # 问题 1: uniform location 为 null
    if not results.get('shader', {}).get('pass', False):
        log("Shader binding issues detected — review shader code", 'WARN')

    # 问题 2: FPS 过低
    perf = results.get('performance', {})
    if not perf.get('pass', False):
        fps = perf.get('results', {}).get('idle_fps', 0)
        if fps < 45:
            log(f"Performance issue: FPS={fps} < 45", 'WARN')
            # 优化建议：减少 shader 指令数
            log("Suggestion: Reduce shader instruction count or optimize GLSL", 'WARN')

    return fixed

def main():
    parser = argparse.ArgumentParser(description='Jade Glass Control QA Runner')
    parser.add_argument('--full', action='store_true', help='Run full test suite')
    parser.add_argument('--fast', action='store_true', help='Skip visual tests')
    parser.add_argument('--test', choices=['performance', 'shader', 'functional', 'visual', 'code_quality'])
    parser.add_argument('--output', default='./test_results/latest', help='Output directory')
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {}

    # 确定要运行的测试
    if args.test:
        test_map = {
            'performance': 'tests/test_performance.py',
            'shader': 'tests/test_shader.py',
            'functional': 'tests/test_functional.py',
            'visual': 'tests/test_visual.py',
            'code_quality': 'tests/test_code_quality.py',
        }
        test_file = test_map[args.test]
        passed, stdout, stderr = run_pytest(test_file)
        results[args.test] = {'pass': passed, 'score': 80 if passed else 40}

    elif args.full or args.fast:
        tests = ['shader', 'code_quality', 'functional', 'performance']
        if not args.fast:
            tests.append('visual')

        for test_name in tests:
            test_file = f'tests/test_{test_name}.py'
            log(f"Running {test_name}...")
            passed, stdout, stderr = run_pytest(test_file)

            # 解析 score (pytest 输出格式)
            score = 100 if passed else 0
            if passed and 'score' in stdout.lower():
                # 尝试从输出中提取 score
                import re
                match = re.search(r'score[=:]\s*(\d+)', stdout, re.IGNORECASE)
                if match:
                    score = int(match.group(1))

            results[test_name] = {'pass': passed, 'score': score}
            log(f"{test_name}: {'PASS' if passed else 'FAIL'} (score: {score})",
                'PASS' if passed else 'FAIL')

    else:
        log("No test specified. Use --full, --fast, or --test TEST_NAME")
        sys.exit(1)

    # 生成报告
    report = generate_report(results, output_dir)

    # 打印摘要
    print(f"\n{'='*50}")
    print(f"Overall Score: {report['overall_score']:.1f}/100 — Grade: {report['grade']}")
    print(f"Report: {output_dir / 'quality_report.json'}")
    print(f"Details: {output_dir / 'QUALITY_REPORT.md'}")

    # 自动修复
    if not all(r['pass'] for r in results.values()):
        auto_fix(results, Path('index.html'))

    # 退出码
    sys.exit(0 if report['all_passed'] else 1)

if __name__ == '__main__':
    main()
```

---

## 5. Continuous Quality Monitoring

### 5.1 Pre-commit Hook
在 `jade_web/` 目录添加 `.pre-commit-config.yaml`：
```yaml
repos:
  - repo: local
    hooks:
      - id: quality-check
        name: Quality Check
        entry: python test_runner.py --fast
        language: system
        pass_filenames: false
        files: ^jade_web/
```

### 5.2 Nightly Build
每日凌晨运行完整测试：
```
0 3 * * * cd /Users/klkjjhjkhjhg/.hermes/hermes-agent/jade_web && python test_runner.py --full --output ./test_results/$(date +\%Y\%m\%d)
```

### 5.3 Baseline Update Workflow
当视觉测试发现 `max_diff_percent > 1%`：
1. 检查差异是否为预期改动（功能修改导致）
2. 若是预期：更新 baseline 截图
3. 若不是：视为 regression，回退代码

---

## 6. Test Results Directory Structure

```
jade_web/test_results/
├── 20260531_120000/           # 每次完整测试的输出
│   ├── quality_report.json    # 结构化报告
│   ├── QUALITY_REPORT.md     # Markdown 报告
│   ├── screenshots/
│   │   ├── baseline/          # 参考截图
│   │   └── latest/            # 最新截图
│   └── logs/
│       └── test.log          # 测试日志
├── 20260530_120000/
├── latest -> 20260531_120000  # 软链接指向最新
└── regression_log.txt          # 回归趋势记录
```

---

## 7. Quality Gate Summary

| Check | Pass Criteria | Auto-fixable |
|-------|--------------|-------------|
| Idle FPS | ≥45 | ⚠️ Shader 优化 |
| Slider FPS | ≥40 | ⚠️ Shader 优化 |
| Shader compiles | true | ❌ |
| Uniforms bound | true | ❌ |
| Sliders work | 30/30 | ❌ |
| Tab switching | 4/4 | ❌ |
| Visual diff | <1% | ⚠️ Update baseline |
| JS syntax | valid | ❌ |
| GLSL syntax | valid | ❌ |

---

*Last updated: 2026-05-31*