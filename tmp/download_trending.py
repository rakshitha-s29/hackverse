import os, time, requests

base_dir = 'assets/trending_attractions'
os.makedirs(base_dir, exist_ok=True)

attractions = {
    'solang_valley.jpg': 'Solang Valley Manali',
    'rohtang_pass.jpg': 'Rohtang Pass',
    'hadimba_temple.jpg': 'Hadimba Temple Manali',
    'tea_gardens.jpg': 'Munnar Tea Garden',
    'eravikulam_park.jpg': 'Eravikulam National Park',
    'mattupetty_dam.jpg': 'Mattupetty Dam',
    'abbey_falls.jpg': 'Abbey Falls Coorg',
    'rajas_seat.jpg': "Raja's Seat Coorg",
    'dubare_camp.jpg': 'Dubare Elephant Camp',
    'ooty_lake.jpg': 'Ooty Lake',
    'botanical_garden.jpg': 'Botanical Garden Ooty',
    'doddabetta_peak.jpg': 'Doddabetta Peak',
    'tiger_hill.jpg': 'Tiger Hill Darjeeling',
    'batasia_loop.jpg': 'Batasia Loop',
    'toy_train.jpg': 'Darjeeling Toy Train',
    'mall_road.jpg': 'Shimla Mall Road',
    'kufri.jpg': 'Kufri Shimla',
    'jakhoo_temple.jpg': 'Jakhoo Temple'
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}

for filename, query in attractions.items():
    print(f'Fetching {filename} for {query}')
    try:
        url = 'https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&pithumbsize=800&generator=search&gsrsearch=' + requests.utils.quote(query) + '&gsrlimit=1'
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            pages = data.get('query', {}).get('pages', {})
            for _, info in pages.items():
                if 'thumbnail' in info:
                    img_url = info['thumbnail']['source']
                    img_r = requests.get(img_url, headers=headers)
                    if img_r.status_code == 200:
                        with open(os.path.join(base_dir, filename), 'wb') as f:
                            f.write(img_r.content)
                        print(f'Saved {filename}')
                        break
        elif r.status_code == 429:
            print('Hit 429 on Wiki. Sleeping 5 seconds...')
            time.sleep(5)
            # Re-try once
            r = requests.get(url, headers=headers)
            # ... process it or log error
        time.sleep(2)
    except Exception as e:
        print(f'Error searching for {query}: {e}')
