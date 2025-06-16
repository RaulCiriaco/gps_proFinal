async function buscarSugerencias(tipo) {
    const query = document.getElementById(tipo).value;
    if (query.length < 3) return;

    const response = await fetch(`/buscar_lugar?q=${query}`);
    const lugares = await response.json();

    const contenedor = document.getElementById(`sugerencias-${tipo}`);
    contenedor.innerHTML = "";

    lugares.forEach(lugar => {
        const opcion = document.createElement("div");
        opcion.classList.add("sugerencia");
        opcion.textContent = lugar.label;
        opcion.onclick = () => seleccionarUbicacion(tipo, lugar.coordinates);
        contenedor.appendChild(opcion);
    });
}

async function buscarRuta() {
    const origen = document.getElementById("origen").value;
    const destino = document.getElementById("destino").value;
    const transporte = document.getElementById("transporte").value;

    if (!origen || !destino) {
        alert("Por favor, ingresa un origen y destino válido.");
        return;
    }

    const response = await fetch("/ruta", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ origen, destino, transporte })
    });

    const datos = await response.json();

    if (datos.error) {
        alert(datos.error);
        return;
    }

    document.getElementById("distancia_real").textContent = datos.distancia_real + " km";
    document.getElementById("distancia_manhattan").textContent = datos.distancia_manhattan + " km";
    document.getElementById("duracion_real").textContent = datos.duracion_horas + " h " + datos.duracion_minutos + " min";
    document.getElementById("gasolina_litros").textContent = datos.gasolina_litros + " L";
    document.getElementById("costo_gasolina").textContent = "$" + datos.costo_gasolina + " MXN";
    document.getElementById("velocidad_recomendada").textContent = datos.velocidad_recomendada + " km/h"; 

    const listaInstrucciones = document.getElementById("instrucciones");
    listaInstrucciones.innerHTML = "";
    datos.instrucciones.forEach(instruccion => {
        const li = document.createElement("li");
        li.textContent = instruccion;
        listaInstrucciones.appendChild(li);
    });

    actualizarMapa(datos.ruta_geojson);
}
