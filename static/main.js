var socket = io();

socket.on('connect', function () {
    console.log('Connected');
    socket.emit('start_stream');
});

socket.on('log', function (data) {
    console.log("entre")
    var consoleDiv = document.querySelector('.log-console');
    var p = document.createElement('p');
    p.classList.add('console-text')
    p.innerText = data;
    consoleDiv.appendChild(p);
});

socket.on('obtener_datos', function (data) {
    var consoleDiv = document.querySelector('.datosContainer');
    var p = document.createElement('p');
    p.classList.add('console-text')
    p.innerText = data;
    consoleDiv.appendChild(p);
    // Acceder a los datos recibidos
    var listaPuertos = data.lista_puertos;
    var puertoLider = data.puerto_lider;
    var miPuerto = data.mi_puerto;
    var miId = data.mi_id;
    console.log(listaPuertos,puertoLider)
    // Mostrar los datos en el front-end
    var datosContainer = document.getElementById('datosContainer');
    datosContainer.innerHTML = `
                <p>Lista de puertos: ${listaPuertos.join(', ')}</p>
                <p>Puerto del líder: ${puertoLider}</p>
                <p>Mi puerto: ${miPuerto}</p>
                <p>Mi ID: ${miId}</p>
            `;
    consoleDiv.appendChild(datosContainer);
});