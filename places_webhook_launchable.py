from fastapi import FastAPI, Query
from typing import List

app = FastAPI()

# ✅ Public route, no authentication required
@app.get("/get_multi_venue_map")
async def get_multi_venue_map(city: str, venues: List[str] = Query(...)):
    return {
        "city": city,
        "venues": [
            {
                "id": v,
                "name": f"Venue {v}",
                "address": "123 Main St",
                "image_url": "https://example.com/venue.jpg"
            }
            for v in venues
        ]
    }

# ✅ Public route, no authentication required
@app.get("/get_venue_info")
async def get_venue_info(venue_id: str):
    return {
        "name": f"Venue {venue_id}",
        "address": "123 Main St",
        "image_url": "https://example.com/venue.jpg"
    }
