$ErrorActionPreference = 'Stop'
$cvRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$cvStem = Join-Path $cvRoot '对外PDF/周子靖_中文学术简历_Master_v1.4'
if (Test-Path -LiteralPath "$cvStem.pdf") { throw 'PDF already exists; do not overwrite frozen versions.' }
$word = $null
$doc = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $doc = $word.Documents.Open("$cvStem.docx", $false, $true)
    $doc.Repaginate()
    Write-Output "Word pages: $($doc.ComputeStatistics(2))"
    $doc.ExportAsFixedFormat("$cvStem.pdf", 17)
} finally {
    if ($null -ne $doc) { $doc.Close(0); [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($doc) }
    if ($null -ne $word) { $word.Quit(); [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($word) }
}
