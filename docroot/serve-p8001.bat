SET mypath=%~dp0
cd %mypath%
python -m http.server 8001
