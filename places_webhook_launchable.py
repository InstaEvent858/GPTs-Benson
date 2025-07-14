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
    return {"status": "Hey Benson webhook v3.1 is alive ✅"}

@app.get("/healthcheck/env")
def check_env_key():
    if GOOGLE_API_KEY:
        return {"env_status": "GOOGLE_API_KEY is set ✅"}
    else:
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY is NOT set ❌")

@app.get("/get_venue_info")
def get_venue_info(query: str, city: str):
    full_query = f"{query}, {city}"
    search_params = {
        "query": full_query,
        "key": GOOGLE_API_KEY
    }

    try:
        search_resp = requests.get(PLACES_SEARCH_URL, params=search_params)
        search_json = search_resp.json()
    except Exception as e:
        print("Error fetching place search:", e)
        print("Raw response:", search_resp.text)
        raise HTTPException(status_code=500, detail="Failed to fetch or parse Places Search response")

    if not search_json.get("results"):
        raise HTTPException(status_code=404, detail="No place found")

    place_id = search_json["results"][0]["place_id"]
    details_params = {
        "place_id": place_id,
        "fields": "name,formatted_address,website,photos",
        "key": GOOGLE_API_KEY
    }

    try:
        details_resp = requests.get(PLACE_DETAILS_URL, params=details_params)
        details_json = details_resp.json()
    except Exception as e:
        print("Error fetching place details:", e)
        print("Raw response:", details_resp.text)
        raise HTTPException(status_code=500, detail="Failed to fetch or parse Place Details")

    if not details_json.get("result"):
        raise HTTPException(status_code=404, detail="No details found")

    result = details_json["result"]
    venue_data = {
        "name": result.get("name"),
        "address": result.get("formatted_address"),
        "website": result.get("website", None),
        "city": city,
        "area_map": f"https://www.google.com/maps/search/?api=1&query={city.replace(' ', '+')}",
        "static_map_image": f"{STATIC_MAP_URL}?center={city.replace(' ', '+')}&zoom=13&size=600x400&key={GOOGLE_API_KEY}"
    }

    if "photos" in result and result["photos"]:
        photo_ref = result["photos"][0]["photo_reference"]
        image_url = f"{PHOTO_BASE_URL}?maxwidth=800&photoreference={photo_ref}&key={GOOGLE_API_KEY}"
        venue_data["image_url"] = image_url
    else:
        venue_data["image_url"] = None

    return venue_data

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Launching Benson webhook v3.1 on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
