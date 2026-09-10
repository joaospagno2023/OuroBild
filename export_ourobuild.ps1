$ErrorActionPreference = "Stop"

# ============================================================
# Projeto : OuroBuild
# Arquivo : export_ourobuild.ps1
# Descrição :
#   Gera um ZIP do projeto OuroBuild excluindo:
#   - diretórios __pycache__
#   - diretórios logs
#   - arquivos *.log
# ============================================================

$ProjectRoot = (Get-Location).Path

$ProjectName = Split-Path $ProjectRoot -Leaf

$ParentDirectory = Split-Path $ProjectRoot -Parent

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

$ZipPath = Join-Path `
    $ParentDirectory `
    "$ProjectName`_$Timestamp.zip"

$TemporaryDirectory = Join-Path `
    $env:TEMP `
    "OuroBuildExport_$Timestamp"


Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host " Exportação do projeto OuroBuild" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Projeto:" -ForegroundColor Yellow
Write-Host "  $ProjectRoot"

Write-Host ""
Write-Host "ZIP:" -ForegroundColor Yellow
Write-Host "  $ZipPath"

Write-Host ""
Write-Host "Criando diretório temporário..." -ForegroundColor Yellow

New-Item `
    -ItemType Directory `
    -Path $TemporaryDirectory `
    -Force | Out-Null


Write-Host ""
Write-Host "Copiando arquivos..." -ForegroundColor Yellow


$ExcludedDirectoryNames = @(
    "__pycache__",
    "logs"
)

$ExcludedFileExtensions = @(
    ".log"
)


$Files = Get-ChildItem `
    -Path $ProjectRoot `
    -Recurse `
    -File `
    -Force


$CopiedFiles = 0
$SkippedFiles = 0


foreach ($File in $Files) {

    $RelativePath = $File.FullName.Substring(
        $ProjectRoot.Length
    ).TrimStart(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    )


    $RelativeParts = $RelativePath -split '[\\/]'


    $IsExcludedDirectory = $false


    foreach ($Part in $RelativeParts) {

        if (
            $ExcludedDirectoryNames `
                -contains $Part
        ) {

            $IsExcludedDirectory = $true

            break
        }
    }


    if ($IsExcludedDirectory) {

        $SkippedFiles++

        continue
    }


    if (
        $ExcludedFileExtensions `
            -contains $File.Extension.ToLowerInvariant()
    ) {

        $SkippedFiles++

        continue
    }


    $DestinationFile = Join-Path `
        $TemporaryDirectory `
        $RelativePath


    $DestinationDirectory = Split-Path `
        $DestinationFile `
        -Parent


    if (
        -not (
            Test-Path `
                -LiteralPath $DestinationDirectory
        )
    ) {

        New-Item `
            -ItemType Directory `
            -Path $DestinationDirectory `
            -Force | Out-Null
    }


    Copy-Item `
        -LiteralPath $File.FullName `
        -Destination $DestinationFile `
        -Force


    $CopiedFiles++
}


Write-Host ""
Write-Host "Arquivos copiados : $CopiedFiles" -ForegroundColor Green
Write-Host "Arquivos ignorados: $SkippedFiles" -ForegroundColor DarkYellow


if (
    Test-Path `
        -LiteralPath $ZipPath
) {

    Write-Host ""
    Write-Host "Removendo ZIP anterior..." -ForegroundColor Yellow

    Remove-Item `
        -LiteralPath $ZipPath `
        -Force
}


Write-Host ""
Write-Host "Compactando projeto..." -ForegroundColor Yellow


Compress-Archive `
    -Path "$TemporaryDirectory\*" `
    -DestinationPath $ZipPath `
    -CompressionLevel Optimal


Write-Host ""
Write-Host "Removendo diretório temporário..." -ForegroundColor Yellow


Remove-Item `
    -LiteralPath $TemporaryDirectory `
    -Recurse `
    -Force


Write-Host ""
Write-Host "==============================================" -ForegroundColor Green
Write-Host " ZIP criado com sucesso!" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green
Write-Host ""

Write-Host "Arquivo:" -ForegroundColor Cyan
Write-Host "  $ZipPath"

Write-Host ""
Write-Host "Tamanho:" -ForegroundColor Cyan

$ZipInfo = Get-Item `
    -LiteralPath $ZipPath

$SizeMB = [math]::Round(
    $ZipInfo.Length / 1MB,
    2
)

Write-Host "  $SizeMB MB"

Write-Host ""