$ErrorActionPreference = 'Stop'
$taskRoot = $PSScriptRoot
$taskUrl = 'http://localhost:18765'
$taskHealthUrl = 'http://127.0.0.1:18765/api/health'
$ready = $false
try { $health = Invoke-RestMethod $taskHealthUrl -TimeoutSec 3; $ready = ($health.app -eq 'gre-study') } catch {}
if (-not $ready) {
    $nodePath = Join-Path $taskRoot 'runtime/node.exe'
    $serverPath = Join-Path $taskRoot 'server.cjs'
    Start-Process -FilePath $nodePath -ArgumentList ('"' + $serverPath + '"') -WorkingDirectory $taskRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $taskRoot 'server.log') -RedirectStandardError (Join-Path $taskRoot 'server-error.log')
    for ($attempt = 0; $attempt -lt 20; $attempt++) {
        Start-Sleep -Milliseconds 300
        try { $health = Invoke-RestMethod $taskHealthUrl -TimeoutSec 3; if ($health.app -eq 'gre-study') { $ready = $true; break } } catch {}
    }
}
if ($ready) { Start-Process $taskUrl } else { throw 'Website could not start. See server-error.log in the website folder.' }
