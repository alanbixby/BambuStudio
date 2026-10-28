#!/usr/bin/env python3
"""Lexical helper/font inventory at one immutable revision, not a C++ AST audit."""
import argparse
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from source_inputs import git, revision, output_directory
from scanner import calls, mask


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True, type=Path)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    out = output_directory(args.output)
    sha = revision(args.repo, args.revision)
    paths = git(args.repo, 'ls-tree', '-r', '--name-only', sha, '--', 'src').decode().splitlines()
    sources = {p: git(args.repo, 'show', f'{sha}:{p}').decode(errors='replace')
               for p in paths if Path(p).suffix in ('.cpp', '.hpp', '.h', '.cc', '.cxx')}
    declarations = {}
    for source in sources.values():
        for m in re.finditer(r'\b(ScalableBitmap|ScalableButton|wxFont|wxFontInfo)\s+(?:const\s*)?[*&]?\s*(\w+)', mask(source)):
            if m[2] not in {'const', 'operator', 'return'}:
                declarations.setdefault(m[2], set()).add(m[1])
    inventory = [dict(path=p, **call) for p, source in sources.items()
                 for call in calls(source, declarations)]
    nested = [c for c in inventory if 'FromDIP' in c['code']]
    for name, data in [('typed-names.json', {k: sorted(v) for k, v in declarations.items()}),
                       ('call-inventory.json', inventory), ('nested-calls.json', nested)]:
        (out / name).write_text(json.dumps(data, indent=2) + '\n')
    summary = {'commit': sha, 'source_files': len(sources), 'lexical_candidates': len(inventory),
               'containing_FromDIP': len(nested),
               'limits': 'Lexical candidate discovery only; includes disabled code, name collisions and false positives; manual unit analysis required.'}
    (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
