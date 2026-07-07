param(
    [Parameter(Mandatory=$true)]
    [string]$RepoUrl,
    [string]$MirrorDir = "repo-mirror.git",
    [string]$ReplacementsFile = "../replacements.txt"
)

Write-Host "Starting secret purge for repository: $RepoUrl"

# Ensure git is available
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "git is not installed or not in PATH. Install Git and rerun this script."
    exit 1
}

# Ensure git-filter-repo is available; try to run it, otherwise install via pip
try {
    git filter-repo --version > $null 2>&1
} catch {
    Write-Host "git-filter-repo not found. Attempting to install via pip..."
    python -m pip install --user git-filter-repo
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install git-filter-repo. Install it manually: https://github.com/newren/git-filter-repo"
        exit 1
    }
}

if (-not (Test-Path $ReplacementsFile)) {
    Write-Error "Replacements file not found: $ReplacementsFile"
    exit 1
}

Write-Host "Cloning mirror repository..."
git clone --mirror $RepoUrl $MirrorDir
if ($LASTEXITCODE -ne 0) { Write-Error "git clone failed."; exit 1 }

Set-Location $MirrorDir

Write-Host "Running git-filter-repo with replacements..."
git filter-repo --replace-text $ReplacementsFile
if ($LASTEXITCODE -ne 0) { Write-Error "git-filter-repo failed."; exit 1 }

Write-Host "Pushing rewritten history to remote (force)..."
git push --force --all
git push --force --tags

Write-Host "Cleanup: you can remove the mirror folder: $MirrorDir"
Write-Host "Done. Remember to rotate the compromised API key immediately and inform collaborators."
