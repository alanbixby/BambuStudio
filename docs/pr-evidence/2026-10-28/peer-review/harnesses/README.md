# Portable source-level evidence for CF-03

Publish this directory on the personal fork's existing `review/screenshots`
evidence branch, then link the published directory from the draft descriptions.
It contains tooling, small test doubles, source-line evidence and logs. It does
not contain complete application source files, generated translation units or
binaries. There are no repository mutations, ref changes, GUI/printer actions,
network requests, application builds or GitHub writes in these tools.

Requirements: Python 3.9+, Git with the referenced commits already present, a
C++17 GCC-compatible compiler with ASan/UBSan support for the Project test, and
`nlohmann/json.hpp` (normally the supplied checkout's `src` directory). Fresh
runs here used Linux and g++; host-native Windows/macOS execution is untested.
The source is obtained through `git show FULL_SHA:path`; a supplied candidate
tree is an explicit precommit exception and its tested bytes are hashed. No
checkout location is hardcoded. Tools refuse an existing output directory to
avoid overwriting evidence. Only the output directory receives generated code,
binaries, fixture trees and run logs. Each compiler invocation is sequential
within its runner; run the commands below sequentially to use one compiler job.

Set these paths for your machine (commands assume the evidence directory is the
current directory):

```sh
REPO=/path/to/BambuStudio
OUT=/path/to/new-output-parent
```

## Project cleanup, identity and Model lifecycle

The original input is `a667512789236ea21f5530bcd31c496b4db43fab`.
The proposed source was not committed when this payload was prepared. Its four
file hashes are recorded in [project/results.json](evidence/project/results.json).
To test that candidate before committing it:

```sh
CANDIDATE=/path/to/project/candidate
python3 project/check.py --repo "$REPO" \
  --before a667512789236ea21f5530bcd31c496b4db43fab \
  --candidate-tree "$CANDIDATE" --output "$OUT/project-candidate"
```

The candidate tree must contain `src/slic3r/GUI/Project.{cpp,hpp}` and
`src/libslic3r/Model.{cpp,hpp}`. Once integrated, use its final immutable SHA:

```sh
AFTER_PROJECT=0826d59e1e1b36bf80b82904859c64f339749820
python3 project/check.py --repo "$REPO" \
  --before a667512789236ea21f5530bcd31c496b4db43fab \
  --after "$AFTER_PROJECT" --output "$OUT/project-final"
```

`--include /path/to/include` overrides the default `REPO/src` JSON-header path;
the header's hash is recorded. `--cxx clang++` or another GCC-compatible compiler
can override g++. The retained run used the default supplied-checkout header.
The final-SHA run passed at `0826d59e1e1b36bf80b82904859c64f339749820`;
[results](evidence/project-final/results.json) and individual run logs are retained.
The candidate-tree evidence above remains historical and is not relabeled.

The runner compiles extracted actual Project destructor, generation/posting,
identity, local-publication, lookup and file-traversal methods, and actual Model
destructor, setter, ownership-transfer and auxiliary-accessor methods. It makes
the extracted private panel fields public for the test and supplies a minimal
panel declaration. Only `Reload` entry is instrumented with a worker assertion
and scan counter. Full Model/Project files are read in memory and never copied
into the payload or output; generated extracted translation units stay in
`--output`.

Two original-source controls must exit 1 with their **specific** assertion:
Project recursively deletes the old root during UI reload, and a local identity
check recreates the auxiliary directory. Unexpected crashes/sanitizer failures
do not count as a successful control. Identical fixture code requires injecting
the candidate's pure getter body into the original translation unit; the
original guard still executes its actual creating getter. The original control
is already the asynchronous PR3 implementation, not the earlier blocking HTTP
implementation.

The four candidate modes test real disposable attachment files:

- `cleanup`: publication and a scheduled UI heartbeat precede held modeled owner
  cleanup; Project performs no deletion; eventual owner deletion removes the
  retired whole tree and retains the live tree; actual `load_from` transfers it.
- `identity`: local completion, lookup start and lookup completion avoid creating
  getters/recreating removed paths; live Model/design changes reject stale work;
  empty identity and the existing separator spelling are preserved.
- `reuse`: rapid A→B→A panel reload publishes latest A and retains both still-owned
  roots without Project cleanup.
- `lifecycle`: actual Model same-path/detach/clear setter and destructor preserve
  ownership/cleanup behavior through the modeled owner queue.

Before running either binary, the runner asserts that six existing Model method
bodies are byte-identical: both backup-creating overloads, the creating auxiliary
getter, destructor, setter and `load_from`. The backup-creating overloads are
source-checked, **not executed**; filesystem-backed doubles replace them.

Limits: scheduler and `boost::thread` are deterministic single-threaded queues;
UI/worker labels detect selected illegal accesses but do not prove native race
freedom, event-loop behavior, latency or responsiveness. The heartbeat is an
ordering check, not a timing measurement. `Slic3r::remove_backup` is a modeled
whole-tree backup-owner queue, not the native backup manager. Its final deletion
is labeled backup-UI; this test does not claim all recursive deletion moved off
the UI thread. File traversal uses a std::filesystem adapter; wx strings/stat,
metadata, configuration, HTTP, WebView and editor state are doubles. Text files
are exercised; image/base64 paths are unsupported. Windows-style path checking
is only string preservation. ASan/UBSan covers these isolated binaries only.
The actual creating backup-root initialization/fallback/free-space logic, native
backup task cancellation/shutdown/export, network timeouts and OS filesystem
semantics are not executed.

This focused payload does not independently recreate every older claim about
panel destruction during pending HTTP, failed-link/editor behavior, or the
pre-PR blocking HTTP negative control. Those need their own linked evidence or
narrower wording; merely extracting a method is not test coverage of its cases.

## Historical fourteen-site measured-pixel geometry (236 assertions)

This is the historical check for PR5 at exactly:

- before: `79df7ae309be398ed30c9f397c13c9911c2edc57`
- after: `e20789d722ffb71ac410b3fe341c157687d12624`

```sh
python3 historical-dip/check.py --repo "$REPO" \
  --before 79df7ae309be398ed30c9f397c13c9911c2edc57 \
  --after e20789d722ffb71ac410b3fe341c157687d12624 \
  --output "$OUT/historical-green"
python3 historical-dip/check.py --repo "$REPO" \
  --before 79df7ae309be398ed30c9f397c13c9911c2edc57 \
  --after e20789d722ffb71ac410b3fe341c157687d12624 \
  --negative-control --output "$OUT/historical-red"
```

The historical extractor and all original C++ invariants are preserved in
`historical-dip/expressions.py`; only portable source/loading/runner plumbing and
the explicit negative-control mode were added. It extracts 14 expressions across
six files: camera budget (1), calibration label sizes (5), progress sizes (3),
centering (1), mapping-line endpoints (3), and sync-popup offsets (1). The
separate progress-height cap removals are outside this harness. It compiles with
`-Wall -Wextra -Werror`. Five factors (0.75, 1, 1.25, 1.5, 2) exercise 235 geometry
and old-versus-new assertions plus one coverage-count assertion, for 236 total.

The explicit red run substitutes original expressions into the corrected slots
and must fail the camera budget at factor 0.75. Both red-mode runners exit 0 when
their intended rejection occurs; their result JSON records the underlying
failure. The normal run also checks old-expression counterexamples. The fresh
green output is byte-identical to the preserved prior log,
[historical-dip-original.log](evidence/historical-dip-original.log).

This is minimal pixel-geometry arithmetic, not actual wx `FromDIP`, native GTK,
rendering, a full application build or cross-platform testing. It intentionally
requires the historical progress `GetSize().x` expression shape. Later
`ClientToWindowSize` progress code will not match it unchanged. **The 236 figure
does not validate later progress changes or any of the 43 additional caller-unit
corrections below.**

## Separate later caller-unit checks (43 replacements)

The explicit site specification in `caller-units/sites.json` is against
`e20789d722ffb71ac410b3fe341c157687d12624`. It records the later twelve-file
candidate independently of historical PR5. Run before committing:

```sh
CALLER_CANDIDATE=/path/to/dip_callers/tree
python3 caller-units/verify.py --repo "$REPO" \
  --before e20789d722ffb71ac410b3fe341c157687d12624 \
  --candidate-tree "$CALLER_CANDIDATE" --output "$OUT/callers-green"
python3 caller-units/verify.py --repo "$REPO" \
  --before e20789d722ffb71ac410b3fe341c157687d12624 \
  --candidate-tree "$CALLER_CANDIDATE" --negative-control \
  --output "$OUT/callers-red"
python3 caller-units/audit.py --repo "$REPO" \
  --revision e20789d722ffb71ac410b3fe341c157687d12624 \
  --output "$OUT/callers-inventory"
```

After integration, replace `--candidate-tree ...` with `--after FINAL_SHA` in
both verification commands. The verifier intentionally rejects any additional
changes/line shifts in its twelve files, rather than silently attributing them
to the original 43-site result. A combined later commit may therefore require a
new explicitly reviewed site specification and separately labeled evidence.

The check asserts exactly 43 line replacements (31 explicit conversions and 12
macro-derived conversions), verifies the `ICON_SINGLE_SIZE` macro, and compares
lexical nested-call counts. It also records 104 modeled bitmap cases at
96/120/144/192 font DPI and GDK scales 1/2. The scale is recorded independently;
it does not multiply modeled wx coordinates. The one point-font correction is
source-checked separately from that bitmap matrix. No C++ compiler is used here.
The red mode substitutes unchanged source and verifies that it is rejected.

`audit.py` regenerates the original lexical inventory from immutable source
blobs: comments/strings are masked, balanced calls and declared bitmap/font
names produce candidates. It is not an AST or exhaustive unit proof. Disabled
code, name collisions and false positives remain; manual analysis is required.
Original changed-site/validation and wrapper candidate/nonliteral data is
retained under `evidence/caller-units-original-*` for comparison. Fresh inventory
data and caller verification are under `evidence/callers-*`.

Known exclusions from this 43-site patch remain outside its claims: StatusPanel
measured-height/arrow bitmap counts; ObjectDataViewModel's em-based separator
policy; an unestablished Auxiliary rescale entry path; a Windows-only font path;
disabled/commented code; Monitor's converted style argument. Passing these
checks does not establish exhaustive caller safety, native rasterization,
rescale behavior, build success or visual acceptance.

## Retained evidence and description wording

`evidence/project/`, `evidence/historical-{green,red}/`, and
`evidence/callers-{green,red,audit}/` contain fresh logs/results. Input manifests
identify full baseline/history SHAs, candidate byte hashes and toolchains.
`provenance.json` identifies adapted original tooling and the untouched original
historical log. `SHA256SUMS` covers every published file except itself.

Suggested wording, once the published links are added:

> The linked extracted-method Project harness passes cleanup, identity, rapid
> reload and Model lifecycle cases under ASan/UBSan on Linux; both original-source
> cleanup/identity controls fail as expected. GUI, HTTP, scheduler and backup
> queues are doubled. The retained run identifies candidate source hashes; a
> final-commit run is pending.

> At historical head e20789d7, a linked arithmetic harness passes 236 assertions
> for the original fourteen measured-pixel sites at five factors and rejects the
> original expressions. This is historical source-expression evidence, not
> validation of the later progress shape. Separate source/model checks cover the
> 43 additional caller replacements; native rendering and platform builds remain
> outside these checks.

## Final reviewed source runs

The parent reran the Project checks at PR3 head `0826d59e1e1b36bf80b82904859c64f339749820` (two exact baseline failures, four candidate sanitizer cases), and the 43 caller checks at PR5 head `a1b43d73c23d08db6aa19047286c47c51f4cbe38` (104 modeled DPI cases). Logs are under `evidence/project-final` and `evidence/caller-units-final`. The 236-assertion check was rerun against its explicitly historical SHA; those results are under `evidence/historical-final`. The 43-site check is a subset of PR5: eight additional StatusPanel/em-derived call corrections are covered by separate source review, not those 104 cases.

The published reproduction commands use publicly reachable focused PR ancestors. The Project baseline `a6675127` has the same four tested source blobs as the original local combined baseline; the caller baseline `e20789d7` has the same twelve tested blobs. Final retained runs use those focused ancestors, so no private combined branch is required.
