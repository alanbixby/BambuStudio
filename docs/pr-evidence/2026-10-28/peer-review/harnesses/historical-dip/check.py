#!/usr/bin/env python3
"""Historical fourteen-site geometry only; not the later caller-unit/progress patches."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from source_inputs import read_revision, output_directory
from expressions import FILES, build


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True, type=Path)
    parser.add_argument('--before', required=True)
    parser.add_argument('--after', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--cxx', default='g++')
    parser.add_argument('--negative-control', action='store_true',
                        help='substitute original expressions for corrected ones; expect specific failure')
    args = parser.parse_args()
    out = output_directory(args.output)
    # The original expression extractor and all 236 assertions are preserved.
    before, before_meta = read_revision(args.repo, args.before, FILES.values())
    after, after_meta = read_revision(args.repo, args.after, FILES.values())
    cpp = out / 'dip-callers-arithmetic.cpp'
    binary = out / 'dip-callers-arithmetic'
    cpp.write_text(build({'before': before, 'after': after}, args.negative_control))
    command = [args.cxx, '-std=c++17', '-Wall', '-Wextra', '-Werror', str(cpp), '-o', str(binary)]
    compiled = subprocess.run(command, capture_output=True, text=True)
    (out / 'compile.log').write_text(compiled.stdout + compiled.stderr)
    compiled.check_returncode()
    result = subprocess.run([str(binary)], capture_output=True, text=True)
    (out / 'arithmetic-expanded-results.txt').write_text(result.stdout + result.stderr)
    print(result.stdout + result.stderr, end='')
    if args.negative_control:
        assert result.returncode == 1 and 'FAIL factor=0.75: camera fits remaining pixel budget' in result.stderr
    else:
        result.check_returncode()
        assert '236 assertions passed' in result.stdout
    metadata = {'scope': 'historical fourteen-site geometry', 'before': before_meta, 'after': after_meta,
                'negative_control': args.negative_control, 'binary_exit': result.returncode,
                'compiler_jobs': 1, 'compiler_flags': command[1:5],
                'toolchain': subprocess.check_output([args.cxx, '--version'], text=True).splitlines()[0],
                'result': 'PASS (expected failure)' if args.negative_control else 'PASS: 236 assertions'}
    (out / 'results.json').write_text(json.dumps(metadata, indent=2) + '\n')


if __name__ == '__main__':
    main()
