// Function to update the temperature
function updateTemperature() {
    // Simulate fetching temperature (replace with actual API call in production)
    const fahrenheit = Math.floor(Math.random() * (95 - 75) + 75);
    const rankine = Math.round(fahrenheit + 459.67);
    const ratCities = [
        "Ratopolis",
        "Squeattle",         // (Seattle)
        "Cheesago",         // (Chicago)
        "Los Ratos",        // (Los Angeles / Los Gatos)
        "Gnawleans",        // (New Orleans)
        "Rodentsterdam",    // (Amsterdam)
        "Scamperino",       // (San Marino)
        "Squeakramento",    // (Sacramento)
        "Rat Vegas",        // (Las Vegas)
        "San Cheesco",      // (San Francisco)
        "Scurrybrook",      // (Lynchburg or Harrisburg)
        "Montcheesery",     // (Montgomery)
        "Ratsonville",      // (Jacksonville)
        "Scritchmond",      // (Richmond)
        "Ratislava",        // (Bratislava, Slovakia)
        "Squeakterdam",     // (Amsterdam, Netherlands)
        "Gnaw York",        // (New York, USA, but international rats dream of it too!)
        "Cheeseburg",       // (Hamburg, Germany)
        "Ratcelona",        // (Barcelona, Spain)
        "Squeakjing",       // (Beijing, China)
        "Rodentograd",      // (Volgograd, Russia)
        "São Pawlo",        // (São Paulo, Brazil)
        "Scurrybourg",      // (Strasbourg, France)
        "Tailin",           // (Taipei, Taiwan)
        "Gnawnich",         // (Munich, Germany)
        "Mouscow",          // (Moscow, Russia)
        "Zurwhisk",         // (Zurich, Switzerland)
        "Banggnawk",        // (Bangkok, Thailand)
        "Naplesqueak",      // (Naples, Italy)
    ];

    const randomIndex = Math.floor(Math.random() * ratCities.length);

    // Update the DOM
    const temperatureElement = document.getElementById('temperature');
    if (temperatureElement) {
        temperatureElement.textContent = `${rankine}°R, ${ratCities[randomIndex]}`;
    }
}

// Update temperature after a short delay (load html in) and then periodically
setTimeout(updateTemperature, 10);
setInterval(updateTemperature, 5 * 1000); 
