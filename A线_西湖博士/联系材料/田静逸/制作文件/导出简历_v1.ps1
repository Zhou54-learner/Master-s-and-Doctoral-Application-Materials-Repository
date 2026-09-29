$ErrorActionPreference = 'Stop'
$packageRoot = Split-Path $PSScriptRoot -Parent
$candidate = Join-Path $packageRoot '当前材料/周子靖_中文学术简历_田静逸版_v1_CANDIDATE'
$pdfPath = Join-Path $packageRoot '当前材料/首封附件_待终读/周子靖_学术简历.pdf'
if (Test-Path -LiteralPath $pdfPath) { throw 'PDF already exists; create a new version instead.' }
$word = $null
$document = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $document = $word.Documents.Open("$candidate.docx", $false, $true)
    $document.Repaginate()
    Write-Output "Word page count: $($document.ComputeStatistics(2))"
    $document.ExportAsFixedFormat($pdfPath, 17)
} finally {
    if ($null -ne $document) {
        $document.Close(0)
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($document)
    }
    if ($null -ne $word) {
        $word.Quit()
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)
    }
}
