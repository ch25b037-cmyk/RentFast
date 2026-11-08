#!/usr/bin/env python3
"""
CampusLend repository verifier. Cross-platform, standard library only.

Usage:
  python scripts/verify.py            normal run
  python scripts/verify.py --quick    static checks only (no linters, tests or builds)
  python scripts/verify.py --strict   warnings count as failures; also runs the frontend build

Exit code 0 = no failures, 1 = at least one failure.
Writes a report to docs/VERIFY_LAST_RUN.md.

Run it from the repo root, inside the activated backend virtualenv so that
ruff and pytest are importable.
"""
from __future__ import annotations

import argparse
import fnmatch
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SELF = Path(__file__).resolve()

SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache", ".ruff_cache",
    ".mypy_cache", "dist", "build", ".vite", "coverage", "htmlcov", "playwright-report",
    "test-results", "uploads",
}
SKIP_FILES = {"package-lock.json", "pnpm-lock.yaml", "yarn.lock"}
SKIP_SUFFIX = {".db", ".sqlite3", ".pyc", ".log", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".woff", ".woff2", ".ttf"}
CODE_EXT = {".py", ".js", ".jsx", ".mjs", ".cjs", ".json", ".yml", ".yaml", ".toml", ".ini", ".cfg", ".sh", ".css", ".html"}

REQUIRED = [
    "AGENTS.md",
    "README_FIRST.md",
    ".github/copilot-instructions.md",
    ".github/instructions/backend.instructions.md",
    ".github/instructions/frontend.instructions.md",
    ".github/instructions/env-secrets.instructions.md",
    ".github/instructions/docs-tracking.instructions.md",
    ".github/instructions/tests.instructions.md",
    ".github/agents/builder.agent.md",
    ".github/agents/auditor.agent.md",
    ".github/agents/ui-designer.agent.md",
    ".github/skills/fastapi-feature/SKILL.md",
    ".github/skills/react-feature/SKILL.md",
    ".github/skills/loan-safety/SKILL.md",
    ".github/skills/file-audit/SKILL.md",
    ".github/skills/progress-tracking/SKILL.md",
    ".github/skills/sleek-ui/SKILL.md",
    "docs/PROJECT_BRIEF.md", "docs/ARCHITECTURE.md", "docs/DATA_MODEL.md", "docs/API_CONTRACT.md",
    "docs/SAFETY_SPEC.md", "docs/DESIGN_SYSTEM.md", "docs/ROADMAP.md", "docs/PROGRESS.md",
    "docs/IMPROVEMENTS.md", "docs/DECISIONS.md", "docs/FILE_REGISTRY.md", "docs/ERRORS_LOG.md",
    "backend/.env.example", "frontend/.env.example", ".gitignore",
]
PROMPTS = ["kickoff", "build-milestone", "resume", "audit", "fix-errors", "ui-polish", "improve",
           "milestone-close", "security-review"]
REQUIRED += [f".github/prompts/{p}.prompt.md" for p in PROMPTS]

GENERATED_OK = {"docs/VERIFY_LAST_RUN.md"}


# --------------------------------------------------------------------------- helpers
class Report:
    def __init__(self) -> None:
        self.items: list[tuple[str, str, str, list[str]]] = []

    def add(self, level: str, area: str, msg: str, detail: list[str] | None = None) -> None:
        self.items.append((level, area, msg, detail or []))

    def count(self, level: str) -> int:
        return sum(1 for i in self.items if i[0] == level)


def iter_files(base: Path):
    if not base.exists():
        return
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            p = Path(dirpath) / name
            if name in SKIP_FILES or p.suffix in SKIP_SUFFIX:
                continue
            yield p


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def run(cmd: list[str], cwd: Path, timeout: int = 900) -> tuple[int | None, str]:
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace")
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except FileNotFoundError:
        return None, "command not found"
    except subprocess.TimeoutExpired:
        return 124, "timed out"


def tail(text: str, n: int = 25) -> list[str]:
    return text.strip().splitlines()[-n:]


FM = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.S)


def frontmatter(text: str) -> dict[str, str] | None:
    m = FM.match(text)
    if not m:
        return None
    data: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "\t", "#")):
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip().strip('"').strip("'")
    return data


