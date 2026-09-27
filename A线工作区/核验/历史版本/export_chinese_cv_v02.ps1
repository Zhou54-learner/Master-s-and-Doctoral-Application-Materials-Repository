param([switch]$RefreshInternal)
$ErrorActionPreference = 'Stop'
$materialRoot = Join-Path (Split-Path $PSScriptRoot -Parent) '材料'
$stem = '周子靖_中文学术简历_v0.2_INTERNAL'
$docx = Join-Path $materialRoot "校对稿/$stem.docx"
$pdf = Join-Path $materialRoot "校对稿/$stem.pdf"
if ((Test-Path -LiteralPath $pdf) -and -not $RefreshInternal) {
    throw "Preserve existing version: $pdf"
}
$word = $null
$document = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $document = $word.Documents.Open($docx, $false, $true)
    $document.Repaginate()
    Write-Output "Word pages: $($document.ComputeStatistics(2))"
    $document.ExportAsFixedFormat($pdf, 17)
    Write-Output $pdf
}
finally {
    if ($null -ne $document) {
        $document.Close(0)
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($document)
    }
    if ($null -ne $word) {
        $word.Quit()
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)
    }
}
