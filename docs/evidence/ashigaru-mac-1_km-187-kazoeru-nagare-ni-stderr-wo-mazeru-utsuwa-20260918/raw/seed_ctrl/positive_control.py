r = subprocess.run(["git","status"], stderr=subprocess.STDOUT, capture_output=True)
n = len(r.stdout.splitlines())