def find_tool(name: str) -> list[str] | None:
    exe = shutil.which(name)
    if exe:
        return [exe]
    code, _ = run([sys.executable, "-m", name, "--version"], ROOT, 60)
    return [sys.executable, "-m", name] if code == 0 else None


# --------------------------------------------------------------------------- checks: harness
def check_harness(r: Report) -> None:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    if missing:
        r.add("FAIL", "harness", f"{len(missing)} required harness file(s) missing", missing)
    else:
        r.add("PASS", "harness", f"all {len(REQUIRED)} required harness files exist")

    problems: list[str] = []
    for p in sorted((ROOT / ".github/prompts").glob("*.prompt.md")):
        fm = frontmatter(read(p))
        if fm is None or not fm.get("description") or not fm.get("agent"):
            problems.append(f"{rel(p)}: needs frontmatter with description and agent")
    for p in sorted((ROOT / ".github/agents").glob("*.agent.md")):
        fm = frontmatter(read(p))
        if fm is None or not fm.get("description"):
            problems.append(f"{rel(p)}: needs frontmatter with description")
    for p in sorted((ROOT / ".github/instructions").glob("*.instructions.md")):
        fm = frontmatter(read(p))
        if fm is None or not fm.get("applyTo") or not fm.get("description"):
            problems.append(f"{rel(p)}: needs frontmatter with applyTo and description")
    skills_dir = ROOT / ".github/skills"
    if skills_dir.exists():
        for d in sorted(x for x in skills_dir.iterdir() if x.is_dir()):
            sk = d / "SKILL.md"
            if not sk.exists():
                problems.append(f"{rel(d)}: missing SKILL.md")
                continue
            fm = frontmatter(read(sk))
            if fm is None:
                problems.append(f"{rel(sk)}: missing frontmatter")
                continue
            if fm.get("name") != d.name:
                problems.append(f"{rel(sk)}: name '{fm.get('name')}' must equal folder '{d.name}'")
            if not re.fullmatch(r"[a-z0-9-]+", fm.get("name", "")):
                problems.append(f"{rel(sk)}: name must be lowercase letters, digits, hyphens")
            if len(fm.get("description", "")) < 40:
                problems.append(f"{rel(sk)}: description too short to be useful")
    if problems:
        r.add("FAIL", "harness", f"{len(problems)} frontmatter problem(s)", problems)
    else:
        r.add("PASS", "harness", "prompt, agent, instruction and skill frontmatter valid")

    ref_re = re.compile(r"`((?:docs|\.github|scripts)/[^`\s]+)`")
    bad: list[str] = []
    md_files = [ROOT / "AGENTS.md"] + list((ROOT / "docs").glob("*.md")) + list((ROOT / ".github").rglob("*.md"))
    for md in md_files:
        for ref in ref_re.findall(read(md)):
            ref = ref.rstrip(".,;:)")
            if any(c in ref for c in "*<>{}$…") or ref in GENERATED_OK:
                continue
            if not (ROOT / ref).exists():
                bad.append(f"{rel(md)} -> {ref}")
    if bad:
        r.add("FAIL", "harness", f"{len(bad)} broken file reference(s) in markdown", bad[:20])
    else:
        r.add("PASS", "harness", "all file references in markdown resolve")


# --------------------------------------------------------------------------- checks: env and secrets
def env_keys(p: Path) -> set[str]:
    return set(re.findall(r"^([A-Z][A-Z0-9_]*)=", read(p), re.M))


