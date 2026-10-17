param([string]$Compiler = '')
$ErrorActionPreference = 'Stop'
$firmwareRoot = $PSScriptRoot
$buildDir = Join-Path $firmwareRoot 'build'
New-Item -ItemType Directory -Force -Path $buildDir | Out-Null
if (-not $Compiler) {
    $foundCompiler = Get-Command g++.exe,clang++.exe -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($foundCompiler) { $Compiler = $foundCompiler.Source }
    else {
        $localCompiler = Join-Path $env:USERPROFILE 'Documents\mingw64\bin\g++.exe'
        if (Test-Path -LiteralPath $localCompiler) { $Compiler = $localCompiler }
        else { throw 'Provide -Compiler path to an installed C++17 g++ or clang++ compiler.' }
    }
}
& $Compiler --version
if ($LASTEXITCODE -ne 0) { throw 'Compiler version check failed.' }
$flags = @('-std=c++17','-Wall','-Wextra','-Werror','-pedantic','-static-libgcc','-static-libstdc++','-I',(Join-Path $firmwareRoot 'src'))
$journal = Join-Path $firmwareRoot 'src\journal.cpp'
$controller = Join-Path $firmwareRoot 'src\controller.cpp'
foreach ($target in @('journal_tests','controller_tests','host_sim')) {
    $source = if ($target -eq 'host_sim') { Join-Path $firmwareRoot 'host\sim.cpp' } else { Join-Path $firmwareRoot "tests\$target.cpp" }
    $sources = @($journal)
    if ($target -ne 'journal_tests') { $sources += $controller }
    $binary = Join-Path $buildDir "$target.exe"
    & $Compiler @flags @sources $source -o $binary
    if ($LASTEXITCODE -ne 0) { throw "Compilation failed: $target" }
    if ($target -eq 'host_sim') {
        & $binary (Join-Path $buildDir 'synthetic-transport.csv')
    } else { & $binary }
    if ($LASTEXITCODE -ne 0) { throw "Execution failed: $target" }
}
Write-Output 'Host checks passed; CSV is TEST_ONLY synthetic. No hardware/film validation.'
