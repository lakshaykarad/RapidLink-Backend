@echo off
title RapidLink Server
echo =======================================================
echo     Booting RapidLink Server on Port 5000...
echo =======================================================
echo.

docker run -p 5000:5000 -v "%cd%:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/OSRM_ROUTING_ETA_DATA_FILE.osrm

pause