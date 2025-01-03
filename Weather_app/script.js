const mapContainer = $("#map-container");
let countryP = $(".country");
let idP = $(".temp_c");
let latP = $("#lat");
let lonP = $("#lon");
let nameP = $(".name");
let regionP = $(".region");
let urlP = $(".url");
let humidity = $(".humidity");
let tz_id = $(".tz_id");
let wind_kph = $(".wind_kph");
let img = document.getElementById("weatherIcon");
const apiKey = "6b8de6d0cd6140579a4140304242112";
const city = document.getElementById("location-input").value;
var map = L.map('map').setView([0, 0], 13);

var marker;

getLocation();


async function fetchSuggestions() {
  const query = document.getElementById("location-input").value.trim();
  const suggestionsList = document.getElementById("suggestions");

  // Clear previous suggestions
  suggestionsList.innerHTML = "";

  if (query.length < 1) return;

  const apiUrl = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&addressdetails=1&limit=5`;

  try {
    const response = await fetch(apiUrl);
    if (!response.ok) {
      console.error("Error fetching suggestions:", response.statusText);
      return;
    }

    const data = await response.json();

    // Populate suggestions
    data.forEach((place) => {
      const li = document.createElement("li");
      li.innerHTML = `
        <span>${place.display_name.split(",")[0]}</span>
        <span class="country">${place.address.country}</span>
      `;
      li.addEventListener("click", () => {
        document.getElementById("location-input").value = `${place.display_name.split(",")[0]}, ${place.address.country}`;
        suggestionsList.innerHTML = ""; // Clear suggestions
      });
      suggestionsList.appendChild(li);
    });
  } catch (error) {
    console.error("Error fetching suggestions:", error);
  }
}

// Close suggestions when clicking outside
document.addEventListener("click", (event) => {
  if (!event.target.closest(".user-interface")) {
    document.getElementById("suggestions").innerHTML = "";
  }
});


function darkMode() {
  var element = document.body;
  element.classList.toggle("dark-mode");
}
//--------------------------------------getCurrentPosition-----------------------------------
let latitude;
let longitude;
function getLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(showPosition);
  } else {
    alert("Geolocation is not supported by this browser.");
  }
}
function showPosition(position) {
  latitude = position.coords.latitude;
  longitude = position.coords.longitude;
  fetchWeatherData(latitude + "," + longitude);


  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(map);

  marker = L.marker([latitude, longitude]).addTo(map);
  marker.setLatLng([latitude, longitude]).update();
  map.setView([latitude, longitude]);

  const geoApiUrl = `https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${latitude}&longitude=${longitude}&localityLanguage=en`;


    
  $.ajax({
    method: "GET",
    url: geoApiUrl,
    success: (resp) => {
      console.log('====================================');
      console.log(resp);
      console.log('====================================');
    }
  })
  
}





//-------------------------------------------handleSearch----------------------------------------

function handleSearch() {
  const location = document.getElementById("location-input").value;
  fetchWeatherData(location);
}
document.getElementById("search-button").addEventListener("click", handleSearch);

function fetchWeatherData(location) {
  $.ajax({
    method: "GET",
    url: `https://api.weatherapi.com/v1/current.json?key=${apiKey}&q=${location}`,
    success: ({ location, current }) => {
      countryP.text(location.country);
      idP.text(current.temp_c + "°C");
      latP.text(location.lat);
      lonP.text(location.lon);
      nameP.text(location.name);
      regionP.text(location.region);
      urlP.text(current.condition.text);
      humidity.text(current.humidity + "%");
      tz_id.text(location.tz_id);
      wind_kph.text(current.wind_kph + "kph");
      img.src = current.condition.icon;

      // Update the map and marker
      marker.setLatLng([location.lat, location.lon]).update();
      map.setView([location.lat, location.lon]);

      // Display the local time for the searched city
      const cityTimeZone = location.tz_id;

      // Get the current time for the city using Luxon
      const cityTime = luxon.DateTime.now().setZone(cityTimeZone).toFormat('MMMM dd, yyyy - hh:mm a');
      
      // Update the local time element with the formatted date-time
      const localTimeElement = document.getElementById("local-time");
      localTimeElement.textContent = cityTime;  // Show the city's local time
    
    }
  });
}


// ------------------------------------getWeatherTimeLine---------------------------------

function getWeatherTimeLine() {

  $.ajax({
    method: "GET",
    url: `https://api.weatherapi.com/v1/forecast.json?key=${apiKey}&q=${city}&days=7&aqi=no&alerts=no`, // Fetch 7-day forecast
    success: (resp) => {
      // Iterate through the next 7 days of the forecast
      for (let i = 0; i < 7; i++) {
        const forecastDay = resp.forecast.forecastday[i];

        // Get the weather icons, titles, and dates for each day
        const img = document.getElementById(`img${i + 1}`);
        const title = document.querySelector(`.title${i + 1}`);
        const date = document.getElementById(`date${i + 1}`);

        // Update weather icon
        img.src = `https:${forecastDay.day.condition.icon}`; // Dynamically set the weather icon from the API

        // Update weather condition description
        title.innerHTML = forecastDay.day.condition.text;

        // Update date
        date.innerHTML = forecastDay.date;
      }
    },
    error: (error) => {
      console.error("Error fetching weather forecast:", error);
    }
  });
}

getWeatherTimeLine();
