// script file

// Initialize map and tile layer
const map = L.map('map').setView([51.96, 7.62], 11);

// Store the tile layer reference
const tileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
	maxZoom: 19
}).addTo(map);

		// Function to execute SQL query and add GeoJSON data to the map
function executeQuery() {
	const query = document.getElementById('sqlQuery').value;
	axios.post('/execute-sql', { query })
	.then(response => {
		console.log(response.data);
		if (response.data.length > 0) {
			const geoJsonLayer = L.geoJSON(response.data, {
				onEachFeature: (feature, layer) => {
					if (feature.properties) {
						layer.bindPopup(
							Object.entries(feature.properties)
							.map(([key, value]) => `<b>${key}</b>: ${value}`)
							.join('<br>')
							);
					}
				}
			}).addTo(map);

						// Fit the map to the bounds of the GeoJSON layer
			map.fitBounds(geoJsonLayer.getBounds());
		} else {
			alert('No data returned!');
		}
	})
	.catch(error => {
		console.error(error);
		alert('Error executing query: ' + (error.response?.data?.error || error.message));
	});
}