# Link every skill in ./skills into ~/.claude/skills (directory junctions, no admin rights needed).
$dest = Join-Path $HOME ".claude\skills"
New-Item -ItemType Directory -Force $dest | Out-Null
Get-ChildItem (Join-Path $PSScriptRoot "skills") -Directory | ForEach-Object {
    $link = Join-Path $dest $_.Name
    if (Test-Path $link) {
        Write-Host "skipped  $($_.Name) (already in $dest)"
    } else {
        New-Item -ItemType Junction -Path $link -Target $_.FullName | Out-Null
        Write-Host "linked   $($_.Name) -> $($_.FullName)"
    }
}
