from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import json, os, csv
from pydantic import BaseModel
from typing import List

app = FastAPI()

script_dir = os.path.dirname(os.path.abspath(__file__))
DEVICES_FILE = os.path.join(script_dir, "devices.json")
CSV_FILE = os.path.join(script_dir, "traffic.csv")


class RouteRequest(BaseModel):
    route_id: str
    distance_m: float
    roads: List[str] # List of road names this route goes through

def load_devices():
    if os.path.exists(DEVICES_FILE):
        with open(DEVICES_FILE) as f:
            return json.load(f)
    return {}

def save_devices(devices):
    with open(DEVICES_FILE, "w") as f:
        json.dump(devices, f, indent = 4)  # dump -> save as json format, indent use as 4 space  

def generate_csv(devices):
    with open(CSV_FILE, "w",newline= "") as f:
        writer = csv.writer(f)
        writer.writerow(["device_id", "lat", "lng", "speed_kmh", "road_label"])
        for d_id, d in devices.items():
            writer.writerow([d_id, d["lat"], d["lng"], d["speed"], d["road"]])

# ---------- endpoints ----------
@app.get("/ping")
def ping():
    return {"status": "server is alive"}

@app.get("/")
def home():
    return FileResponse(os.path.join(script_dir, "static/index.html"))

@app.get("/devices")
def get_devices():
    return load_devices()

@app.post("/device/add")
def add_device(device_id: str, lat: float, lng: float,
               speed: float, road: str = "unknown"):
    devices = load_devices()
    devices[device_id] = {"lat": lat, "lng": lng, "speed": speed, "road": road}
    save_devices(devices)
    generate_csv(devices)
    return {"status": "added", "total_devices": len(devices)}

@app.delete("/device/remove/{device_id}")
def remove_device(device_id: str):
    devices = load_devices()
    if device_id in devices:
        del devices[device_id]
    save_devices(devices)
    generate_csv(devices)
    return {"status": "removed", "total_devices": len(devices)}

@app.delete("/devices/clear")
def clear_all():
    save_devices({})
    generate_csv({})
    return {"status": "cleared"}

@app.get("/traffic/summary")
def traffic_summary():
    devices = load_devices()
    road_groups = {} # We use a dictionary to group speeds by road name

    for d in devices.values():
        road_name = d["road"]
        speed = d["speed"] 
        if road_name not in road_groups:
            road_groups[road_name] = []
        
        road_groups[road_name].append(speed)
            
    summary = {}
    for road_name, speeds in road_groups.items():
        if not speeds:
            continue
            
        avg = sum(speeds) / len(speeds)
        
        if avg < 15:
            status = "🔴 Heavy"
        elif avg < 30:
            status = "🟡 Moderate"
        else:
            status = "🟢 Clear"
            
        summary[road_name] = {
            "avg_speed": round(avg, 1),
            "status": status,
            "devices": len(speeds)
        }
    return summary
 
@app.get("/eta")
def get_eta(distance_m: float, road: str = "unknown"):
    
    base_speed_kmh = 40.0  
    multiplier = 1.0
    
    current_summary = traffic_summary()   
    
    if road in current_summary:
        avg = current_summary[road].get("avg_speed", 0)
        if avg > 0:
            base_speed_kmh = avg
        else:
            base_speed_kmh = 5.0 
    else:
        multiplier = 1.1 

    distance_km = distance_m / 1000.0
    eta_hours = (distance_km / max(base_speed_kmh, 1.0)) * multiplier
    
    return {
        "road": road,
        "distance_m": distance_m,
        "speed_used_kmh": base_speed_kmh,
        "eta_minutes": round(eta_hours * 60, 1),
        "eta_seconds": int(eta_hours * 3600)
    }

@app.post("/traffic/best_route")
def get_best_route(routes: List[RouteRequest]):
   
    if not routes:
        return {"error": "No routes provided"}

    summary = traffic_summary()
    results = []
    
    for route in routes:
        if not route.roads:
            # If no road found apply simple ETA 
            total_eta_hours = (route.distance_m / 1000.0) / 40.0
        else:
            # divide total distance equally among roads -> if distance is 12 KM then 2 segments is divide as 6-6
            # segments stands for number of routes. 
            num_segments = len(route.roads) # Length of routes. 
            segment_dist_km = (route.distance_m / 1000.0) / num_segments
                
            """route.roads = ["highway", "city_road"]
            segment_dist_km = 5

            summary = {
            "highway": {"avg_speed": 50},
            "city_road": {"avg_speed": 25}
            }

            total_eta_hours = 0
            """    
            total_eta_hours = 0
            for road in route.roads:  
                # Use .get() to avoid potential KeyErrors
                road_data = summary.get(road, {})
                avg_speed = road_data.get("avg_speed", 40.0)
                
                # Prevent division by zero if speed is 0
                speed = avg_speed if avg_speed > 0 else 5.0 
                total_eta_hours += segment_dist_km / speed

        results.append({
            "route_id": route.route_id,
            "total_eta_minutes": round(total_eta_hours * 60, 1),
            "distance_m" : route.distance_m
        })

    results.sort(key=lambda x: x["total_eta_minutes"])
    
    return {
        "best_route_id": results[0]["route_id"],
        "fastest_time_minutes": results[0]["total_eta_minutes"],
        "all_routes": results
    }

app.mount("/static", StaticFiles(directory=os.path.join(script_dir, "static")), name="static")

# cd traffic_dashboard
# python -m uvicorn server:app --reload --port 8080 
# python -m uvicorn server:app --host 0.0.0.0 --port 8000

# Link -> http://127.0.0.1:8000