param([switch]$RefreshCandidate)
$ErrorActionPreference = 'Stop'
$root = Join-Path (Split-Path $PSScriptRoot -Parent) '材料/校对稿'
$stems = @('周子靖_中文学术简历_v0.5_INTERNAL', '周子靖_中文学术简历_Master_v1.2_CANDIDATE')
foreach ($stem in $stems) {
    if ((Test-Path -LiteralPath (Join-Path $root "$stem.pdf")) -and -not $RefreshCandidate) {
        throw "Preserve existing candidate: $stem"
    }
}
$word = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    foreach ($stem in $stems) {
        $document = $null
        try {
            $document = $word.Documents.Open((Join-Path $root "$stem.docx"), $false, $true)
            $document.Repaginate()
            Write-Output "$stem : $($document.ComputeStatistics(2)) page(s)"
            $document.ExportAsFixedFormat((Join-Path $root "$stem.pdf"), 17)
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
