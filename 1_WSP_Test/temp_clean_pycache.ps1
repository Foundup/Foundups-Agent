Write-Host "Attempting to remove __pycache__ directories from .\modules..."
Get-ChildItem -Path .\modules -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "__pycache__ removal attempt complete."
exit 0 