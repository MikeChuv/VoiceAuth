
$scriptDirectory = $PSScriptRoot
$repoRoot = "$scriptDirectory\..\.."

$uiDir = "$repoRoot\src\ui"

$uiFiles = Get-ChildItem -Path $uiDir -Filter "*.ui"


foreach ($uiFile in $uiFiles) {
    $pyFile = Join-Path $uiFile.DirectoryName ("ui_" + $uiFile.BaseName + ".py")
    Write-Host "Converting $($uiFile.Name) to $([System.IO.Path]::GetFileName($pyFile))..."

    pyuic5 $uiFile.FullName -o $pyFile

    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Failed to convert: $($uiFile.FullName)"
    }
}