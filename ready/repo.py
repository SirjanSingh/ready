"""Answer from the live checkout what nobody should have to ask a human.

This is the part Alan's PM Agent cannot do (it "cannot edit files or run commands"): read
the working tree, find where the issue's words live, find the tests next to them, and read
how this repo runs its tests.
"""

from __future__ import annotations

import json
import re
import subprocess
import tomllib
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

CODE_EXT = {".py", ".pyi", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".rb"}
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__", ".tox", "site-packages", "docs", "docs_src", "examples"}
STOP = set("""a an the and or not but if then else for to of in on at by with from as is are was were be been it this that
these those there here what which who when where why how can could should would will do does did done has have had i we you
they he she my our your their me us them get set use used using new add make need want like just also only very more most
some any all none no yes true false none null self cls def class return import python version error issue bug fix work works
working expected actual instead problem example code file line call calls called value values type types default""".split())


@dataclass
class Candidate:
    path: str
    score: float
    hits: list[str] = field(default_factory=list)


def _tracked_files(repo: Path) -> list[str]:
    try:
        out = subprocess.run(["git", "-C", str(repo), "ls-files"], capture_output=True, text=True, check=True).stdout
        files = out.splitlines()
    except (subprocess.CalledProcessError, FileNotFoundError):
        files = [str(p.relative_to(repo)).replace("\\", "/") for p in repo.rglob("*") if p.is_file()]
    return [f for f in files if Path(f).suffix in CODE_EXT and not (set(Path(f).parts) & SKIP_DIRS)]


def is_test_path(p: str) -> bool:
    name = Path(p).name
    return "/tests/" in f"/{p}" or "/test/" in f"/{p}" or name.startswith("test_") or name.endswith(("_test.py", ".test.ts", ".spec.ts", ".test.js"))


def extract_terms(text: str) -> dict[str, float]:
    """Identifiers and paths from the issue, weighted by how specific they look."""
    terms: dict[str, float] = {}
    for m in re.finditer(r"File \"([^\"]+)\", line \d+", text):  # traceback frames are gold
        terms[m.group(1).replace("\\", "/")] = 6.0
    for m in re.finditer(r"[\w/.-]+\.(?:py|ts|tsx|js|go|rs)\b", text):
        terms.setdefault(m.group(0), 4.0)
    for m in re.finditer(r"`([^`\n]{2,60})`", text):  # backticked spans
        for tok in re.findall(r"[A-Za-z_][\w.]*", m.group(1)):
            if tok.lower() not in STOP and len(tok) > 2:
                terms[tok] = max(terms.get(tok, 0), 3.0)
    for tok in re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+\b", text):  # dotted names
        if not re.match(r"^\d", tok):
            terms[tok] = max(terms.get(tok, 0), 3.0)
    for tok in re.findall(r"\b[A-Za-z_][A-Za-z0-9_]{2,}\b", text):
        low = tok.lower()
        if low in STOP:
            continue
        # A capitalised word is a class name only if it has inner capitals (CamelCase) or is
        # used like code (followed by "(" or "."); "Calling" at a sentence start is not.
        camel = bool(re.search(r"[a-z][A-Z]", tok)) or (tok[0].isupper() and bool(re.search(rf"\b{re.escape(tok)}[(.]", text)))
        snake = "_" in tok
        w = 2.0 if (camel or snake) else 0.5
        terms[tok] = max(terms.get(tok, 0), w)
    return terms


def candidate_files(issue_text: str, repo: Path, limit: int = 25) -> list[Candidate]:
    """Rank tracked source files by weighted term hits in their path and contents."""
    repo = Path(repo)
    terms = extract_terms(issue_text)
    title = issue_text.partition("\n")[0]
    # The title is where people name the thing that is wrong; the body names everything nearby.
    terms = {t: w * (2.0 if re.search(rf"\b{re.escape(t)}\b", title) else 1.0) for t, w in terms.items()}
    # `Cart.total`, `c.total` and `total` are one symbol: count it once, at its best weight.
    by_leaf: dict[str, tuple[str, float]] = {}
    for t, w in terms.items():
        leaf = t if ("/" in t or "." in t and t.rsplit(".", 1)[-1] in {"py", "ts", "tsx", "js", "go", "rs"}) else t.split(".")[-1]
        if leaf not in by_leaf or w > by_leaf[leaf][1]:
            by_leaf[leaf] = (t, w)
    terms = dict(by_leaf.values())
    if not terms:
        return []
    files = _tracked_files(repo)
    scores: Counter[str] = Counter()
    hits: dict[str, list[str]] = {}
    for f in files:
        low_path = f.lower()
        try:
            content = (repo / f).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        s = 0.0
        for term, w in terms.items():
            leaf = term.split(".")[-1] if "/" not in term else Path(term).name
            if "/" in term or term.endswith((".py", ".ts", ".js", ".go", ".rs", ".tsx")):
                if low_path.endswith(term.lower().lstrip("./")) or Path(f).name == Path(term).name:
                    s += w * 3
                    hits.setdefault(f, []).append(term)
                continue
            if leaf.lower() in low_path:
                s += w * 1.5
            n = len(re.findall(rf"\b(def|class|function|const|let|var|fn|func)\s+{re.escape(leaf)}\b", content))
            if n:
                s += w * 4  # the definition site outranks mentions
                hits.setdefault(f, []).append(f"def {leaf}")
            elif re.search(rf"\b{re.escape(leaf)}\b", content):
                s += w * 0.6
        if s:
            # Tests mention everything; they are where to verify, not where to fix.
            scores[f] = s * (0.35 if is_test_path(f) else 1.0)
    return [Candidate(p, sc, hits.get(p, [])) for p, sc in scores.most_common(limit)]


