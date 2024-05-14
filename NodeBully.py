from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import time
from datetime import datetime   
import random
from threading import Thread 
import threading
import sched
import requests


url = 'http://10.4.75.114'
app = Flask(__name__)
socketio = SocketIO(app)
Lista_puertos = []
lider = None
puerto = None
peso = None
get_lider_running = False
tread = False

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/agregar_numero', methods=['POST'])
def agregar_numero():
    data = request.get_json()
    numero = data.get('numero')
    if numero is not None:
        try:
            numero = int(numero)
            if numero in Lista_puertos:
                sendlog("Error: El puerto ya existe en la lista ", "")
                return jsonify({"mensaje": "Error: El número ya existe en la lista."}), 400
            else:
                Lista_puertos.append(numero)
                sendlog(f'Puerto {numero} agregado correctamente ','')
                print(Lista_puertos)
                
                return jsonify({"mensaje": "Número agregado correctamente a la lista.", "lista": Lista_puertos}), 200
        except ValueError:
            sendlog("Error: El valor enviado no es un numero entero","")
            return jsonify({"mensaje": "Error: El valor enviado no es un número entero."}), 400
    else:
        sendlog("Error: No se ha proporcionado ningun valor en la solicitud","")
        return jsonify({"mensaje": "Error: No se proporcionó ningún número en la solicitud."}), 400

@app.route('/healthcheck', methods=['GET'])
def health_check():
    # Aquí puedes realizar cualquier verificación necesaria para determinar el estado de salud de la aplicación
    # Por ejemplo, podrías verificar la conectividad a la base de datos, el estado de la memoria, etc.
    
    # Devuelve un código de estado 200 OK si la aplicación está saludable
    return 'OK', 200

def start_health_check(interval):
    global lider, scheduler
    
    print(f'aqui estoy lider es {lider}')
    if lider == -1:
        sendlog("No hay puertos en mi lista soy el lider","")
        print('soy el lider')
    else:
        print('aqui estoy preocupate')
        sendlog(f"Se va a empezar a realizar helatCheck al lider {lider} cada {interval} segundos","")
        scheduler = sched.scheduler(time.time, time.sleep)  # Define el planificador
        print(interval)
        periodic_task(interval)
    
    # Define la función de verificación de la aplicación
def check_app_health():
    global lider, url
    healthcheck_url = f'{url}:{lider}/healthcheck'
    
    try:
        response = requests.get(healthcheck_url)
        response.raise_for_status()  # Lanza una excepción si ocurre un error HTTP
        print("La aplicación está en un estado saludable.")
    except requests.exceptions.RequestException as e:
        print("Error al verificar el estado de la aplicación:")
        print("El servidor está indisponible. La aplicación continúa su curso normal.")
        sendlog(f"el lider {lider} no esta disponible se busca nuevo lider","")
        get_lider()

# Define la función que programa la verificación periódica
def periodic_task(interval):
    global t, tread
    tread = True
    if lider != -1:
        check_app_health()  # Realiza la verificación
    scheduler.enter(interval, 1, periodic_task, (interval,))  # Programa la próxima verificación

# Inicia la verificación periódica
    scheduler.enter(interval, 1, periodic_task, (interval,))

# Ejecuta el planificador en un hilo separado
    t = Thread(target=scheduler.run)
    t.daemon = True
    t.start()

@app.route('/get_weight', methods=['GET'])
def get_weight():
    global peso
    # Obtiene el peso del nodo actual
    peso_actual = peso
    # Obtiene el peso enviado en la solicitud
    peso_solicitado = int(request.args.get('peso'))
    
    if peso_actual > peso_solicitado:
        respuesta = "Mayor"
        sendlog("El peso del Nodo verifiacdor es menor inicio a buscar un lider mayor","")
        threading.Thread(target=get_lider).start()
    elif peso_actual < peso_solicitado:
        respuesta = "Menor"
    else:
        respuesta = "Igual"
    
    return jsonify({"respuesta": respuesta})

def get_lider():
    global Lista_puertos, lider, url, peso, t, get_lider_running
    get_lider_running = True
    llamadas =0
    timeout=5
    respuesta = None
    while (llamadas<len(Lista_puertos)):
        try:
            get_weight_url = f'{url}:{Lista_puertos[llamadas]}/get_weight'
            # Realiza una solicitud GET al otro nodo con un tiempo de espera
            response = requests.get(get_weight_url, params={'peso': peso}, timeout=timeout)
            # Verifica si la solicitud fue exitosa
            response.raise_for_status()
            # Obtiene la respuesta JSON
            respuesta_json = response.json()
            # Extrae la respuesta del JSON
            respuesta = respuesta_json.get('respuesta')
            # Imprime la respuesta recibida
            print("Respuesta del otro nodo:", respuesta)
        except requests.exceptions.RequestException as e:
            # Maneja cualquier error de solicitud, incluido el tiempo de espera agotado
            sendlog(f"EL Nodo {Lista_puertos[llamadas]} no esta disponible","")
            print("Error al solicitar información del otro nodo:",e) 
        if respuesta == "Mayor":
            print("Ejecutar")
            sendlog(f"El nodo {Lista_puertos[llamadas]} tiene un peso {respuesta} que es mayor a {peso}","")
        elif respuesta == "Menor" or respuesta == "Igual":
            sendlog(f"El nodo {Lista_puertos[llamadas]} tiene un peso {respuesta} que es menor a {peso}","")
            # Continuar ejecutándose normalmente
            pass
        llamadas+=1
    if llamadas == len(Lista_puertos):
        lider = -1
        tread = False
        sendlog(f"No hay un nodo con un peso mayor a {peso} ahora soy el lider", "")

        enviar_nuevo_lider()
        print('Ahora soy el lider')
    

