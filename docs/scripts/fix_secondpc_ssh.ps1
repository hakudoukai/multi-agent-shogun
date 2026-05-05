# =============================================================
# fix_secondpc_ssh.ps1 - SecondPC SSH 自動復旧スクリプト
# =============================================================
# 作成: 2026-05-05 22:30 by 将軍
# 用途: SecondPC で SSH 接続が timeout した時の一発修復
# 実行: PowerShell を「管理者として実行」で開いて
#       PowerShell -ExecutionPolicy Bypass -File fix_secondpc_ssh.ps1
# 効果:
#   1. WSL2 NAT (winnat/hns) を再起動
#   2. WSL2 を完全 shutdown して再起動
#   3. WSL Ubuntu 内で sshd を起動
#   4. WSL2 の現在IPを取得
#   5. Windows portproxy を新IPで再設定
#   6. Windows Firewall ルールを再作成
#   7. localhost / WSL直接 / LAN の3経路で SSH テスト
# =============================================================

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "=== SecondPC SSH Recovery v1.0 ===" -ForegroundColor Cyan
Write-Host ""

# 管理者チェック
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: 管理者権限が必要です。Windows Terminal を「管理者として実行」で開き直してください。" -ForegroundColor Red
    exit 1
}

# 1. NAT 再起動
Write-Host "[1/7] WSL2 NAT services restart..." -ForegroundColor Yellow
Restart-Service hns,winnat -Force -ErrorAction SilentlyContinue
Write-Host "      done." -ForegroundColor Green

# 2. WSL 完全停止
Write-Host "[2/7] WSL --shutdown..." -ForegroundColor Yellow
wsl --shutdown
Start-Sleep -Seconds 8
Write-Host "      done." -ForegroundColor Green

# 3. WSL 起動 + sshd 起動
Write-Host "[3/7] WSL boot + sshd start..." -ForegroundColor Yellow
wsl -d Ubuntu -- sudo systemctl start ssh
Start-Sleep -Seconds 2
Write-Host "      done." -ForegroundColor Green

# 4. WSL2 IP 取得
Write-Host "[4/7] WSL IP detect..." -ForegroundColor Yellow
$wslIp = (wsl -d Ubuntu -- hostname -I).Trim().Split()[0]
if (-not $wslIp) {
    Write-Host "ERROR: WSL IP取得失敗" -ForegroundColor Red
    exit 2
}
Write-Host "      WSL IP: $wslIp" -ForegroundColor Green

# 5. portproxy 更新
Write-Host "[5/7] Windows portproxy update..." -ForegroundColor Yellow
netsh interface portproxy delete v4tov4 listenport=22 listenaddress=0.0.0.0 2>$null | Out-Null
netsh interface portproxy add v4tov4 listenport=22 listenaddress=0.0.0.0 connectport=22 connectaddress=$wslIp | Out-Null
Write-Host "      done." -ForegroundColor Green

# 6. Firewall ルール
Write-Host "[6/7] Firewall rule rebuild..." -ForegroundColor Yellow
Get-NetFirewallRule -DisplayName "WSL SSH*" -ErrorAction SilentlyContinue | Remove-NetFirewallRule -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "WSL SSH" -Direction Inbound -Protocol TCP -LocalPort 22 -Action Allow -Profile Any | Out-Null
Write-Host "      done." -ForegroundColor Green

# 7. SSH テスト 3経路
Write-Host "[7/7] SSH connectivity tests..." -ForegroundColor Yellow
Write-Host ""

Write-Host "  Test 1: Direct WSL ($wslIp)" -ForegroundColor Cyan
$r1 = ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -o BatchMode=yes "hakudokai@$wslIp" "echo DIRECT_OK; hostname" 2>&1
$r1 | ForEach-Object { Write-Host "    $_" }

Write-Host ""
Write-Host "  Test 2: localhost:22 (portproxy)" -ForegroundColor Cyan
$r2 = ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -o BatchMode=yes "hakudokai@127.0.0.1" "echo PORTPROXY_OK; hostname" 2>&1
$r2 | ForEach-Object { Write-Host "    $_" }

Write-Host ""
Write-Host "  Test 3: 192.168.11.47 (LAN)" -ForegroundColor Cyan
$r3 = ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -o BatchMode=yes "hakudokai@192.168.11.47" "echo LAN_OK; hostname" 2>&1
$r3 | ForEach-Object { Write-Host "    $_" }

Write-Host ""
Write-Host "=== Complete ===" -ForegroundColor Green
Write-Host "WSL IP   : $wslIp"
Write-Host "From MainPC test: ssh hakudokai@192.168.11.47"
Write-Host ""
Write-Host "If Test 3 (LAN) succeeded => MainPC can now SSH."
Write-Host "If only Test 1 succeeded  => Firewall/portproxy still blocked."
Write-Host "If all failed             => WSL2 vSwitch dead, contact 将軍."
