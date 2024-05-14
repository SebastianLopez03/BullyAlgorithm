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

socket.on('obtener_lider', function(data){
    // Selecciona el elemento HTML que contiene la hora
    var horaElement = document.getElementById('hora');
    // Actualiza el contenido del elemento con el valor recibido en 'data'
     horaElement.innerText = "" + data;
});

socket.on('obtener_datos', function (data) {
    // Acceder a los datos recibidos
    var puertoLider = data.puerto_lider;
    var miPuerto = data.mi_puerto;
    var miId = data.mi_id;

    // Actualizar la hora con el puerto líder
   if (miPuerto == puertoLider){
    var horaElement = document.getElementById('hora');
    horaElement.innerText = "Soy el  líder: " + miPuerto;
   }else{
    var horaElement = document.getElementById('hora');
    horaElement.innerText = "Puerto Líder: " + puertoLider;
   }

    // Actualizar el cliente con el estado (lider/no lider) y los datos propios
    var clienteElement = document.getElementById('cliente');
    if (miPuerto === puertoLider) {
        clienteElement.innerText = "- Puerto: " + miPuerto + " - ID: " + miId;
    } else {
        clienteElement.innerText = "- Puerto: " + miPuerto + " - ID: " + miId;
    }

});
