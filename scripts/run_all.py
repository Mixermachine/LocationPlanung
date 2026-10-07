"""run_all.py — gated pipeline. Build is only allowed with documented completeness.

Order: harvest_sources (optional) -> harvest_staedte -> audit_coverage -> cluster report -> GATE -> distances -> images -> site -> md

GATE fails (exit 2) if:
  - OFFEN-rustikal count > 0 (names not yet triaged/rejected), or
  - clusters still open (cluster_progress ledger).
Override: --force (documents the exception in .research/gate_overrides.txt).
"""
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(script, *args, capture=False):
    cmd = [sys.executable, str(ROOT / "scripts" / script), *args]
    print("==>", script, *args)
    r = subprocess.run(cmd, cwd=ROOT, capture_output=capture, text=True)
    if capture:
        return r.returncode, r.stdout + r.stderr
    return r.returncode, ""


def main():
    force = "--force" in sys.argv
    skip_harvest = "--skip-harvest" in sys.argv
    if not skip_harvest:
        run("harvest_sources.py")
        run("harvest_staedte.py")
    rc, out = run("audit_coverage.py", capture=True)
    print(out.strip())
    import json
    offen_r = len(json.loads((ROOT / ".research" / "offen_rustikal.json").read_text(encoding="utf-8")))
    rc2, out2 = run("cluster_progress.py", "--report", capture=True)
    line = out2.splitlines()[0] if out2 else "?"
    print(line)
    clusters_open = int(line.split()[2]) if line.split()[2].isdigit() else 999

    blocked = []
    if offen_r > 0:
        blocked.append(f"OFFEN-rustikal: {offen_r} Namen nicht triagiert/verworfen")
    if clusters_open > 0:
        blocked.append(f"Cluster offen: {clusters_open}/89 nicht abgearbeitet")
    if blocked and not force:
        print("\nBUILD BLOCKED — Vollständigkeit nicht dokumentiert:")
        for b in blocked:
            print("  [BLOCKED]", b)
        print("-> Abarbeiten ODER --force (wird in gate_overrides.txt protokolliert; Grund nachreichen!)")
        if force:
            pass
        sys.exit(2)
    if blocked and force:
        p = ROOT / ".research" / "gate_overrides.txt"
        with p.open("a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%F %T')} FORCE-Build: {'; '.join(blocked)}\n")
        print("GATE OVERRIDE protokolliert, baue trotzdem")

    run("distances_final.py")
    run("fetch_images.py")
    run("fetch_images2.py")
    run("build_site.py")
    run("build_md.py")
    print("PIPELINE OK")


if __name__ == "__main__":
    main()
