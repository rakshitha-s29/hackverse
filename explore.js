// explore.js

document.addEventListener('DOMContentLoaded', () => {

    const regions = {
      north: [
        { name: "Manali", img: "https://images.unsplash.com/photo-1626714485864-793540c9535c", tag: "Snow Adventure" },
        { name: "Jaipur", img: "https://images.unsplash.com/photo-1477587458883-47145ed94245", tag: "Heritage" },
        { name: "Leh Ladakh", img: "https://images.unsplash.com/photo-1570535312015-81232d34a413", tag: "Mountains" },
        { name: "Delhi", img: "https://images.unsplash.com/photo-1587474260584-136574528ed5", tag: "Capital" },
        { name: "Varanasi", img: "https://images.unsplash.com/photo-1561359313-0639aad49ca6", tag: "Spiritual" },
        { name: "Amritsar", img: "https://images.unsplash.com/photo-1514222026365-5c1cfad8cba4", tag: "Golden Temple" },
        { name: "Rishikesh", img: "https://images.unsplash.com/photo-1549487565-d01f2fdeacac", tag: "Yoga & Adventure" },
        { name: "Gulmarg", img: "https://images.unsplash.com/photo-1533512140645-f09c37129b9", tag: "Ski Resort" }
      ],
      south: [
        { name: "Goa", img: "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2", tag: "Beaches" },
        { name: "Munnar", img: "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944", tag: "Tea Gardens" },
        { name: "Coorg", img: "https://images.unsplash.com/photo-1596422846543-74c6ba68a4d4", tag: "Coffee Hills" },
        { name: "Hampi", img: "https://images.unsplash.com/photo-1620766182966-c6eb5ed2b788", tag: "Temple Ruins" },
        { name: "Ooty", img: "https://images.unsplash.com/photo-1596422846543-74c6ba68a4d4", tag: "Queen of Hills" },
        { name: "Alleppey", img: "https://images.unsplash.com/photo-1593351415075-3bac9f45c877", tag: "Backwaters" },
        { name: "Kodaikanal", img: "https://images.unsplash.com/photo-1518104593124-ac2e82a5eb9d", tag: "Princess of Hills" },
        { name: "Madurai", img: "https://images.unsplash.com/photo-1582510003544-4d00b7f7415e", tag: "Temple City" }
      ],
      northeast: [
        { name: "Shillong", img: "https://images.unsplash.com/photo-1626014903706-e7d6270fc6da", tag: "Clouds" },
        { name: "Kaziranga", img: "https://images.unsplash.com/photo-1590050752117-238cb0fb12b1", tag: "Wildlife" },
        { name: "Tawang", img: "https://images.unsplash.com/photo-1558231263-2283a0429f9f", tag: "Monasteries" },
        { name: "Gangtok", img: "https://images.unsplash.com/photo-1582510003544-4d00b7f7415e", tag: "Himalayas" },
        { name: "Pelling", img: "https://images.unsplash.com/photo-1582510003544-4d00b7f7415e", tag: "Views" },
        { name: "Ziro Valley", img: "https://images.unsplash.com/photo-1626014903706-e7d6270fc6da", tag: "Lush Hills" },
        { name: "Majuli", img: "https://images.unsplash.com/photo-1590050752117-238cb0fb12b1", tag: "River Island" },
        { name: "Imphal", img: "https://images.unsplash.com/photo-1558231263-2283a0429f9f", tag: "Valley Views" }
      ]
    };

    const regionBtns = document.querySelectorAll('.region-btn');
    const grid = document.getElementById('region-destinations-grid');

    regionBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all
            regionBtns.forEach(b => b.classList.remove('active'));
            // Add active class to clicked
            btn.classList.add('active');

            const regionKey = btn.getAttribute('data-region');
            renderRegion(regionKey);
        });
    });

    function renderRegion(regionKey) {
        // Fade out
        grid.classList.remove('show');

        setTimeout(() => {
            grid.innerHTML = '';
            
            const destinations = regions[regionKey];
            if (destinations && destinations.length > 0) {
                destinations.forEach(item => {
                    const cardAnchor = document.createElement('a');
                    // We map them to a mock dynamic route, or static
                    cardAnchor.href = `/city/${item.name.toLowerCase().replace(' ', '')}`;
                    cardAnchor.className = 'card folder-card-photo'; // using folder-card-photo class for unified luxury styling
                    cardAnchor.style.textDecoration = 'none';
                    cardAnchor.style.display = 'block';
                    cardAnchor.style.height = '250px'; // consistent height
                    
                    let tagHTML = item.tag ? `<div class="card-tag">${item.tag}</div>` : '';
                    cardAnchor.innerHTML = `
                        ${tagHTML}
                        <img src="${item.img}?auto=format&fit=crop&q=80&w=800" alt="${item.name}">
                        <div class="folder-overlay" style="background: linear-gradient(to top, rgba(0,0,0,0.9), transparent);">
                            <span style="font-size:24px; font-weight:800; position:absolute; bottom:20px; left:20px;">${item.name}</span>
                        </div>
                    `;
                    grid.appendChild(cardAnchor);
                });
            } else {
                grid.innerHTML = `<div class="region-empty-state">No destinations found for this region.</div>`;
            }

            // Fade in
            grid.classList.add('show');
        }, 300); // 300ms matches the CSS transition duration (or approximate)
    }
});
