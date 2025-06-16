document.addEventListener("DOMContentLoaded", function () {
    var map = L.map("map").setView([19.4326, -99.1332], 13);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap contributors"
    }).addTo(map);

    var origenMarker = L.marker([19.4326, -99.1332], { draggable: true }).addTo(map);
    var destinoMarker = L.marker([19.4352, -99.1406], { draggable: true }).addTo(map);
    var rutaLayer = L.layerGroup().addTo(map);

    origenMarker.on("dragend", function () {
        var coord = origenMarker.getLatLng();
        document.getElementById("origen").value = `${coord.lat}, ${coord.lng}`;
    });

    destinoMarker.on("dragend", function () {
        var coord = destinoMarker.getLatLng();
        document.getElementById("destino").value = `${coord.lat}, ${coord.lng}`;
    });

    window.actualizarMapa = function (rutaGeojson) {
        if (!rutaGeojson || !rutaGeojson.coordinates || rutaGeojson.coordinates.length === 0) {
            console.error("No se recibió una ruta válida");
            return;
        }
    
        rutaLayer.clearLayers();
    
        var coordenadas = rutaGeojson.coordinates.map(coord => [coord[1], coord[0]]);
    
        var nuevaRuta = L.polyline(coordenadas, {
            color: "blue",
            weight: 4
        }).addTo(rutaLayer);
    
        map.fitBounds(nuevaRuta.getBounds());
        map.invalidateSize();  // Corrige problemas de visualización en algunos casos
    };
    
});
