# -*- coding: utf-8 -*-
"""走らせ器 10(第45弾・第51弾は第50弾を写した)。argv = <名> <cmd...>。子を subprocess で走らせ、stdout/stderr/rc を kaki の作法で raw/<名>.stdout/.err/.rc に書く(shell の > を使はぬ ―― 生の捕へは正規化を跳ぶ故)。rc は子の returncode 直採・己の rc = 子の rc。"""
import sys, subprocess, os
E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E); import kaki as K
name = sys.argv[1]; cmd = sys.argv[2:]
p = subprocess.run(cmd, capture_output=True)
K.kaku(f'{E}/{name}.stdout', p.stdout.decode('utf-8', 'replace')); K.kaku(f'{E}/{name}.err', p.stderr.decode('utf-8', 'replace')); K.kaku(f'{E}/{name}.rc', str(p.returncode))
sys.stdout.write(p.stdout.decode('utf-8', 'replace')); sys.stderr.write(p.stderr.decode('utf-8', 'replace')); sys.exit(p.returncode)
