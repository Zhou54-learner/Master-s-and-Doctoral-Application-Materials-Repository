$ErrorActionPreference = 'Stop'
$packRoot = Split-Path $PSScriptRoot -Parent
$docPath = Join-Path $packRoot '当前材料/周子靖_中文学术简历_田静逸版_v2_CANDIDATE.docx'
$pdfPath = Join-Path $packRoot '当前材料/首封附件_待审阅/周子靖_学术简历.pdf'
if (Test-Path -LiteralPath $pdfPath) { throw 'Refuse to overwrite an existing PDF.' }
$word = $null
$doc = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $doc = $word.Documents.Open($docPath, $false, $true)
    $doc.Repaginate()
    Write-Output "Word pages: $($doc.ComputeStatistics(2))"
    $doc.ExportAsFixedFormat($pdfPath, 17)
} finally {
    if ($null -ne $doc) { $doc.Close(0); [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($doc) }
    if ($null -ne $word) { $word.Quit(); [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($word) }
}
