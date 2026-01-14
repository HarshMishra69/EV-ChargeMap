console.log("Script loaded");

const map = L.map('map').setView([28.6139, 77.2090], 10);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

// Show Stations
fetch("/stations").then(res=>res.json()).then(data=>{
  data.forEach(station=>{
    L.marker([station.latitude, station.longitude])
      .addTo(map)
      .bindPopup(station.name);
  });
});

// Show AI Suggested Expansion Areas
fetch("/insights").then(res=>res.json()).then(data=>{
  data.new_station_areas.forEach(area=>{
    L.circle([area.latitude, area.longitude],{
      radius:2500,color:"red"
    }).addTo(map).bindPopup("Suggested New Station Area");
  });
});
