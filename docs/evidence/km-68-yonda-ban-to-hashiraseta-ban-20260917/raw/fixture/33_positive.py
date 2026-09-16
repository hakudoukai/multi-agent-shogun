# 33 の陽性対照(甲)―― shell=True の cmd に | が在る形。此の file は鳴らねばならぬ。
import subprocess
p = subprocess.run("false | true", shell=True)
print(p.returncode)
