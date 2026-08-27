param(
  [Parameter(Mandatory = $true)][string]$Locale,
  [double]$FetchInterval = 0.35,
  [double]$TranslateInterval = 0.4
)

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

python Tools/fetch_quests.py --locale $Locale --workers 6 --interval $FetchInterval
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python Tools/build_wordlist.py --locale $Locale
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python Tools/translate_google.py --locale $Locale --workers 4 --interval $TranslateInterval
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python Tools/build_dictionary_lua.py --locale $Locale
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "$Locale dictionary complete"
