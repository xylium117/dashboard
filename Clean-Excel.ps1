param(
    [string]$InputFile = ""
)

if ([string]::IsNullOrWhiteSpace($InputFile)) {
    $candidate = Get-ChildItem -File "*Combined*Cost Report*.xlsx" | Where-Object { $_.Name -notlike "*_Cleaned*" } | Select-Object -First 1
    if (-not $candidate) {
        $candidate = Get-ChildItem -File "*Combined*.xlsx" | Where-Object { $_.Name -notlike "*_Cleaned*" } | Select-Object -First 1
    }
    if (-not $candidate) {
        $candidate = Get-ChildItem -File "*Cost Report*.xlsx" | Where-Object { $_.Name -notlike "*_Cleaned*" } | Select-Object -First 1
    }
    if ($candidate) {
        $InputFile = $candidate.FullName
    }
}

if (-not (Test-Path $InputFile)) {
    Write-Host "File not found: $InputFile" -ForegroundColor Red
    exit 1
}

$OutputFile = [System.IO.Path]::GetFileNameWithoutExtension($InputFile) + "_Cleaned.xlsx"
Write-Host "Cleaning: $InputFile -> $OutputFile" -ForegroundColor Cyan

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ([System.Guid]::NewGuid().ToString())
[System.IO.Compression.ZipFile]::ExtractToDirectory((Resolve-Path $InputFile), $tempDir)

$wbXmlPath = Join-Path $tempDir "xl\workbook.xml"
if (Test-Path $wbXmlPath) {
    $content = [System.IO.File]::ReadAllText($wbXmlPath)
    $origSize = $content.Length
    $cleaned = [System.Text.RegularExpressions.Regex]::Replace($content, '<definedNames>.*?</definedNames>', '<definedNames/>', [System.Text.RegularExpressions.RegexOptions]::Singleline)
    [System.IO.File]::WriteAllText($wbXmlPath, $cleaned)
    Write-Host "Reduced workbook.xml from $origSize bytes to $($cleaned.Length) bytes." -ForegroundColor Green
}

if (Test-Path $OutputFile) {
    Remove-Item $OutputFile -Force
}

$outZip = [System.IO.Compression.ZipFile]::Open((Join-Path (Get-Location) $OutputFile), [System.IO.Compression.ZipArchiveMode]::Create)
Get-ChildItem $tempDir -Recurse -File | ForEach-Object {
    $relPath = $_.FullName.Substring($tempDir.Length).TrimStart('\', '/').Replace('\', '/')
    [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($outZip, $_.FullName, $relPath, [System.IO.Compression.CompressionLevel]::Optimal)
}
$outZip.Dispose()
Remove-Item $tempDir -Recurse -Force
Write-Host "Success! Cleaned file created: $OutputFile" -ForegroundColor Green
