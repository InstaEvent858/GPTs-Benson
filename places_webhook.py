import os
import requests
from fastapi import FastAPI, HTTPException

app = FastAPI()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PLACES_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
PLACE_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
PHOTO_BASE_URL = "https://maps.googleapis.com/maps/api/place/photo"

@app.get("/")
def root():
    return {"status": "Hey Benson webhook is alive"}

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
        "website": result.get("website", None)
    }

    if "photos" in result and result["photos"]:
        photo_ref = result["photos"][0]["photo_reference"]
        image_url = f"{PHOTO_BASE_URL}?maxwidth=800&photoreference={photo_ref}&key={GOOGLE_API_KEY}"
        venue_data["image_url"] = image_url
    else:
        venue_data["image_url"] = None

    return venue_data
