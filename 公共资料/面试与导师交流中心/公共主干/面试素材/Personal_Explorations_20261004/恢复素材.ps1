$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$packed = Join-Path $root "packed"
$zip = Join-Path $root "Personal_Explorations_素材_workcopy600_20261004.zip"
$decoded = Join-Path $root "decoded"
$expected = "70f1a46f4b91207f4eb81f301624eacc7c6b7cd1ada66aa7f44dd068d793169b"

if (-not (Test-Path $packed)) {
    throw "未找到 packed 目录：$packed"
}

$parts = Get-ChildItem $packed -Filter 'part*.b64' | Sort-Object Name
if ($parts.Count -ne 4) {
    throw "预期 4 个 Base64 分片，实际找到 $($parts.Count) 个。"
}

$b64 = ($parts | ForEach-Object { (Get-Content $_.FullName -Raw).Trim() }) -join ''
[IO.File]::WriteAllBytes($zip, [Convert]::FromBase64String($b64))

$hash = (Get-FileHash $zip -Algorithm SHA256).Hash.ToLower()
if ($hash -ne $expected) {
    throw "SHA256 mismatch: $hash`nexpected: $expected"
}

if (Test-Path $decoded) {
    Remove-Item $decoded -Recurse -Force
}
Expand-Archive -Path $zip -DestinationPath $decoded -Force

Write-Host "素材恢复完成：$decoded"
Write-Host "SHA256 校验通过：$hash"
Get-ChildItem (Join-Path $decoded 'images') | Select-Object Name, Length
