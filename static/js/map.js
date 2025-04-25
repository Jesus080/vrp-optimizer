document.addEventListener("DOMContentLoaded", function () {
    // Datos para el mapa (inyectados desde Flask)
    const data = window.routeData;

    // Inicializar el mapa
    const map = L.map("map").setView([22.5, -102], 5);

    // Añadir capa de OpenStreetMap
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);

    // Iconos personalizados
    const almacenIcon = L.icon({
        iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png",
        shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41],
    });

    const cityIcon = L.icon({
        iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png",
        shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41],
    });

    // Añadir marcador del almacén
    const almacenLatLng = [data.almacen_coords[0], data.almacen_coords[1]];
    L.marker(almacenLatLng, { icon: almacenIcon })
        .addTo(map)
        .bindPopup(`<strong>Almacén: ${data.almacen}</strong>`);

    // Añadir marcadores de ciudades
    for (const [ciudad, coords] of Object.entries(data.ciudades_coords)) {
        if (ciudad !== data.almacen) {
            L.marker([coords[0], coords[1]], { icon: cityIcon })
                .addTo(map)
                .bindPopup(`<strong>${ciudad}</strong>`);
        }
    }

    // Dibujar rutas
    const colors = ["#FF5733", "#33FF57", "#3357FF", "#F3FF33", "#FF33F3"];
    data.rutas.forEach((resultado, index) => {
        const color = colors[index % colors.length];
        const ruta = resultado.ruta;

        if (ruta.length > 0) {
            const routePoints = [almacenLatLng];
            ruta.forEach((ciudad) => {
                const coords = data.ciudades_coords[ciudad];
                routePoints.push([coords[0], coords[1]]);
            });
            routePoints.push(almacenLatLng);

            const polyline = L.polyline(routePoints, {
                color: color,
                weight: 3,
                opacity: 0.8,
            }).addTo(map);

            polyline.bindPopup(
                `<strong>Ruta ${index + 1}</strong><br>
                 Distancia: ${resultado.distancia_total} km<br>
                 Tiempo: ${resultado.tiempo_operacion} horas`
            );
        }
    });

    // Ajustar el mapa para mostrar todas las rutas
    const bounds = [];
    bounds.push(almacenLatLng);
    data.rutas.forEach((resultado) => {
        resultado.ruta.forEach((ciudad) => {
            const coords = data.ciudades_coords[ciudad];
            bounds.push([coords[0], coords[1]]);
        });
    });
    map.fitBounds(L.latLngBounds(bounds), { padding: [50, 50] });
});