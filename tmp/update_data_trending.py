import json
import os

data_path = 'data.json'
with open(data_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

new_cities = {
    "manali": {
        "title": "Manali",
        "state": "Himachal Pradesh",
        "lat": 32.2396,
        "lng": 77.1887,
        "description": "Popular hill station known for snow, mountains, and adventure activities.",
        "img": "/assets/trending/manali.jpg",
        "attractions": [
            {"name": "Solang Valley", "lat": 32.3166, "lng": 77.1558, "img": "/assets/trending_attractions/solang_valley.jpg"},
            {"name": "Rohtang Pass", "lat": 32.3716, "lng": 77.2464, "img": "/assets/trending_attractions/rohtang_pass.jpg"},
            {"name": "Hadimba Temple", "lat": 32.2483, "lng": 77.1747, "img": "/assets/trending_attractions/hadimba_temple.jpg"}
        ]
    },
    "munnar": {
        "title": "Munnar",
        "state": "Kerala",
        "lat": 10.0889,
        "lng": 77.0595,
        "description": "Scenic hill station famous for tea plantations and cool climate.",
        "img": "/assets/trending/munnar.jpg",
        "attractions": [
            {"name": "Tea Gardens", "lat": 10.0852, "lng": 77.0608, "img": "/assets/trending_attractions/tea_gardens.jpg"},
            {"name": "Eravikulam National Park", "lat": 10.1500, "lng": 77.0500, "img": "/assets/trending_attractions/eravikulam_park.jpg"},
            {"name": "Mattupetty Dam", "lat": 10.1065, "lng": 77.1235, "img": "/assets/trending_attractions/mattupetty_dam.jpg"}
        ]
    },
    "coorg": {
        "title": "Coorg",
        "state": "Karnataka",
        "lat": 12.3375,
        "lng": 75.8069,
        "description": "Beautiful coffee region with lush greenery and waterfalls.",
        "img": "/assets/trending/coorg.jpg",
        "attractions": [
            {"name": "Abbey Falls", "lat": 12.4554, "lng": 75.7208, "img": "/assets/trending_attractions/abbey_falls.jpg"},
            {"name": "Raja's Seat", "lat": 12.4172, "lng": 75.7378, "img": "/assets/trending_attractions/rajas_seat.jpg"},
            {"name": "Dubare Elephant Camp", "lat": 12.3686, "lng": 75.9056, "img": "/assets/trending_attractions/dubare_camp.jpg"}
        ]
    },
    "ooty": {
        "title": "Ooty",
        "state": "Tamil Nadu",
        "lat": 11.4102,
        "lng": 76.6950,
        "description": "Charming hill station known for lakes and botanical gardens.",
        "img": "/assets/trending/ooty.jpg",
        "attractions": [
            {"name": "Ooty Lake", "lat": 11.4116, "lng": 76.6896, "img": "/assets/trending_attractions/ooty_lake.jpg"},
            {"name": "Botanical Garden", "lat": 11.4190, "lng": 76.7118, "img": "/assets/trending_attractions/botanical_garden.jpg"},
            {"name": "Doddabetta Peak", "lat": 11.4004, "lng": 76.7350, "img": "/assets/trending_attractions/doddabetta_peak.jpg"}
        ]
    },
    "darjeeling": {
        "title": "Darjeeling",
        "state": "West Bengal",
        "lat": 27.0360,
        "lng": 88.2627,
        "description": "Famous for tea estates and views of the Himalayas.",
        "img": "/assets/trending/darjeeling.jpg",
        "attractions": [
            {"name": "Tiger Hill", "lat": 27.0000, "lng": 88.2433, "img": "/assets/trending_attractions/tiger_hill.jpg"},
            {"name": "Batasia Loop", "lat": 27.0210, "lng": 88.2475, "img": "/assets/trending_attractions/batasia_loop.jpg"},
            {"name": "Toy Train", "lat": 27.0425, "lng": 88.2661, "img": "/assets/trending_attractions/toy_train.jpg"}
        ]
    },
    "shimla": {
        "title": "Shimla",
        "state": "Himachal Pradesh",
        "lat": 31.1048,
        "lng": 77.1734,
        "description": "Historic hill station with colonial architecture and cool weather.",
        "img": "/assets/trending/shimla.jpg",
        "attractions": [
            {"name": "Mall Road", "lat": 31.1044, "lng": 77.1722, "img": "/assets/trending_attractions/mall_road.jpg"},
            {"name": "Kufri", "lat": 31.1000, "lng": 77.2667, "img": "/assets/trending_attractions/kufri.jpg"},
            {"name": "Jakhoo Temple", 'lat': 31.1014, 'lng': 77.1852, "img": "/assets/trending_attractions/jakhoo_temple.jpg"}
        ]
    }
}

data["cities"].update(new_cities)

with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Updated data.json successfully.")
