import os
import requests
from fastapi import FastAPI, HTTPException

app = FastAPI()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PLACES_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
PLACE_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
PHOTO_BASE_URL = "https://maps.googleapis.com/maps/api/place/photo"

@app.get("/get_venue_info")
def get_venue_info(query: str, city: str):
    full_query = f"{query}, {city}"
    search_params = {
        "query": full_query,
        "key": GOOGLE_API_KEY
    }
    search_resp = requests.get(PLACES_SEARCH_URL, params=search_params).json()

    if not search_resp.get("results"):
        raise HTTPException(status_code=404, detail="No place found")

    place_id = search_resp["results"][0]["place_id"]
    details_params = {
        "place_id": place_id,
        "fields": "name,formatted_address,website,photos",
        "key": GOOGLE_API_KEY
    }
    details_resp = requests.get(PLACE_DETAILS_URL, params=details_params).json()

    if not details_resp.get("result"):
        raise HTTPException(status_code=404, detail="No details found")

    result = details_resp["result"]
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
