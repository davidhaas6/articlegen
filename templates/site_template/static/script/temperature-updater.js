// Function to update the temperature
function updateTemperature() {
    // Simulate fetching temperature (replace with actual API call in production)
    const fahrenheit = Math.floor(Math.random() * (95 - 75) + 75);
    const rankine = Math.round(fahrenheit + 459.67);
    const ratCities = [
        "Ratopolis",
        "Whiskerburg",
        "New Squeakton",
        "Rodentia Falls",
        "Cheeseville",
        "Furrington",
        "Tailsville",
        "Nibbleton",
        "Scurry City",
        "Gnawopolis",
        "Port Whisker"
    ];

    const randomIndex = Math.floor(Math.random() * ratCities.length);

    // Update the DOM
    const temperatureElement = document.getElementById('temperature');
    console.log(temperatureElement);
    console.log(`${rankine}°R, ${ratCities[randomIndex]}`);
    if (temperatureElement) {
        temperatureElement.textContent = `${rankine}°R, ${ratCities[randomIndex]}`;
    }
}

// Update temperature after a short delay (load html in) and then periodically
setTimeout(updateTemperature, 10);
setInterval(updateTemperature, 5 * 1000); 
