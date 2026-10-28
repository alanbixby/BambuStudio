#!/usr/bin/env python3
"""Separate exact 43-caller source checks and modeled arithmetic; no compilation."""
import argparse
import json
import math
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from source_inputs import read_candidate, read_revision, output_directory
from scanner import calls

ROOT = Path(__file__).resolve().parent
PREFIX = 'src/slic3r/GUI/'


def expression_and_size(value):
    return value if isinstance(value, list) else (f'FromDIP({value})', value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True, type=Path)
    parser.add_argument('--before', required=True)
    after = parser.add_mutually_exclusive_group(required=True)
    after.add_argument('--after')
    after.add_argument('--candidate-tree', type=Path)
    parser.add_argument('--output', required=True)
    parser.add_argument('--negative-control', action='store_true', help='verify unchanged baseline is rejected')
    args = parser.parse_args()
    out = output_directory(args.output)
    sites = json.loads((ROOT / 'sites.json').read_text())
    paths = [PREFIX + name for name in sites]
    before, before_meta = read_revision(args.repo, args.before, paths)
    after, after_meta = (read_revision(args.repo, args.after, paths) if args.after else
                         read_candidate(args.candidate_tree, paths))
    macro, macro_meta = read_revision(args.repo, args.before, [PREFIX + 'GUI_Utils.hpp'])
    assert '#define ICON_SINGLE_SIZE FromDIP(16)' in macro[PREFIX + 'GUI_Utils.hpp']
    checks = []

    def verify(sources):
        for path in paths:
            expected = {int(n): v for n, v in sites[path.removeprefix(PREFIX)].items()}
            a_lines = before[path].splitlines(keepends=True)
            b_lines = sources[path].splitlines(keepends=True)
            assert len(a_lines) == len(b_lines), 'line count changed: ' + path
            differing = [(i + 1, a, b) for i, (a, b) in enumerate(zip(a_lines, b_lines)) if a != b]
            assert {n for n, _, _ in differing} == set(expected), 'expected exact changed lines: ' + path
            changes = []
            for n, a, b in differing:
                expression, size = expression_and_size(expected[n])
                assert a.count(expression) == 1, (path, n, expression)
                assert b == a.replace(expression, str(size), 1), (path, n)
                changes.append({'line': n, 'nominal_size': size, 'before': a.rstrip(), 'after': b.rstrip()})
            before_calls = [c for c in calls(before[path]) if 'FromDIP' in c['code']]
            after_calls = [c for c in calls(sources[path]) if 'FromDIP' in c['code']]
            macro_count = sum(isinstance(v, list) for v in expected.values())
            removed = len(before_calls) - len(after_calls)
            assert removed == len(expected) - macro_count, path
            checks.append({'path': path, 'changed_lines': len(differing),
                           'removed_direct_nested_conversions': removed,
                           'removed_macro_conversions': macro_count, 'changes': changes})

    if args.negative_control:
        try:
            verify(before)
        except AssertionError as error:
            assert str(error).startswith('expected exact changed lines: ')
            result = {'before': before_meta, 'after': after_meta, 'result': 'PASS (expected failure)',
                      'expected_rejection': str(error)}
            (out / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
            print('PASS negative control: unchanged source rejected:', error)
            return
        raise AssertionError('unchanged baseline incorrectly accepted')
    verify(after)
    sizes = sorted({expression_and_size(v)[1] for name, rows in sites.items()
                    if name != 'AboutDialog.cpp' for v in rows.values()})
    matrix = []
    for dpi in (96, 120, 144, 192):
        for gdk_scale in (1, 2):
            for size in sizes:
                corrected = math.floor(size * dpi / 96 + 0.5)
                prior = math.floor(corrected * dpi / 96 + 0.5)
                matrix.append(dict(dpi=dpi, gdk_scale=gdk_scale, nominal=size,
                                   prior_wx_height=prior, corrected_wx_height=corrected))
    total = sum(c['changed_lines'] for c in checks)
    assert total == 43 and sum(c['removed_macro_conversions'] for c in checks) == 12
    assert len(matrix) == 104
    result = {'before': before_meta, 'after': after_meta, 'macro_source': macro_meta,
              'checks': checks, 'total_changed_lines': total, 'arithmetic_matrix': matrix,
              'result': 'PASS',
              'limits': 'Exact source replacements and lexical nested-call counts plus modeled arithmetic only. No AST, compiler, native wx, GUI, full build or exhaustive caller-safety proof. Excluded StatusPanel/em-size/rescale candidates remain outside these 43 sites.'}
    (out / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
    print(f'PASS: {total} exact replacements in {len(checks)} files; 31 direct and 12 macro conversions; {len(matrix)} modeled DPI cases')


if __name__ == '__main__':
    main()
