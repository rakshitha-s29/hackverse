import os
import requests
import time
from urllib.parse import quote

# Create data directory if it doesn't already exist
base_dir = 'assets/trending_attractions'
os.makedirs(base_dir, exist_ok=True)

# List of missing images for the 6 new cities
attractions = {
    'solang_valley.jpg': 'Solang Valley Manali photo',
    'rohtang_pass.jpg': 'Rohtang Pass scenic photo',
    'hadimba_temple.jpg': 'Hadimba Temple Manali photo',
    'tea_gardens.jpg': 'Munnar Tea Gardens landscape',
    'eravikulam_park.jpg': 'Eravikulam National Park Munnar',
    'mattupetty_dam.jpg': 'Mattupetty Dam Munnar',
    'abbey_falls.jpg': 'Abbey Falls Coorg',
    'rajas_seat.jpg': "Raja's Seat Coorg",
    'dubare_camp.jpg': 'Dubare Elephant Camp Coorg',
    'ooty_lake.jpg': 'Ooty Lake park',
    'botanical_garden.jpg': 'Ooty Botanical Garden scenic',
    'doddabetta_peak.jpg': 'Doddabetta Peak Ooty view',
    'tiger_hill.jpg': 'Tiger Hill Darjeeling sunrise',
    'batasia_loop.jpg': 'Batasia Loop Darjeeling',
    'toy_train.jpg': 'Darjeeling Himalayan Railway Toy Train',
    'mall_road.jpg': 'Shimla Mall Road evening',
    'kufri.jpg': 'Kufri Shimla snow',
    'jakhoo_temple.jpg': 'Jakhoo Temple Shimla statue'
}

# User-agent to look like a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
}

print(f"Beginning download of {len(attractions)} images...")

for filename, query in attractions.items():
    dest_path = os.path.join(base_dir, filename)
    
    # Skip if already exists
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        print(f"Skipping {filename}, already exists.")
        continue
        
    print(f"Search & Download: {filename} ({query})...")
    
    try:
        # We'll use Wikimedia Commons as it's generally safe for static assets
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&pithumbsize=800&generator=search&gsrsearch={quote(query)}&gsrlimit=1"
        
        response = requests.get(search_url, headers=headers, timeout=10)
        data = response.json()
        
        pages = data.get('query', {}).get('pages', {})
        if pages:
            # Get first page with a thumbnail
            for page_id in pages:
                page = pages[page_id]
                if 'thumbnail' in page:
                    image_url = page['thumbnail']['source']
                    print(f"  Found URL: {image_url}")
                    
                    img_response = requests.get(image_url, headers=headers, timeout=15)
                    if img_response.status_code == 200:
                        with open(dest_path, 'wb') as f:
                            f.write(img_response.content)
                        print(f"  Successfully saved -> {filename}")
                    else:
                        print(f"  Failed to download image (status: {img_response.status_code})")
                    break
            else:
                print(f"  No thumbnail found for {query}")
        else:
            print(f"  No search results for {query}")
            
    except Exception as e:
        print(f"  An error occurred downloading {filename}: {e}")
        
    # Sleep to avoid rate limits
    time.sleep(2.5)

print("Finished all image downloads.")
