"""Scan every eval project with the current scanner and compare findings with eval/results/real (scanner 511aa2e)."""
import json, subprocess, sys, time, pathlib
repo = pathlib.Path(sys.argv[1]); work = pathlib.Path(sys.argv[2]); out = pathlib.Path(sys.argv[3])
keys = ["rule_id","severity","file","line","col","message","suggestion","doc_url","confidence"]
rows = []; total_old = total_new = 0
for res in sorted((repo/"eval/results/real").glob("*.json")):
    if res.name == "summary.json": continue
    name = res.stem
    stored = json.loads(res.read_text())
    old = [{k: f[k] for k in keys} for f in stored["findings"]]
    t = time.perf_counter()
    p = subprocess.run(["qnx-portcheck","scan",str(work/name),"--format","json","--fail-on","never"],capture_output=True,text=True)
    el = time.perf_counter()-t
    new = [{k: f[k] for k in keys} for f in json.loads(p.stdout)["findings"]]
    (out/f"{name}.json").write_text(p.stdout)
    rows.append((name, stored["durations"]["scan"], el, len(old), len(new), old == new))
    total_old += stored["durations"]["scan"]; total_new += el
    print(rows[-1], flush=True)
lines = ["| project | scan s (511aa2e, eval run) | scan s (perf) | findings old | findings new | identical |","|---|---:|---:|---:|---:|---|"]
lines += [f"| {r[0]} | {r[1]:.2f} | {r[2]:.2f} | {r[3]} | {r[4]} | {'yes' if r[5] else 'NO'} |" for r in rows]
lines.append(f"| **total** | {total_old:.1f} | {total_new:.1f} | {sum(r[3] for r in rows)} | {sum(r[4] for r in rows)} | {'all' if all(r[5] for r in rows) else 'NOT ALL'} |")
(out/"table.md").write_text("\n".join(lines)+"\n")
