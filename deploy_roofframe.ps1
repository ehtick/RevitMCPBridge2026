# deploy_roofframe.ps1 — deploy freshly-built Release DLL (analyzeRoofFraming) into Addins\2026.
# Kills Revit (caller confirmed model unmodified), backs up current DLL, copies Release build.
$ErrorActionPreference = 'Stop'
$dst   = Join-Path $env:APPDATA 'Autodesk\Revit\Addins\2026'
$src   = 'D:\RevitMCPBridge2026\bin\Release'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'

Get-Process -Name 'Revit' -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 3

$dllDst = Join-Path $dst 'RevitMCPBridge2026.dll'
if (Test-Path $dllDst) {
    Copy-Item $dllDst (Join-Path $dst "RevitMCPBridge2026.dll.bak-$stamp-preroofframe") -Force
    Write-Host "Backed up current DLL"
}
Copy-Item (Join-Path $src 'RevitMCPBridge2026.dll') $dllDst -Force
$depsSrc = Join-Path $src 'RevitMCPBridge2026.deps.json'
if (Test-Path $depsSrc) { Copy-Item $depsSrc (Join-Path $dst 'RevitMCPBridge2026.deps.json') -Force }

$info = Get-Item $dllDst
Write-Host ("Deployed -> {0}" -f $dllDst)
Write-Host ("  size: {0} bytes   modified: {1}" -f $info.Length, $info.LastWriteTime)
