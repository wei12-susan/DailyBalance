param(
  [Parameter(Mandatory=$true)][string]$SourcePath,
  [switch]$Force
)

$ErrorActionPreference = 'Stop'
$SourcePath = [System.IO.Path]::GetFullPath($SourcePath)
$outputPath = Join-Path $PSScriptRoot 'foods.local.json'

if (-not (Test-Path -LiteralPath $SourcePath -PathType Leaf)) {
  throw "找不到食物成分表：$SourcePath"
}

$excel = $null
$workbook = $null
try {
  $excel = New-Object -ComObject Excel.Application
  $excel.Visible = $false
  $excel.DisplayAlerts = $false
  $excel.EnableEvents = $false
  try { $excel.AutomationSecurity = 3 } catch {}
  $workbook = $excel.Workbooks.Open($SourcePath, 0, $true)
  try { $sheet = $workbook.Worksheets.Item('能量和食物一般营养成分') }
  catch { throw '所选工作簿中没有「能量和食物一般营养成分」工作表。' }

  $used = $sheet.UsedRange
  $foods = [System.Collections.Generic.List[object]]::new()
  for ($row = 4; $row -le $used.Rows.Count; $row++) {
    $code = [string]$sheet.Cells.Item($row, 1).Text
    $name = ([string]$sheet.Cells.Item($row, 2).Text).Trim()
    $edibleValue = $sheet.Cells.Item($row, 3).Value2
    $kcalValue = $sheet.Cells.Item($row, 5).Value2
    $proteinValue = $sheet.Cells.Item($row, 7).Value2
    if ($code -notmatch '^\d{6}x?$' -or -not $name -or $null -eq $kcalValue) { continue }
    $kcal = 0.0
    if (-not [double]::TryParse([string]$kcalValue, [Globalization.NumberStyles]::Any, [Globalization.CultureInfo]::InvariantCulture, [ref]$kcal) -or $kcal -le 0) { continue }
    $protein = 0.0
    [void][double]::TryParse([string]$proteinValue, [Globalization.NumberStyles]::Any, [Globalization.CultureInfo]::InvariantCulture, [ref]$protein)
    $edible = 100.0
    [void][double]::TryParse([string]$edibleValue, [Globalization.NumberStyles]::Any, [Globalization.CultureInfo]::InvariantCulture, [ref]$edible)
    $foods.Add([pscustomobject]@{ code=$code; name=$name; ediblePercent=$edible; kcalPer100g=$kcal; proteinPer100g=$protein })
  }

  if ($foods.Count -eq 0) { throw '没有找到带食物编码和能量值的数据行。' }
  if ((Test-Path -LiteralPath $outputPath) -and -not $Force) {
    $answer = Read-Host '本地食物数据库已存在。是否替换？输入 Y 确认'
    if ($answer -notmatch '^(Y|y)$') { Write-Output '已取消导入，现有数据库未更改。'; exit 0 }
  }
  $json = ConvertTo-Json -InputObject @($foods) -Depth 4
  [System.IO.File]::WriteAllText($outputPath, $json, [System.Text.UTF8Encoding]::new($false))
  Write-Output "导入完成：$($foods.Count) 条食物记录。数据库保存在本机：$outputPath"
}
finally {
  if ($workbook) { $workbook.Close($false) }
  if ($excel) { $excel.Quit() }
}
