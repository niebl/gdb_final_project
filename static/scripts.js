// script file

// Initialize map and tile layer
const map = L.map('map').setView([51.96, 7.62], 11);

// Store the tile layer reference
const tileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
	maxZoom: 19
}).addTo(map);