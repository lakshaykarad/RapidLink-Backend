<div align="center">

<h1>🗺️ RapidLink Backend</h1>

<p>
  <strong>High-performance routing & navigation backend for the RapidLink Android application.</strong><br/>
  Powered by FastAPI, OSRM, Docker, and OpenStreetMap data.
</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Docker-Required-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker"/>
  <img src="https://img.shields.io/badge/OSRM-Latest-FF6B35?style=flat-square" alt="OSRM"/>
  <img src="https://img.shields.io/badge/OpenStreetMap-Data-7EBC6F?style=flat-square&logo=openstreetmap&logoColor=white" alt="OSM"/>
  <img src="https://img.shields.io/badge/License-Apache%202.0-blue?style=flat-square" alt="License"/>
</p>

<p>
  <a href="#-overview">Overview</a> •
  <a href="#-prerequisites">Prerequisites</a> •
  <a href="#-getting-started">Getting Started</a> •
  <a href="#-connecting-the-android-app">Android App</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-important-notes">Notes</a> •
  <a href="#-license">License</a>
</p>

</div>

---

## 📖 Overview

The **RapidLink Backend** is the server-side infrastructure for the [RapidLink Android application](https://github.com/your-org/rapidlink-android) — a Kotlin-based map and navigation app. This backend handles all heavy lifting for:

- ⏱️ **ETA calculations** based on real road network data
- 🚦 **Traffic data processing**
- 🌐 **Map-related REST API services** via FastAPI

The stack runs entirely **locally**, giving you full control over your data.

---

## ⚙️ Prerequisites

Ensure the following are installed and running on your system before proceeding:

| Dependency | Version | Purpose |
|---|---|---|
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | Latest | Run OSRM routing engine |
| [Python](https://www.python.org/downloads/) | 3.x | Run the FastAPI server |
| [pip](https://pip.pypa.io/en/stable/installation/) | Latest | Install Python dependencies |

> **Note:** Docker must be **actively running** (not just installed) before you execute any routing commands.

---

## 🚀 Getting Started

Follow the four steps below to go from zero to a fully running backend.

### Step 1 — Download Map Data

OSRM needs OpenStreetMap (`.pbf`) data to build a routing graph for your target region.

1. Visit **[Geofabrik Downloads](https://download.geofabrik.de)** and download the `.osm.pbf` file for your desired region (e.g., a city, state, or country).
2. Place the downloaded `.pbf` file in the **root directory** of this project.
3. Rename the file to exactly:

```
OSRM_ROUTING_ETA_DATA_FILE.pbf
```

> ⚠️ The filename must match **exactly** — scripts and Docker commands reference this name directly.

---

### Step 2 — Build the Routing Graph

Before OSRM can calculate routes, it must process the raw `.pbf` data into a traversable graph. This is a one-time step per map file.

Run the build script:

```bat
build_map.bat
```

This script performs three operations in sequence:

1. **Extract** — parses road network data from the `.pbf` file
2. **Partition** — segments the graph for the MLD (Multi-Level Dijkstra) algorithm
3. **Customize** — generates the final `.osrm` routing files

---

### Step 3 — Start the OSRM Routing Engine

Once the map graph is built, launch the OSRM backend server.

**On Windows (recommended):**

```bat
start_osrm.bat
```

**Manual / Cross-platform Docker command:**

```bash
docker run -p 5000:5000 -v "%cd%:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/OSRM_ROUTING_ETA_DATA_FILE.osrm
```

> 🟢 The OSRM routing engine will be live at: **`http://127.0.0.1:5000`**

---

### Step 4 — Start the FastAPI Backend

Open a **new terminal window** (keep the OSRM terminal running) and start the Python API server:

```bash
python -m uvicorn server:app --reload --port 8000
```

> 🟢 The FastAPI backend will be live at: **`http://127.0.0.1:8000`**  
> 📄 Interactive API docs available at: **`http://127.0.0.1:8000/docs`**

---

## 📱 Connecting the Android App

Both backend services must be running **simultaneously** before launching the RapidLink Android app.

```
┌─────────────────────────────────────────────────┐
│              RapidLink Android App               │
└───────────────┬─────────────────┬───────────────┘
                │                 │
                ▼                 ▼
   ┌────────────────────┐  ┌─────────────────────┐
   │   FastAPI Backend  │  │   OSRM Backend      │
   │   Port :8000       │  │   Port :5000        │
   │   (API Services)   │  │   (Routing Engine)  │
   └────────────────────┘  └─────────────────────┘
```

| Service | URL | Status Check |
|---|---|---|
| FastAPI Backend | `http://127.0.0.1:8000` | Visit `/docs` for Swagger UI |
| OSRM Engine | `http://127.0.0.1:5000` | Should return OSRM status JSON |

Launch the Android app **only after** both services confirm they are live.

---

## 🏗️ Architecture

```
rapidlink-backend/
├── server.py                          # FastAPI application entrypoint
├── OSRM_ROUTING_ETA_DATA_FILE.pbf     # Your downloaded OSM map data (gitignored)
├── OSRM_ROUTING_ETA_DATA_FILE.osrm    # Built routing graph (generated)
├── build_map.bat                      # Script: builds OSRM routing graph
├── start_osrm.bat                     # Script: starts OSRM Docker container
```

---

## ⚠️ Important Notes

**Docker must stay running**  
The Docker daemon must remain active for the entire duration of your routing session. Stopping Docker will kill the OSRM server.

**RAM requirements scale with map size**  
Processing and serving large `.pbf` files (e.g., entire countries or continents) requires significant RAM. For reference:

| Region Size | Approx. RAM Required |
|---|---|
| City / Province | ~512 MB – 2 GB |
| Country (small) | ~2 GB – 8 GB |
| Country (large) | 8 GB+ |
| Continent | 16 GB+ |

**Re-run Step 2 only when changing map files**  
If you swap out the `.pbf` file for a new region, you must re-run `build_map.bat` to rebuild the routing graph.

**OSM file compatibility**  
This backend works with any standard `.osm.pbf` file from OpenStreetMap — not just Geofabrik. Other sources like [BBBike](https://extract.bbbike.org/) or the [official OSM planet](https://planet.openstreetmap.org/) also work.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'feat: add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

Please ensure your code follows the existing style and includes relevant documentation updates.

---

## 📄 License

This project is licensed under the **Apache License 2.0**.  
See the [LICENSE](LICENSE) file for full details.

---

<div align="center">

Made with ❤️ for the RapidLink project

</div>
