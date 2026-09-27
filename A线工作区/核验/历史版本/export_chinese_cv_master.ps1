$ErrorActionPreference = 'Stop'
$root = Join-Path (Split-Path $PSScriptRoot -Parent) '材料'
$stems = @(
    (Join-Path $root '校对稿/周子靖_中文学术简历_v0.3_INTERNAL'),
    (Join-Path $root '对外PDF/周子靖_中文学术简历_Master_v1')
)
foreach ($stem in $stems) {
    if (Test-Path -LiteralPath "$stem.pdf") { throw "Preserve existing PDF: $stem.pdf" }
}
$word = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    foreach ($stem in $stems) {
        $document = $null
        try {
            $document = $word.Documents.Open("$stem.docx", $false, $true)
            $document.Repaginate()
            if ($document.ComputeStatistics(2) -ne 1) { throw "Unexpected page count: $stem" }
            $document.ExportAsFixedFormat("$stem.pdf", 17)
            Write-Output "$stem.pdf (1 page)"
        }
        finally {
            if ($null -ne $document) {
                $document.Close(0)
                [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($document)
            }
        }
    }
}
finally {
    if ($null -ne $word) {
        $word.Quit()
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)
    }
}