get_lider_running = False

@app.route('/nuevo_lider', methods=['POST'])
def nuevo_lider():
    global lider
    data = request.get_json()
    nuevo_lider = data.get('nuevo_lider')
    if nuevo_lider is not None:
        lider = nuevo_lider
        print(f"El nuevo líder es: {lider}")
        obtener_lider(lider)
        sendlog(f"El  nuevo lider es {nuevo_lider} y se ha guardado correctamente","")
        return jsonify({"mensaje": "Nuevo líder establecido correctamente."}), 200
    else:
        sendlog(f"Error: No se ha detectado un nuevo lider dentro de la solicitud","")
        return jsonify({"mensaje": "Error: No se proporcionó ningún nuevo líder en la solicitud."}), 400
    

def enviar_nuevo_lider():
    global Lista_puertos, url, mi_puerto
    obtener_lider(mi_puerto)
    for puerto in Lista_puertos:
        try:
            # Construye la URL para enviar el nuevo líder al nodo actual
            url_nuevo_lider = f'{url}:{puerto}/nuevo_lider'
            # Realiza una solicitud POST al otro nodo con el nuevo líder
            response = requests.post(url_nuevo_lider, json={"nuevo_lider": mi_puerto})
            # Verifica si la solicitud fue exitosa
            response.raise_for_status()
            sendlog(f"El  nuevo lider fue enviado al puerto {puerto}","")
            print(f"Nuevo líder enviado al nodo {puerto}")
        except requests.exceptions.RequestException as e:
            # Maneja cualquier error de solicitud
            sendlog(f"Error al enviar el lider al puerto {puerto}, el puerto en cuestion no responde","")
            print(f"Error al enviar nuevo líder al nodo {puerto}")

@socketio.on('connect')
def test_connect():
    print('Client connected')

@socketio.on('start_stream')
def handle_start_stream():
    print('Client connected and started streaming')

def enviar_datos_al_cliente(msg):
    global mi_puerto, lider, peso, Lista_puertos
    mensaje = msg
    # Envía los datos al cliente a través del WebSocket
    if lider == -1:
        emit('obtener_datos', {
        'puerto_lider': mi_puerto,
        'mi_puerto': mi_puerto,
        'mi_id': peso
        })
    else:
        emit('obtener_datos', {
        'puerto_lider': lider,
        'mi_puerto': mi_puerto,
        'mi_id': peso
        })

@socketio.on('connect')
def handle_connect():
    # Envía los datos al cliente al conectarse por primera vez
    enviar_datos_al_cliente("")
    

def obtener_lider(port):
    socketio.emit('obtener_lider', 'El lider es '+str(port)+'')

def sendlog(msg, ip):
    thetime = datetime.now()
    socketio.emit('log', '['+ thetime.strftime('%m/%d/%y %H:%M:%S') + '] ' + msg + '' + str(ip))


def validar_argumentos():
    import sys
    global Lista_puertos, lider, peso, mi_puerto
    if len(sys.argv) >= 3:  # Se espera al menos 3 argumentos (script, mi_puerto, peso_mi_puerto)
        try:
            mi_puerto = int(sys.argv[1])
            peso_mi_puerto = int(sys.argv[2])
            if len(sys.argv) >= 4:
                Lista_puertos = [int(num) for num in sys.argv[3:-1]]
                if Lista_puertos == []:
                    print("Advertencia: Lista vacía recibida desde la consola.")
            else:
                print("Advertencia: No se recibió ninguna lista de puertos desde la consola.")
            lider = sys.argv[-1]
            if lider == '':
                print("Advertencia: Líder vacío recibido desde la consola.")
            print("Puerto propio recibido desde la consola:", mi_puerto)
            print("Peso de mi puerto recibido desde la consola:", peso_mi_puerto)
            print("Lista de puertos recibida desde la consola:", Lista_puertos)
            print("Líder recibido desde la consola:", lider)
            peso = peso_mi_puerto
            if len(Lista_puertos) == 0:
                lider = -1
                sendlog("No hay otros puertos soy el lider", mi_puerto)
        except ValueError:
            print("Error: Por favor, asegúrate de ingresar solo números para los puertos y pesos.")
            sys.exit(1)
    else:
        print("Error: Se esperaban al menos dos argumentos para 'mi_puerto' y 'peso_mi_puerto'.")
        sys.exit(1)

    
if __name__ == '__main__':
    validar_argumentos()
    # Llama a esta función para iniciar la ejecución periódica del health check
    start_health_check(random.randint(10, 100))  
    app.run(debug=True, host='0.0.0.0')