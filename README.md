 Create a virtual environment

**python -m venv .venv**

Step 4: Activate the environment

For Windows PowerShell:

.**\.venv\Scripts\Activate.ps1**

If PowerShell blocks activation, run the environment's Python executable directly instead:
**.\.venv\Scripts\python.exe --version**

**Install dependencies**

With the virtual environment activated, execute:

**python -m pip install streamlit osmnx scikit-learn folium streamlit-folium matplotlib**
 Download the Road Network

The project uses OSMnx to obtain real-world road network data from OpenStreetMap.

Open **download_roads.py** and configure the download radius.

For example:

G = ox.graph.graph_from_point(
    (12.9165, 79.1325),
    dist=10000,
    network_type="drive",
    simplify=True
)

Here:

Latitude: 12.9165

Longitude: 79.1325

Download radius: 10000 metres

Network type: drive

Run:

python download_roads.py

The script saves the road network to:

**data/vellore_roads.graphml**

The downloaded network must cover both the origin and destination selected by the user.

Downloading a larger area may take more time and memory.

 Running the Website

After installing the dependencies and downloading the road network, start the Streamlit application:

**python -m streamlit run app.py**

The terminal will display a local URL, normally:

http://localhost:8501

Open this address in a web browser.**
