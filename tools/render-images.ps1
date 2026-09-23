# Renders the social preview card and the Apple touch icon from their HTML sources
# with headless Edge (or Chrome). Writes only to public/. Safe to re-run.
#
#   .\tools\render-images.ps1

$ErrorActionPreference = 'Stop'

$browser = @(
  "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
  "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
  "$env:ProgramFiles\Google\Chrome\Application\chrome.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $browser) { throw 'Edge or Chrome is required to render the images.' }

# A separate profile stops headless mode from handing off to an already-open browser window.
$profileDir = Join-Path $env:TEMP 'portfolio-render-profile'
$root = Split-Path -Parent $PSScriptRoot
$jobs = @(
  @{ Source = 'tools\social-card.html'; Output = 'public\og-image.png'; Size = '1200,630' },
  @{ Source = 'tools\touch-icon.html'; Output = 'public\apple-touch-icon.png'; Size = '180,180' }
)

foreach ($job in $jobs) {
  $source = Join-Path $root $job.Source
  $output = Join-Path $root $job.Output
  # Clear the previous render so a failed run can't pass the check below with a stale file.
  if (Test-Path $output) { Remove-Item $output }
  $arguments = @(
    '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
    "--user-data-dir=$profileDir", "--window-size=$($job.Size)", "--screenshot=$output",
    ([System.Uri]$source).AbsoluteUri
  )
  Start-Process -FilePath $browser -ArgumentList $arguments -Wait -WindowStyle Hidden
  if (-not (Test-Path $output)) { throw "Rendering failed: $($job.Output)" }
  Write-Host "Rendered $($job.Output)"
}
