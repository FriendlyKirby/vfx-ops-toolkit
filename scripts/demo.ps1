Write-Host "== VFX Ops Toolkit Demo =="

if (-not (Get-Command toolkit -ErrorAction SilentlyContinue)) {
  Write-Error "toolkit command not found. Try: pip install -e "".[dev]"""
  exit 1
}

$repoRoot = (Resolve-Path ".").Path
$demoDb   = Join-Path $repoRoot "data\demo_tracking_db.json"
$demoCfg  = Join-Path $repoRoot "toolkit_demo.yaml"

Remove-Item -Force -ErrorAction SilentlyContinue $demoDb

@"
shows_root: "examples/shows"

naming:
  frame_prefix: "frame_"
  frame_padding: 4
  frame_ext: ".exr"

thresholds:
  disk_warning_mb: 500

tracking:
  backend: "json"
  json_path: "data/demo_tracking_db.json"
"@ | Set-Content -Encoding UTF8 $demoCfg

Write-Host "`n-- validate"
toolkit validate --config $demoCfg
Write-Host "validate exit code: $LASTEXITCODE"

Write-Host "`n-- validate (json)"
toolkit validate --config $demoCfg --json | Out-Host

Write-Host "`n-- disk"
toolkit disk --config $demoCfg
Write-Host "disk exit code: $LASTEXITCODE"

Write-Host "`n-- disk (json)"
toolkit disk --config $demoCfg --json | Out-Host

Write-Host "`n-- publish (json)"
toolkit publish --config $demoCfg --show demo_show --shot shot010 --version v001 --note "demo publish" --json | Out-Host
Write-Host "publish exit code: $LASTEXITCODE"

Write-Host "`n-- publish (human summary from latest record)"
toolkit list-publishes --config $demoCfg --show demo_show --limit 1 | Out-Host

Write-Host "`n-- list-publishes"
toolkit list-publishes --config $demoCfg --show demo_show
Write-Host "list-publishes exit code: $LASTEXITCODE"

Write-Host "`n-- list-publishes (json)"
toolkit list-publishes --config $demoCfg --json | Out-Host