def check_env(r: Report) -> None:
    be_example = ROOT / "backend/.env.example"
    config = ROOT / "backend/app/core/config.py"
    if be_example.exists() and config.exists():
        example = {k.lower() for k in env_keys(be_example)}
        fields = set(re.findall(r"^ {4}([A-Za-z_]\w*)\s*:\s*[^=\n]+(?:=|$)", read(config), re.M))
        fields = {f for f in fields if f != "model_config" and not f.startswith("_")}
        only_example = sorted(example - fields)
        only_config = sorted(fields - example)
        if only_example or only_config:
            d = [f"in .env.example but not in config.py: {k}" for k in only_example]
            d += [f"in config.py but not in .env.example: {k}" for k in only_config]
            r.add("FAIL", "env", "backend .env.example and config.py are out of sync", d)
        else:
            r.add("PASS", "env", f"backend config.py and .env.example agree ({len(example)} variables)")
    else:
        r.add("INFO", "env", "backend config.py not created yet; env sync check skipped")

    fe_example = ROOT / "frontend/.env.example"
    src = ROOT / "frontend/src"
    if src.exists():
        used: set[str] = set()
        for p in iter_files(src):
            used |= set(re.findall(r"import\.meta\.env\.(VITE_[A-Z0-9_]+)", read(p)))
        missing = sorted(used - env_keys(fe_example))
        if missing:
            r.add("FAIL", "env", "frontend uses env vars missing from frontend/.env.example", missing)
        else:
            r.add("PASS", "env", "frontend env vars are documented")
    risky = [k for k in env_keys(fe_example) if re.search(r"SECRET|PASSWORD|PRIVATE|TOKEN|KEY", k)]
    if risky:
        r.add("FAIL", "env", "frontend env example contains secret-looking names (they ship to the browser)", risky)

    gi = read(ROOT / ".gitignore")
    if not re.search(r"^\.env\s*$", gi, re.M) or "!.env.example" not in gi:
        r.add("FAIL", "env", ".gitignore must ignore .env and keep !.env.example")
    else:
        r.add("PASS", "env", ".gitignore protects .env files")

    if (ROOT / ".git").exists() and shutil.which("git"):
        code, out = run(["git", "ls-files"], ROOT, 60)
        if code == 0:
            tracked = [f for f in out.splitlines() if re.search(r"(^|/)\.env(\.[^/]*)?$", f) and not f.endswith(".env.example")]
            if tracked:
                r.add("FAIL", "env", "real .env file(s) are tracked by git", tracked)
            else:
                r.add("PASS", "env", "no real .env files tracked by git")


