import os
import requests
import time

# Create data directory
base_dir = 'assets/trending_attractions'
os.makedirs(base_dir, exist_ok=True)

# Unsplash source mappings (specific high-quality photos)
attractions = {
    'solang_valley.jpg': 'https://images.unsplash.com/photo-1590408544465-98511ce5172c?auto=format&fit=crop&q=80&w=800',
    'rohtang_pass.jpg': 'https://images.unsplash.com/photo-1549487565-d01f2fdeacac?auto=format&fit=crop&q=80&w=800',
    'hadimba_temple.jpg': 'https://images.unsplash.com/photo-1514222026365-5c1cfad8cba4?auto=format&fit=crop&q=80&w=800',
    'tea_gardens.jpg': 'https://images.unsplash.com/photo-1593351415075-3bac9f45c877?auto=format&fit=crop&q=80&w=800',
    'eravikulam_park.jpg': 'https://images.unsplash.com/photo-1502082553048-f009c37129b9?auto=format&fit=crop&q=80&w=800',
    'mattupetty_dam.jpg': 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&q=80&w=800',
    'abbey_falls.jpg': 'https://images.unsplash.com/photo-1541414779247-5586548dbbb3?auto=format&fit=crop&q=80&w=800',
    'rajas_seat.jpg': 'https://images.unsplash.com/photo-1590050752117-238cb0fb12b1?auto=format&fit=crop&q=80&w=800',
    'dubare_camp.jpg': 'https://images.unsplash.com/photo-1515544464164-325bdf2559fd?auto=format&fit=crop&q=80&w=800',
    'ooty_lake.jpg': 'https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&q=80&w=800',
    'botanical_garden.jpg': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&q=80&w=800',
    'doddabetta_peak.jpg': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&q=80&w=800',
    'tiger_hill.jpg': 'https://images.unsplash.com/photo-1518104593124-ac2e82a5eb9d?auto=format&fit=crop&q=80&w=800',
    'batasia_loop.jpg': 'https://images.unsplash.com/photo-1563211516-43b95a864d4b?auto=format&fit=crop&q=80&w=800',
    'toy_train.jpg': 'https://images.unsplash.com/photo-1587474260584-136574528ed5?auto=format&fit=crop&q=80&w=800',
    'mall_road.jpg': 'https://images.unsplash.com/photo-1549487565-d01f2fdeacac?auto=format&fit=crop&q=80&w=800',
    'kufri.jpg': 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&q=80&w=800',
    'jakhoo_temple.jpg': 'https://images.unsplash.com/photo-1514222026365-5c1cfad8cba4?auto=format&fit=crop&q=80&w=800'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
}

print(f"Beginning download of {len(attractions)} images...")

for filename, url in attractions.items():
    dest_path = os.path.join(base_dir, filename)
    
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        continue
        
    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code == 200:
            with open(dest_path, 'wb') as f:
                f.write(response.content)
            print(f"Saved {filename}")
        else:
            print(f"Failed {filename}: {response.status_code}")
    except Exception as e:
        print(f"Error {filename}: {e}")
        
    time.sleep(1.0)

print("Batch completed.")
