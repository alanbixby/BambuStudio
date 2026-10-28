#!/usr/bin/env python3
"""Compile actual extracted methods with explicit GUI/HTTP/backup-queue doubles."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from source_inputs import read_candidate, read_revision, output_directory
from extract import method

ROOT = Path(__file__).resolve().parent
PROJECT = 'src/slic3r/GUI/Project.cpp'
HEADER = 'src/slic3r/GUI/Project.hpp'
MODEL = 'src/libslic3r/Model.cpp'
MODEL_HEADER = 'src/libslic3r/Model.hpp'
PATHS = (PROJECT, HEADER, MODEL, MODEL_HEADER)
PURE = 'std::string Model::get_auxiliary_file_temp_path_if_initialized() const'
UNCHANGED = [
    'std::string Model::get_auxiliary_file_temp_path()',
    'std::string Model::get_backup_path()',
    'std::string Model::get_backup_path(const std::string &sub_path)',
    'Model::~Model()', 'void Model::set_backup_path(', 'void Model::load_from(',
]
MODEL_SIGS = ['Model::~Model()', 'void Model::set_backup_path(',
              'void Model::load_from(', 'std::string Model::get_auxiliary_file_temp_path()']
PROJECT_SIGS = [
    'ProjectPanel::~ProjectPanel()', 'void ProjectPanel::on_reload(',
    'void ProjectPanel::clear_model_info()', 'std::uint64_t ProjectPanel::next_reload_generation()',
    'bool ProjectPanel::reload_is_current(', 'void ProjectPanel::post_reload_result(',
    'bool ProjectPanel::matches_project(', 'void ProjectPanel::dispatch_project_payload()',
    'void ProjectPanel::start_model_id_lookup(', 'std::string ProjectPanel::fetch_model_id(',
    'std::map<std::string, std::vector<json>> ProjectPanel::Reload(',
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True, type=Path)
    parser.add_argument('--before', required=True, help='baseline commit, resolved to full SHA')
    after = parser.add_mutually_exclusive_group(required=True)
    after.add_argument('--after', help='final commit, read with git show')
    after.add_argument('--candidate-tree', type=Path, help='precommit tree with four source files')
    parser.add_argument('--output', required=True)
    parser.add_argument('--include', type=Path, help='directory containing nlohmann/json.hpp; default REPO/src')
    parser.add_argument('--cxx', default='g++')
    args = parser.parse_args()
    out = output_directory(args.output)
    include = (args.include or args.repo / 'src').resolve()
    before, before_meta = read_revision(args.repo, args.before, PATHS)
    after, after_meta = (read_revision(args.repo, args.after, PATHS) if args.after else
                         read_candidate(args.candidate_tree, PATHS))
    for sig in UNCHANGED:
        assert method(before[MODEL], sig) == method(after[MODEL], sig), 'changed protected Model body: ' + sig
    assert 'get_auxiliary_file_temp_path_if_initialized() const;' in after[MODEL_HEADER]
    manifest = {'before': before_meta, 'after': after_meta,
                'unchanged_model_bodies': UNCHANGED, 'compiler_jobs': 1,
                'json_header_sha256': hashlib.sha256((include / 'nlohmann/json.hpp').read_bytes()).hexdigest(),
                'toolchain': subprocess.check_output([args.cxx, '--version'], text=True).splitlines()[0],
                'runs': []}
    (out / 'inputs.json').write_text(json.dumps(manifest, indent=2) + '\n')
    for label, sources in [('before', before), ('after', after)]:
        header = sources[HEADER]
        start = header.index('class ProjectPanel : public wxPanel')
        fields = header[start:header.index('\npublic:\n', start)].replace('private:', 'public:')
        model_methods = '\n\n'.join(method(sources[MODEL], s) for s in MODEL_SIGS)
        # The before source lacks this helper. Inject ONLY the after pure helper so
        # identical fixture code compiles; before matches_project still uses its
        # actual creating getter. Its two expected failures are the controls.
        model_methods += '\n' + method(after[MODEL], PURE)
        methods = '\n\n'.join(method(sources[PROJECT], s) for s in PROJECT_SIGS)
        anchor = 'ProjectPanel::Reload(wxString aux_path)\n{'
        assert methods.count(anchor) == 1
        methods = methods.replace(anchor, anchor + '\n    require(!on_ui,"Reload ran on UI");++scan_calls;', 1)
        unit = out / (label + '-test.cpp')
        unit.write_text((ROOT / 'doubles.hpp').read_text() + fields +
                        (ROOT / 'panel-declarations.hpp').read_text() + model_methods +
                        methods + (ROOT / 'tests.cpp').read_text())
        binary = out / (label + '-test')
        command = [args.cxx, '-std=c++17', '-pthread', '-Wall', '-Wextra', '-Wno-unused-parameter',
                   '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-g',
                   '-I', str(include), str(unit), '-o', str(binary)]
        compiled = subprocess.run(command, capture_output=True, text=True)
        (out / (label + '-compile.log')).write_text(compiled.stdout + compiled.stderr)
        compiled.check_returncode()
        modes = ['cleanup', 'identity'] if label == 'before' else ['cleanup', 'identity', 'reuse', 'lifecycle']
        for mode in modes:
            result = subprocess.run([str(binary), str(out / 'fixtures' / (label + '-' + mode)), mode],
                                    capture_output=True, text=True)
            (out / (label + '-' + mode + '.log')).write_text(result.stdout + result.stderr)
            print(label, mode, 'exit=' + str(result.returncode), result.stdout + result.stderr, flush=True)
            if label == 'before':
                expected = {'cleanup': 'Project performed recursive cleanup on the reload UI path',
                            'identity': 'local identity check recreated auxiliary directory'}[mode]
                assert result.returncode == 1 and expected in result.stderr, 'wrong negative control failure'
                assert 'AddressSanitizer' not in result.stderr and 'runtime error:' not in result.stderr
            else:
                assert result.returncode == 0, 'candidate failed ' + mode
                assert 'AddressSanitizer' not in result.stderr and 'runtime error:' not in result.stderr
            manifest['runs'].append({'source': label, 'case': mode, 'exit': result.returncode,
                                     'expected_failure': label == 'before'})
    manifest['result'] = 'PASS'
    (out / 'results.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('PASS: two specific baseline failures; four candidate cases pass ASan/UBSan; six existing Model bodies unchanged.')


if __name__ == '__main__':
    main()