SECRET_PATTERNS = [
    (re.compile("-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE " + "KEY-----"), "private key"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key id"),
    (re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"), "GitHub token"),
    (re.compile(r"sk-[A-Za-z0-9]{32,}"), "API key (sk-...)"),
    (re.compile(r"(?i)\b(secret|api[_-]?key|password|passwd|token)\w*\s*[:=]\s*[\"'][A-Za-z0-9_\-/+=.]{16,}[\"']"),
     "hard-coded credential"),
]
SECRET_OK = re.compile(r"(?i)example|change-?me|placeholder|fake|dummy|test|xxxx|your[_-]|<.*>|\$\{|os\.environ|getenv")


def check_secrets(r: Report) -> None:
    hits: list[str] = []
    for p in iter_files(ROOT):
        if p.resolve() == SELF or p.suffix not in CODE_EXT and not p.name.startswith(".env"):
            continue
        if p.name == ".env.example":
            continue
        for n, line in enumerate(read(p).splitlines(), 1):
            for pat, label in SECRET_PATTERNS:
                if pat.search(line) and not (label == "hard-coded credential" and SECRET_OK.search(line)):
                    hits.append(f"{rel(p)}:{n}: possible {label}")
    real_env = [rel(p) for p in iter_files(ROOT) if re.fullmatch(r"\.env(\.[^.]+)?", p.name) and p.name != ".env.example"]
    if hits:
        r.add("FAIL", "secrets", f"{len(hits)} possible secret(s) in files", hits[:20])
    else:
        r.add("PASS", "secrets", "no secret patterns found")
    if real_env:
        r.add("INFO", "secrets", "local .env file(s) present (fine if git-ignored; never share them)", real_env)


# --------------------------------------------------------------------------- checks: code hygiene
class Rule:
    def __init__(self, name, regex, roots, exts, level, msg, skip=()):
        self.name, self.regex, self.roots, self.exts = name, re.compile(regex), roots, exts
        self.level, self.msg, self.skip = level, msg, skip


RULES = [
    Rule("placeholders-be", r"\b(TODO|FIXME|XXX)\b|NotImplementedError", ["backend"], {".py"}, "WARN",
         "placeholder markers in backend code (finished work must have none)", ("alembic/versions",)),
    Rule("print-be", r"^\s*print\(", ["backend/app"], {".py"}, "WARN", "print() in backend app code; use the logger"),
    Rule("random-be", r"^\s*(import random|from random import)", ["backend/app"], {".py"}, "WARN",
         "'random' module used; codes and tokens must use 'secrets'"),
    Rule("utcnow-be", r"datetime\.utcnow\(", ["backend"], {".py"}, "WARN", "datetime.utcnow(); use core/clock.py"),
    Rule("placeholders-fe", r"\b(TODO|FIXME|XXX)\b", ["frontend/src"], {".js", ".jsx", ".css"}, "WARN",
         "placeholder markers in frontend code"),
    Rule("console-fe", r"console\.log\(", ["frontend/src"], {".js", ".jsx"}, "WARN", "console.log left in frontend code"),
    Rule("xss-fe", r"dangerouslySetInnerHTML", ["frontend/src"], {".js", ".jsx"}, "FAIL",
         "dangerouslySetInnerHTML is forbidden (render user text as text)"),
    Rule("storage-fe", r"(?i)(localStorage|sessionStorage)\.\w+\(.*(token|jwt|code|otp)", ["frontend/src"], {".js", ".jsx"},
         "FAIL", "token or code written to browser storage"),
    Rule("fetch-fe", r"\b(fetch|axios)\s*\(", ["frontend/src/components", "frontend/src/pages"], {".js", ".jsx"},
         "WARN", "network call inside components/pages; use src/api + hooks"),
    Rule("hex-fe", r"#[0-9a-fA-F]{6}\b", ["frontend/src"], {".js", ".jsx", ".css"}, "WARN",
         "raw hex colour outside tokens.css; use design tokens", ("tokens.css", ".test.", "/tests/")),
]


def check_hygiene(r: Report) -> None:
    any_code = False
    for rule in RULES:
        hits: list[str] = []
        for root in rule.roots:
            for p in iter_files(ROOT / root):
                if p.suffix not in rule.exts:
                    continue
                path = rel(p)
                if any(s in path for s in rule.skip):
                    continue
                if rule.name in ("print-be", "random-be") and "/tests/" in path:
                    continue
                any_code = True
                for n, line in enumerate(read(p).splitlines(), 1):
                    if rule.regex.search(line):
                        hits.append(f"{path}:{n}")
        if hits:
            r.add(rule.level, "hygiene", f"{rule.msg} ({len(hits)})", hits[:8])
    if not any_code:
        r.add("INFO", "hygiene", "no application code yet; hygiene scan skipped")
    else:
        r.add("PASS", "hygiene", "hygiene scan completed (see warnings above, if any)")


def check_layering(r: Report) -> None:
    svc = ROOT / "backend/app/services"
    rtr = ROOT / "backend/app/routers"
    bad: list[str] = []
    for p in iter_files(svc):
        if p.suffix == ".py" and re.search(r"^\s*(from|import)\s+fastapi", read(p), re.M):
            bad.append(f"{rel(p)}: services must not import fastapi")
    warn: list[str] = []
    for p in iter_files(rtr):
        if p.suffix != ".py":
            continue
        for n, line in enumerate(read(p).splitlines(), 1):
            if re.search(r"\.query\(|\bselect\(|\.execute\(", line):
                warn.append(f"{rel(p)}:{n}: query in router; move it to a service")
    if bad:
        r.add("FAIL", "layering", f"{len(bad)} layering violation(s)", bad[:15])
    if warn:
        r.add("WARN", "layering", f"{len(warn)} query call(s) inside routers", warn[:10])
    if not bad and not warn and svc.exists():
        r.add("PASS", "layering", "backend layering rules hold")


# --------------------------------------------------------------------------- checks: registry and contract
def check_registry(r: Report) -> None:
    reg = read(ROOT / "docs/FILE_REGISTRY.md")
    registered: list[str] = []
    for line in reg.splitlines():
        if line.startswith("|"):
            cell = line.split("|")[1].strip().strip("`")
            if cell and cell != "path" and not set(cell) <= set("-: "):
                registered.append(cell)
    files: list[str] = []
    for base in (ROOT / "backend", ROOT / "frontend"):
        for p in iter_files(base):
            if p.name == ".env" or p.name == ".gitkeep":
                continue
            files.append(rel(p))
    for p in iter_files(ROOT / "scripts"):
        files.append(rel(p))
    files += [f for f in (".gitignore", "AGENTS.md", "README_FIRST.md") if (ROOT / f).exists()]
    for p in iter_files(ROOT / ".vscode"):
        files.append(rel(p))

    def covered(path: str) -> bool:
        return any(path == g or ("*" in g and fnmatch.fnmatch(path, g)) for g in registered)

    unregistered = sorted(f for f in files if not covered(f))
    dead = sorted(g for g in registered
                  if "*" not in g and not (ROOT / g).exists()
                  or "*" in g and not any(fnmatch.fnmatch(f, g) for f in files + [rel(x) for x in iter_files(ROOT / ".github")]
                                          + [rel(x) for x in iter_files(ROOT / "docs")]))
    if unregistered:
        r.add("WARN", "registry", f"{len(unregistered)} file(s) not in docs/FILE_REGISTRY.md "
              "(patterns like backend/alembic/versions/*.py are allowed)", unregistered[:15])
    if dead:
        r.add("WARN", "registry", f"{len(dead)} registry row(s) point to missing files", dead[:15])
    if not unregistered and not dead:
        r.add("PASS", "registry", f"file registry matches the repository ({len(registered)} rows)")


def norm_route(path: str) -> str:
    path = re.sub(r"^/api/v\d+", "", path)
    path = re.sub(r"\{[^}]*\}", "{}", path)
    return (path.rstrip("/") or "/")


def check_contract(r: Report) -> None:
    routers = ROOT / "backend/app/routers"
    if not routers.exists():
        r.add("INFO", "contract", "no routers yet; contract drift check skipped")
        return
    contract_paths: set[str] = set()
    for line in read(ROOT / "docs/API_CONTRACT.md").splitlines():
        if line.startswith("|"):
            cells = line.split("|")
            if len(cells) > 3:
                for m in re.findall(r"`(/[^`\s]*)`", cells[2]):
                    contract_paths.add(norm_route(m))
    code_paths: set[str] = set()
    for p in iter_files(routers):
        if p.suffix != ".py":
            continue
        text = read(p)
        pm = re.search(r"APIRouter\([^)]*prefix\s*=\s*[\"']([^\"']*)[\"']", text)
        prefix = pm.group(1) if pm else ""
        for m in re.finditer(r"@\w+\.(?:get|post|patch|put|delete)\(\s*[\"']([^\"']*)[\"']", text):
            code_paths.add(norm_route(prefix + m.group(1)))
    extra = sorted(code_paths - contract_paths)
    done = len(code_paths & contract_paths)
    r.add("INFO", "contract", f"{done} of {len(contract_paths)} contract routes implemented so far")
    if extra:
        r.add("WARN", "contract", f"{len(extra)} route(s) in code but not in docs/API_CONTRACT.md "
              "(update the contract and log a decision)", extra[:15])
    else:
        r.add("PASS", "contract", "no routes outside the contract")


# --------------------------------------------------------------------------- checks: run tools
def check_backend(r: Report, quick: bool) -> None:
    be = ROOT / "backend"
    if not (be / "app").exists():
        r.add("INFO", "backend", "backend/app not created yet; backend checks skipped")
        return
    code, out = run([sys.executable, "-m", "compileall", "-q", "app", "tests"] if (be / "tests").exists()
                    else [sys.executable, "-m", "compileall", "-q", "app"], be, 300)
    if code == 0:
        r.add("PASS", "backend", "python files compile")
    else:
        r.add("FAIL", "backend", "compile errors", tail(out))
    if quick:
        r.add("INFO", "backend", "--quick: ruff and pytest skipped")
        return
    ruff = find_tool("ruff")
    if ruff:
        code, out = run(ruff + ["check", "."], be, 300)
        r.add("PASS" if code == 0 else "FAIL", "backend", "ruff check" + ("" if code == 0 else " failed"),
              [] if code == 0 else tail(out))
    else:
        r.add("WARN", "backend", "ruff not installed (pip install -r requirements-dev.txt)")
    tests = [p for p in iter_files(be / "tests") if p.name.startswith("test_") and p.suffix == ".py"]
    if not tests:
        r.add("WARN", "backend", "no backend tests found yet")
        return
    code, out = run([sys.executable, "-m", "pytest", "-q"], be, 900)
    if code == 0:
        summary = next((l for l in reversed(out.strip().splitlines()) if "passed" in l), "pytest passed")
        r.add("PASS", "backend", f"pytest: {summary.strip()}")
    elif code == 5:
        r.add("WARN", "backend", "pytest collected no tests")
    elif "No module named pytest" in out:
        r.add("WARN", "backend", "pytest not installed (pip install -r requirements-dev.txt)")
    else:
        r.add("FAIL", "backend", "pytest failed", tail(out, 30))


def check_frontend(r: Report, quick: bool, strict: bool) -> None:
    fe = ROOT / "frontend"
    if not (fe / "package.json").exists():
        r.add("INFO", "frontend", "frontend/package.json not created yet; frontend checks skipped")
        return
    if quick:
        r.add("INFO", "frontend", "--quick: lint, tests and build skipped")
        return
    npm = shutil.which("npm")
    if not npm:
        r.add("WARN", "frontend", "npm not found on PATH")
        return
    if not (fe / "node_modules").exists():
        r.add("WARN", "frontend", "node_modules missing; run 'npm install' in frontend/")
        return
    code, out = run([npm, "run", "--if-present", "lint"], fe, 600)
    r.add("PASS" if code == 0 else "FAIL", "frontend", "npm run lint" + ("" if code == 0 else " failed"),
          [] if code == 0 else tail(out))
    code, out = run([npm, "run", "--if-present", "test", "--", "--run"], fe, 900)
    r.add("PASS" if code == 0 else "FAIL", "frontend", "npm test" + ("" if code == 0 else " failed"),
          [] if code == 0 else tail(out, 30))
    if strict:
        code, out = run([npm, "run", "--if-present", "build"], fe, 900)
        r.add("PASS" if code == 0 else "FAIL", "frontend", "npm run build" + ("" if code == 0 else " failed"),
              [] if code == 0 else tail(out))
    else:
        r.add("INFO", "frontend", "build skipped (it runs with --strict)")


# --------------------------------------------------------------------------- checks: docs health
def check_docs(r: Report) -> None:
    prog = ROOT / "docs/PROGRESS.md"
    text = read(prog)
    m = re.search(r"## NEXT ACTION\s*\n(.+?)(\n## |\Z)", text, re.S)
    if not m or len(m.group(1).strip()) < 20:
        r.add("FAIL", "docs", "docs/PROGRESS.md has no usable NEXT ACTION section")
    else:
        r.add("PASS", "docs", "PROGRESS.md has a NEXT ACTION")
    newest = 0.0
    for base in (ROOT / "backend", ROOT / "frontend"):
        for p in iter_files(base):
            if p.name.startswith(".env"):
                continue
            newest = max(newest, p.stat().st_mtime)
    if newest and prog.exists() and newest - prog.stat().st_mtime > 7200:
        hours = (newest - prog.stat().st_mtime) / 3600
        r.add("WARN", "docs", f"PROGRESS.md looks stale: code changed {hours:.1f}h after its last update")
    unresolved = len(re.findall(r"Status:\s*UNRESOLVED", read(ROOT / "docs/ERRORS_LOG.md")))
    if unresolved:
        r.add("WARN", "docs", f"{unresolved} UNRESOLVED entr{'y' if unresolved == 1 else 'ies'} in docs/ERRORS_LOG.md")


# --------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description="CampusLend repository verifier")
    ap.add_argument("--quick", action="store_true", help="static checks only")
    ap.add_argument("--strict", action="store_true", help="warnings fail; run the frontend build")
    args = ap.parse_args()

    started = time.time()
    r = Report()
    check_harness(r)
    check_env(r)
    check_secrets(r)
    check_hygiene(r)
    check_layering(r)
    check_registry(r)
    check_contract(r)
    check_backend(r, args.quick)
    check_frontend(r, args.quick, args.strict)
    check_docs(r)

    if args.strict:
        r.items = [("FAIL" if lvl == "WARN" else lvl, a, m, d) for lvl, a, m, d in r.items]

    lines: list[str] = []
    for lvl, area, msg, detail in r.items:
        lines.append(f"[{lvl:4}] {area}: {msg}")
        for d in detail:
            lines.append(f"         - {d}")
    fails, warns = r.count("FAIL"), r.count("WARN")
    summary = (f"RESULT: {'FAIL' if fails else 'PASS'} | pass={r.count('PASS')} warn={warns} "
               f"fail={fails} info={r.count('INFO')} | mode={'strict' if args.strict else 'quick' if args.quick else 'normal'} "
               f"| {time.time() - started:.1f}s")
    print("\n".join(lines))
    print("\n" + summary)

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    report = ["# Last verify run", "", f"Run at {stamp}. Generated by `scripts/verify.py`; do not edit.", "",
              f"**{summary}**", "", "```", *lines, "```", ""]
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs/VERIFY_LAST_RUN.md").write_text("\n".join(report), encoding="utf-8")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
