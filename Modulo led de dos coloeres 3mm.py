from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# Configuración de los pines del LED bicolor
led_rojo = Pin(26, Pin.OUT)   # GPIO26 controla el color rojo
led_verde = Pin(27, Pin.OUT)  # GPIO27 controla el color verde

# Configuración WiFi
WIFI_SSID = "Galaxy S22 Ultra"
WIFI_PASSWORD = "Jp159000"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_led_bicolor"
MQTT_BROKER = "192.168.41.135"  # Cambia por la IP de tu servidor Mosquitto
MQTT_PORT = 1883
MQTT_TOPIC_LED = "actuator/led2colores3mm"

def conectar_wifi():
    """Conecta el ESP32 a la red WiFi."""
    print("[INFO] Conectando a WiFi...")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    
    while not sta_if.isconnected():
        print(".", end="")
        time.sleep(0.5)
    
    print("\n[INFO] WiFi Conectada!")
    print(f"[INFO] Dirección IP: {sta_if.ifconfig()[0]}")

def conectar_mqtt():
    """Conecta a MQTT y maneja reconexiones."""
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        print(f"[INFO] Conectado a MQTT en {MQTT_BROKER}")
        return client
    except Exception as e:
        print(f"[ERROR] No se pudo conectar a MQTT: {e}")
        return None

# Conectar a WiFi y MQTT
conectar_wifi()
client = conectar_mqtt()

# Estado anterior para evitar mensajes repetidos
estado_anterior = None

# Bucle principal
while True:
    try:
        # Verificar conexión WiFi
        if not network.WLAN(network.STA_IF).isconnected():
            print("[ERROR] WiFi desconectado, reconectando...")
            conectar_wifi()
            client = conectar_mqtt()

        # Verificar conexión MQTT
        if client is None:
            print("[ERROR] MQTT desconectado, reconectando...")
            client = conectar_mqtt()
            time.sleep(5)
            continue

        # Alternar entre rojo y verde
        if estado_anterior != "rojo":
            led_rojo.value(1)  # Encender rojo
            led_verde.value(0)  # Apagar verde
            mensaje = "LED ROJO ENCENDIDO"
            client.publish(MQTT_TOPIC_LED, mensaje.encode())
            print(f"[INFO] Publicado en {MQTT_TOPIC_LED}: {mensaje}")
            estado_anterior = "rojo"

        time.sleep(2)

        if estado_anterior != "verde":
            led_rojo.value(0)  # Apagar rojo
            led_verde.value(1)  # Encender verde
            mensaje = "LED VERDE ENCENDIDO"
            client.publish(MQTT_TOPIC_LED, mensaje.encode())
            print(f"[INFO] Publicado en {MQTT_TOPIC_LED}: {mensaje}")
            estado_anterior = "verde"

        time.sleep(2)

    except Exception as e:
        print(f"[ERROR] Error en el loop principal: {e}")
        client = None