# Some fixes live in config, not code: dependency pins, CI, docs builds. Code search never
# ranks these, so name them when the issue talks about what they control.
CONFIG_HINTS = [
    (re.compile(r"\b(install|dependenc|requires?|pin(ned)?|version (bump|constraint)|wheels?|sdist|packag|>=|<=|upper bound|support \w+ ?[<>=]+)", re.I),
     ("pyproject.toml", "setup.cfg", "setup.py", "requirements.txt", "package.json")),
    (re.compile(r"\b(ci|workflow|github actions?|nightly|pipeline|pre-commit)\b", re.I),
     (".github/workflows/", ".pre-commit-config.yaml")),
    (re.compile(r"\b(docs?|documentation|mkdocs|readthedocs|sphinx)\b.*\b(build|broken|link|page|render)", re.I | re.S),
     ("mkdocs.yml", "docs/conf.py")),
]


def config_candidates(issue_text: str, repo: Path, limit: int = 2) -> list[str]:
    try:
        tracked = subprocess.run(["git", "-C", str(repo), "ls-files"], capture_output=True, text=True, check=True).stdout.splitlines()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    out: list[str] = []
    for pattern, targets in CONFIG_HINTS:
        if not pattern.search(issue_text):
            continue
        for t in targets:
            for f in tracked:
                if (f == t or (t.endswith("/") and f.startswith(t))) and f not in out:
                    out.append(f)
                    break
    return out[:limit]


def related_tests(paths: list[str], repo: Path, limit: int = 3) -> list[str]:
    """Test files that import or are named after the given source files."""
    files = [f for f in _tracked_files(Path(repo)) if is_test_path(f)]
    out: list[str] = []
    for src in paths:
        stem = Path(src).stem
        if stem in {"__init__", "index"}:
            stem = Path(src).parent.name
        for t in files:
            if stem and stem in Path(t).stem and t not in out:
                out.append(t)
        if len(out) >= limit:
            break
    if len(out) < limit:
        mod_names = {Path(s).with_suffix("").as_posix().replace("/", ".") for s in paths}
        for t in files:
            if t in out:
                continue
            try:
                body = (Path(repo) / t).read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if any(m.split(".")[-1] in body and m in body.replace("/", ".") for m in mod_names):
                out.append(t)
            if len(out) >= limit:
                break
    return out[:limit]


def detect_test_command(repo: Path) -> str | None:
    """How this repo runs its tests, read from its own config, never guessed from habit."""
    repo = Path(repo)
    pkg = repo / "package.json"
    if pkg.exists():
        try:
            scripts = json.loads(pkg.read_text(encoding="utf-8")).get("scripts", {})
            if "test" in scripts:
                return "npm test"
        except (json.JSONDecodeError, OSError):
            pass
    mk = repo / "Makefile"
    if mk.exists() and re.search(r"^test:", mk.read_text(encoding="utf-8", errors="ignore"), re.M):
        return "make test"
    for script in ("scripts/test.sh", "scripts/test"):
        if (repo / script).exists():
            return f"bash {script}"
    pp = repo / "pyproject.toml"
    if pp.exists():
        try:
            data = tomllib.loads(pp.read_text(encoding="utf-8"))
        except (tomllib.TOMLDecodeError, OSError):
            data = {}
        if "pytest" in json.dumps(data.get("tool", {})) or (repo / "tests").exists():
            return "pytest"
    if (repo / "noxfile.py").exists():
        return "nox"
    if (repo / "tox.ini").exists():
        return "tox"
    if (repo / "go.mod").exists():
        return "go test ./..."
    if (repo / "Cargo.toml").exists():
        return "cargo test"
    return None
