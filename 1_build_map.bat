@echo off
title RapidLink Map Builder
echo =======================================================
echo     Building the Map Graph (This takes a few minutes!)
echo =======================================================
echo.

echo [1/3] Extracting roads from the raw .pbf file...
docker run -v "%cd%:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/OSRM_ROUTING_ETA_DATA_FILE.pbf

echo.
echo [2/3] Partitioning the map grid...
docker run -v "%cd%:/data" osrm/osrm-backend osrm-partition /data/OSRM_ROUTING_ETA_DATA_FILE.osrm

echo.
echo [3/3] Customizing map with base speeds...
docker run -v "%cd%:/data" osrm/osrm-backend osrm-customize /data/OSRM_ROUTING_ETA_DATA_FILE.osrm

echo.
echo Map build complete! You can now start the server.
pause