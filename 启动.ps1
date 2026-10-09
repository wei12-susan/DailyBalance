param(
  [Parameter(Mandatory=$true)][string]$AppDirectory,
  [Parameter(Mandatory=$true)][string]$NodeExecutable
)

$ErrorActionPreference = 'Stop'
$AppDirectory = [System.IO.Path]::GetFullPath($AppDirectory)
$nodeScript = Join-Path $AppDirectory 'app.js'
$dataFile = Join-Path $AppDirectory 'data.json'
$url = 'http://127.0.0.1:38472/'

function Open-JournalPage {
  $edgeCandidates = @(
    (Join-Path $env:ProgramFiles 'Microsoft\Edge\Application\msedge.exe'),
    (Join-Path ${env:ProgramFiles(x86)} 'Microsoft\Edge\Application\msedge.exe'),
    (Join-Path $env:LocalAppData 'Microsoft\Edge\Application\msedge.exe')
  )
  foreach ($edge in $edgeCandidates) {
    if ($edge -and (Test-Path -LiteralPath $edge)) {
      Start-Process -FilePath $edge -ArgumentList @('--new-window', $url)
      return
    }
  }
  Start-Process $url
}

try {
  $existing = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 1 -ErrorAction SilentlyContinue
  if ($existing.StatusCode -eq 200) {
    Open-JournalPage
    exit 0
  }
} catch {}

$env:JOURNAL_PORT = '38472'
$env:JOURNAL_DATA_FILE = $dataFile
$process = Start-Process -FilePath $NodeExecutable -ArgumentList @($nodeScript) -WorkingDirectory $AppDirectory -WindowStyle Hidden -PassThru

for ($i = 0; $i -lt 40; $i++) {
  Start-Sleep -Milliseconds 250
  try {
    $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 1
    if ($response.StatusCode -eq 200) {
      Open-JournalPage
      exit 0
    }
  } catch {
    if ($process.HasExited) {
      throw "Local service exited immediately with code $($process.ExitCode). Check that app.js and index.html are in the same folder."
    }
  }
}
throw 'Timed out waiting for the local web service. Check that Node.js is installed.'
