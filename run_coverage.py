
import subprocess

subprocess.run(["/home/jaimevalero/anaconda3/bin/coverage", "run", "-m", "unittest", "discover", "-p", "test_*.py", "-s", "tests"])
subprocess.run(["/home/jaimevalero/anaconda3/bin/coverage", "xml"])