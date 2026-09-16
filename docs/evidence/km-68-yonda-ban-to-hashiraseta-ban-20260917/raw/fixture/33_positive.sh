#!/bin/bash
# 33 の陽性対照(乙)―― pipe の後の $? を讀む形。此の file は鳴らねばならぬ。
ls /nonexistent | head -1
rc=$?
echo "rc=$rc"
