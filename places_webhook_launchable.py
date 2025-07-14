import os
import requests
import uvicorn
from fastapi import FastAPI, HTTPException

app = FastAPI()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PLACES_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
PLACE_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
PHOTO_BASE_URL = "https://maps.googleapis.com/maps/api/place/photo"
STATIC_MAP_URL = "https://maps.googleapis.com/maps/api/staticmap"

@app.get("/")
def root():
    return {"status": "Hey Benson webhook v3.3 is alive ✅"}

@app.get("/get_venue_info")
def get_venue_info(query: str, city: str):
    full_query = f"{query}, {city}"
    search_params = {"query": full_query, "key": GOOGLE_API_KEY}

    try:
        search_resp = requests.get(PLACES_SEARCH_URL, params=search_params)
        search_json = search_resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Places Search error: {e}")

    if not search_json.get("results"):
        raise HTTPException(status_code=404, detail="No place found")

    first_result = search_json["results"][0]
    place_id = first_result["place_id"]
    lat = first_result["geometry"]["location"]["lat"]
    lng = first_result["geometry"]["location"]["lng"]

    details_params = {
        "place_id": place_id,
        "fields": "name,formatted_address,website,photos",
        "key": GOOGLE_API_KEY
    }

    try:
        details_resp = requests.get(PLACE_DETAILS_URL, params=details_params)
        details_json = details_resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Place Details error: {e}")

    if not details_json.get("result"):
        raise HTTPException(status_code=404, detail="No details found")

    result = details_json["result"]
    venue_data = {
        "name": result.get("name"),
        "address": result.get("formatted_address"),
        "website": result.get("website"),
        "lat": lat,
        "lng": lng,
        "city": city
    }

    if "photos" in result and result["photos"]:
        photo_ref = result["photos"][0]["photo_reference"]
        venue_data["image_url"] = f"{PHOTO_BASE_URL}?maxwidth=800&photoreference={photo_ref}&key={GOOGLE_API_KEY}"
    else:
        venue_data["image_url"] = None

    return venue_data

@app.get("/get_multi_venue_map")
def get_multi_venue_map(venues: str, city: str):
    """
    venues: comma-separated list of 'lat|lng|label'
    e.g., "39.7392|-104.9903|A,39.7502|-104.9999|B"
    """
    marker_params = "&".join(
        [f"markers=color:red|label:{v.split('|')[2]}|{v.split('|')[0]},{v.split('|')[1]}"
         for v in venues.split(",")]
    )
    static_map = f"{STATIC_MAP_URL}?center={city}&zoom=13&size=600x400&{marker_params}&key={GOOGLE_API_KEY}"
    return {"static_map_url": static_map}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
