:start
cls
REM - Photos to the webserver
T:\PROJECTS\AKR\FMSS\PHOTOS\PROCESSING\cmd\robocopy.exe T:\PROJECTS\AKR\FMSS\PHOTOS\WEB \\akrgis.nps.gov\inetApps\fmss\photos\web /R:5 /W:5 /Z /MIR /LOG:T:\PROJECTS\AKR\FMSS\PHOTOS\PROCESSING\cmd\photoweblogfile.txt 
T:\PROJECTS\AKR\FMSS\PHOTOS\PROCESSING\cmd\robocopy.exe T:\PROJECTS\AKR\FMSS\PHOTOS\THUMB \\akrgis.nps.gov\inetApps\fmss\photos\thumb /R:5 /W:5 /Z /MIR /LOG:T:\PROJECTS\AKR\FMSS\PHOTOS\PROCESSING\cmd\photothumblogfile.txt
cp "T:\PROJECTS\AKR\FMSS\PHOTOS\PROCESSING\website scripts\buildings.csv" \\akrgis.nps.gov\inetApps\buildings\data\buildings.csv
cp "T:\PROJECTS\AKR\FMSS\PHOTOS\PROCESSING\website scripts\photos.json" \\akrgis.nps.gov\inetApps\fmss\photos.json
:EOF
