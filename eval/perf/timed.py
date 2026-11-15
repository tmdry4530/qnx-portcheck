import subprocess, sys, time, os
out, label = sys.argv[1], sys.argv[2]
env = dict(os.environ)
start = time.perf_counter()
with open(out, "wb") as fh:
    rc = subprocess.run(sys.argv[3:], stdout=fh, env=env).returncode
el = time.perf_counter() - start
open(label, "w").write(f"exit={rc} seconds={el:.2f}\n")
