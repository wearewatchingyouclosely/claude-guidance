# Builds the portable MyApp.exe into this folder (Release). Needs the .NET SDK (6 or later) to build;
# the exe itself needs only .NET Framework 4.8, which every Windows 10/11 has.
# Close a running MyApp.exe first: the copy fails (MSB3021) while it's open.
dotnet build "$PSScriptRoot\src\MyApp\MyApp.csproj" -c Release -nologo -v q
if ($LASTEXITCODE -eq 0) { Get-Item "$PSScriptRoot\MyApp.exe" | Select-Object Name, Length, LastWriteTime }
