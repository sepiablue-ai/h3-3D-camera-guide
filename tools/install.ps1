param([Parameter(Mandatory=$true)][string]$ComfyRoot)
$ErrorActionPreference = 'Stop'
$source = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$parent = (Resolve-Path -LiteralPath (Join-Path $ComfyRoot 'custom_nodes')).Path
$target = Join-Path $parent 'h3-3D-camera-guide'
if (Test-Path -LiteralPath $target) {
    $existing = Get-Item -LiteralPath $target
    if ($existing.LinkType -eq 'Junction' -and $existing.Target -contains $source) {
        Write-Output "Already installed: $target"
        exit 0
    }
    throw "Destination exists; nothing overwritten: $target"
}
New-Item -ItemType Junction -Path $target -Target $source | Out-Null
Write-Output "Installed: $target -> $source"
