#!/usr/bin/env python3
"""
Jade Glass Control — Quality Evaluation Runner

Usage:
    python test_runner.py              # 运行所有静态测试（shader + functional + code）
    python test_runner.py --full        # 完整测试（需浏览器环境）
    python test_runner.py --test shader
    python test_runner.py --test functional
    python test_runner.py --test code_quality
    python test_runner.py --output ./test_results/20260531
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# 颜色
GREEN = '\033[92m'
RED   = '\033[91m'
YELLOW = '\033[93m'
CYAN  = '\033[96m'
RESET = '\033[0m'


def log(msg, level='INFO'):
    prefix = {
        'INFO': f'{CYAN}[INFO]{RESET}',
        'PASS': f'{GREEN}[PASS]{RESET}',
        'FAIL': f'{RED}[FAIL]{RESET}',
        'WARN': f'{YELLOW}[WARN]{RESET}',
        'SKIP': f'{YELLOW}[SKIP]{RESET}',
    }
    print(f"{prefix.get(level, '[INFO]')} {msg}")


def run_pytest(module_path: str, desc: str) -> dict:
    """运行单个 pytest 模块，返回结果"""
    import subprocess
    cmd = [sys.executable, '-m', 'pytest', module_path,
           '-v', '--tb=line', '-c', '/dev/null']
    result = subprocess.run(cmd, capture_output=True, text=True)

    # 解析输出统计
    output = result.stdout + result.stderr
    passed = output.count(' PASSED')
    failed = output.count(' FAILED')
    total = passed + failed

    return {
        'desc': desc,
        'passed': passed,
        'failed': failed,
        'total': total,
        'exit_code': result.returncode,
        'pass': result.returncode == 0,
        'output_snippet': output[-500:] if len(output) > 500 else output,
    }


def calc_score(results: list[dict]) -> tuple[float, str]:
    """根据测试结果计算质量分和等级"""
    total_passed = sum(r['passed'] for r in results)
    total = sum(r['total'] for r in results)
    if total == 0:
        return 0.0, 'D'

    pct = total_passed / total * 100
    if pct >= 90:
        grade = 'A'
    elif pct >= 75:
        grade = 'B'
    elif pct >= 60:
        grade = 'C'
    else:
        grade = 'D'

    return pct, grade


def generate_report(results: list[dict], output_dir: Path):
    """生成质量报告"""
    score, grade = calc_score(results)

    report = {
        'timestamp': datetime.now().isoformat(),
        'overall_score': round(score, 1),
        'grade': grade,
        'all_passed': all(r['pass'] for r in results),
        'modules': [
            {'name': r['desc'], 'passed': r['passed'],
             'failed': r['failed'], 'total': r['total'], 'pass': r['pass']}
            for r in results
        ],
    }

    output_dir.mkdir(parents=True, exist_ok=True)

    # JSON 报告
    json_path = output_dir / 'quality_report.json'
    with open(json_path, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    log(f"Report JSON: {json_path}", 'INFO')

    # Markdown 报告
    md_path = output_dir / 'QUALITY_REPORT.md'
    lines = [
        f"# Quality Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"## Overall: **{grade}** ({score:.1f}/100)",
        "",
        "| Module | Passed | Failed | Total | Status |",
        "|--------|-------|--------|-------|--------|",
    ]
    for r in results:
        status = f"{GREEN}PASS{RESET}" if r['pass'] else f"{RED}FAIL{RESET}"
        lines.append(
            f"| {r['desc']} | {r['passed']} | {r['failed']} | "
            f"{r['total']} | {status} |"
        )
    lines.append("")
    lines.append(f"_Generated at {datetime.now().isoformat()}_")

    with open(md_path, 'w') as f:
        f.write('\n'.join(lines))
    log(f"Report MD: {md_path}", 'INFO')

    return report


def main():
    parser = argparse.ArgumentParser(description='Jade Glass Control QA Runner')
    parser.add_argument('--full', action='store_true',
                        help='Full suite (requires browser, not implemented)')
    parser.add_argument('--test', choices=['shader', 'functional', 'code_quality'])
    parser.add_argument('--output', default='./test_results/latest')
    args = parser.parse_args()

    output_dir = Path(args.output)

    print(f"\n{'='*55}")
    print(f"  Jade Glass Control — Quality Evaluation")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*55}\n")

    modules = {
        'shader':        ('tests/test_shader.py',       'Shader & WebGL'),
        'functional':    ('tests/test_functional.py',   'Functional'),
        'code_quality':  ('tests/test_code_quality.py', 'Code Quality'),
    }

    results = []

    if args.test:
        m = modules[args.test]
        log(f"Running {m[1]} tests...")
        r = run_pytest(m[0], m[1])
        results.append(r)
    else:
        for name, (path, desc) in modules.items():
            log(f"Running {desc} tests...")
            r = run_pytest(path, desc)
            results.append(r)

    # 打印摘要
    print(f"\n{'─'*55}")
    for r in results:
        status = f"{GREEN}PASS{RESET}" if r['pass'] else f"{RED}FAIL{RESET}"
        print(f"  {r['desc']:<20} {status}  {r['passed']}/{r['total']} passed")

    score, grade = calc_score(results)
    overall = f"{GREEN}PASS{RESET}" if all(r['pass'] for r in results) else f"{RED}FAIL{RESET}"
    print(f"{'─'*55}")
    print(f"  {'Overall':<20} {overall}  Score: {score:.1f}%  Grade: {grade}")
    print(f"{'='*55}\n")

    # 生成报告
    report = generate_report(results, output_dir)
    print(f"Reports saved to: {output_dir}/")

    # 退出码：全部通过 = 0，否则 1
    sys.exit(0 if report['all_passed'] else 1)


if __name__ == '__main__':
    main()