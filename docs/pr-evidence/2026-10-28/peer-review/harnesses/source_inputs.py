"""Read source without checking out files or changing refs. Standard library only."""
import hashlib
from pathlib import Path
import subprocess


def git(repo, *args):
    return subprocess.check_output(['git', '--no-optional-locks', '-C', str(repo), *args])


def revision(repo, ref):
    return git(repo, 'rev-parse', '--verify', ref + '^{commit}').decode().strip()


def read_revision(repo, ref, paths):
    sha = revision(repo, ref)
    sources = {p: git(repo, 'show', f'{sha}:{p}').decode() for p in paths}
    return sources, {'commit': sha, 'sha256': hashes(sources)}


def read_candidate(tree, paths):
    sources = {p: (Path(tree) / p).read_bytes().decode() for p in paths}
    return sources, {'kind': 'uncommitted candidate tree; hashes identify tested bytes',
                     'sha256': hashes(sources)}


def hashes(sources):
    return {p: hashlib.sha256(s.encode()).hexdigest() for p, s in sources.items()}


def output_directory(value):
    out = Path(value).resolve()
    # Never overwrite prior evidence. All generated code, logs and fixtures stay here.
    out.mkdir(parents=True, exist_ok=False)
    return out
