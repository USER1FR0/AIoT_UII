from machine import Pin, ADC, reset  # Asegúrate de importar 'reset' de 'machine'
import time
import network
from umqtt.simple import MQTTClient

# 📡 Configuración WiFi
WIFI_SSID = "Galaxy S22 Ultra"
WIFI_PASSWORD = "Jp159000"

# 📡 Configuración MQTT
MQTT_CLIENT_ID = "esp32_sound_sensor"
MQTT_BROKER = "192.168.124.135"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/hoyo"

sensor_pin = Pin(14, Pin.IN)

def conectar_wifi():
    print("Conectando a WiFi...", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    
    tiempo_max_espera = 10  # Espera máxima de 10 segundos
    while not sta_if.isconnected() and tiempo_max_espera > 0:
        print(".", end="")
        time.sleep(1)
        tiempo_max_espera -= 1

    if sta_if.isconnected():
        print("\nWiFi Conectada!")
    else:
        print("\nNo se pudo conectar a WiFi")
        reset()  # Reiniciar el ESP32 si no se conecta a WiFi

# 📌 Función para manejar mensajes MQTT
def llegada_mensaje(topic, msg):
    print(f"Mensaje recibido en {topic.decode()}: {msg.decode()}")

# 📌 Función para conectarse a MQTT
def conectar_mqtt():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.set_callback(llegada_mensaje)  # Asignar la función para recibir mensajes
    try:
        client.connect()
        client.subscribe(MQTT_TOPIC)  # Suscribirse al tópico de sonido
        print(f"Conectado a MQTT {MQTT_BROKER} y suscrito a {MQTT_TOPIC}")
        return client
    except Exception as e:
        print(f"Error al conectar a MQTT: {e}")
        reset()  # Reiniciar el ESP32 si no se conecta a MQTT

conectar_wifi()

client = conectar_mqtt()

ultimo_valor = None
while True:
    try:
        valor = sensor_pin.value()

        if valor != ultimo_valor:
            mensaje = str(valor)
            print(f"📤 Publicando valor: {mensaje}")
            client.publish(MQTT_TOPIC, mensaje)
            ultimo_valor = valor  # Actualizar valor previo

        # Revisar si hay mensajes en el tópico (para ver los valores publicados)
        client.check_msg()

    except Exception as e:
        print(f"⚠️ Error en la lectura del sensor: {e}")

    time.sleep(1)  # Leer cada 1 segundo
