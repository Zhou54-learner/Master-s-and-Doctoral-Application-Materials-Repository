$ErrorActionPreference = 'Stop'
$cvRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$candidate = Join-Path $cvRoot '校对稿/周子靖_中文学术简历_Master_v1.3_CANDIDATE'
$word = $null
$document = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $document = $word.Documents.Open("$candidate.docx", $false, $true)
    $document.Repaginate()
    Write-Output "Word page count: $($document.ComputeStatistics(2))"
    $document.ExportAsFixedFormat("$candidate.pdf", 17)
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
