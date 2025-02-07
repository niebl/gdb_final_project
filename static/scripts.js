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

function findCategories() {
	const query = "SELECT DISTINCT(measurement_type) FROM osem_bike_measurements;"
	const promise = axios.post('/execute-sql', {query})
	
	const outData = promise.then(
		response => {
			category_list = []
			for (let row of response.data){
				category_list.push(row[0])
			}
			return category_list
		})
	.catch(error => {
		console.error(error);
		alert('Error executing query: ' + (error.response?.data?.error || error.message));
	})

	return outData
}

function findDateRange() {
	const query = "select MIN(measurement_time), MAX(measurement_time) from osem_bike_measurements;"
	const promise = axios.post('/execute-sql', {query})
	const outData = promise.then(
		response => {
			range = [
				new Date(response.data[0][0]), 
				new Date(response.data[0][1])
			]
			return range
		})
	.catch(error => {
		console.error(error);
		alert('Error executing query: ' + (error.response?.data?.error || error.message));
	})

	return outData
}

function unixToDatetime(unixString){
	date = new Date(unixString)
	//output = date.getDay()+"."+date.getMonth()+"."+date.getFullYear()+" "+ date.getTime()
	output = date.toISOString()
	return output
}

function initiateMeasurementCategories(category_list){
	$.each(category_list, function (i, item) {
    	$('#category').append($('<option>', { 
        	value: item,
        	text : item 
    	}));
	});
}

// -------------------------------------------
// 	MAIN
// -------------------------------------------

async function main(){
	const date_range = await findDateRange()
	const category_list = await findCategories()

	//initiate category list
	initiateMeasurementCategories(category_list)

	//initiate slider
	$( function() {
		$( "#slider-range" ).slider({
			range: true,
			min: date_range[0].getTime(),
			max: date_range[1].getTime(),
			values: [ date_range[0].getTime(), date_range[1].getTime() ],
			slide: function( event, ui ) {
				$( "#amount" ).val( 
					unixToDatetime(ui.values[ 0 ]) 
					+ " - " + 
					unixToDatetime(ui.values[ 1 ]) );
			}
		});
		$( "#amount" ).val( 
			unixToDatetime($( "#slider-range" ).slider( "values", 0 )) + " - " + 
			unixToDatetime($( "#slider-range" ).slider( "values", 1 )) 
			);
	} );
}

main()