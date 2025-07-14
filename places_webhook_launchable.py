import os
import requests
import uvicorn
from fastapi import FastAPI, HTTPException, Header

app = FastAPI()

API_KEY = os.getenv("API_KEY")  # Your custom key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PLACES_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
PLACE_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
PHOTO_BASE_URL = "https://maps.googleapis.com/maps/api/place/photo"
STATIC_MAP_URL = "https://maps.googleapis.com/maps/api/staticmap"

def verify_api_key(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    key = authorization.split(" ")[1]
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")

@app.get("/")
def root():
    return {"status": "Hey Benson webhook v3.4 (Bearer Auth) is alive ✅"}

@app.get("/get_venue_info")
def get_venue_info(query: str, city: str, authorization: str = Header(...)):
    verify_api_key(authorization)
    full_query = f"{query}, {city}"
    search_params = {"query": full_query, "key": GOOGLE_API_KEY}

    search_resp = requests.get(PLACES_SEARCH_URL, params=search_params)
    search_json = search_resp.json()

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

    details_resp = requests.get(PLACE_DETAILS_URL, params=details_params)
    details_json = details_resp.json()

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
def get_multi_venue_map(venues: str, city: str, authorization: str = Header(...)):
    verify_api_key(authorization)

    venue_list = [
        {"lat": v.split("|")[0], "lng": v.split("|")[1], "label": v.split("|")[2]}
        for v in venues.split(",")
    ]

    marker_params = "&".join([
        f"markers=color:red|label:{v['label']}|{v['lat']},{v['lng']}"
        for v in venue_list
    ])

    static_map_url = (
        f"{STATIC_MAP_URL}?center={city.replace(' ', '+')}&zoom=12&size=600x400&"
        f"{marker_params}&key={GOOGLE_API_KEY}"
    )

    waypoints = "|".join([f"{v['lat']},{v['lng']}" for v in venue_list[1:]])
    google_maps_all_link = (
        f"https://www.google.com/maps/dir/?api=1"
        f"&destination={venue_list[0]['lat']},{venue_list[0]['lng']}"
        f"&waypoints={waypoints}"
    )

    waypoints_embed = "%7C".join([f"{v['lat']},{v['lng']}" for v in venue_list[1:]])
    iframe_embed_url = (
        f"https://www.google.com/maps/embed/v1/directions?key={GOOGLE_API_KEY}"
        f"&origin={venue_list[0]['lat']},{venue_list[0]['lng']}"
        f"&destination={venue_list[0]['lat']},{venue_list[0]['lng']}"
        f"&waypoints={waypoints_embed}"
    )

    return {
        "static_map_url": static_map_url,
        "google_maps_all_link": google_maps_all_link,
        "iframe_embed_url": iframe_embed_url
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
