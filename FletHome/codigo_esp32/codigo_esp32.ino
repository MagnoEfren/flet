#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>

// ── WiFi ─────────────────────────────────────────────────────
const char* WIFI_SSID     = "XXXXXXXXXXX"; // CAMBIAR 
const char* WIFI_PASSWORD = "XXXXXXXXXXXXXXXX";  // CAMBIAR  

// ── HiveMQ Cloud ─────────────────────────────────────────────
const char* MQTT_BROKER   = "XXXXXXXXXXXXXXXXXXXX.s1.eu.hivemq.cloud";  // CAMBIAR 
const int   MQTT_PORT     = 8883;
const char* MQTT_USER     = "XXXXXXXXX";     // CAMBIAR 
const char* MQTT_PASSWORD = "XXXXXXXXXXXX";        // CAMBIAR 
const char* CLIENT_ID     = "esp32-domotica";

// ── 2 Topics ──────────────────────────────────────────────────
const char* TOPIC_SUB = "domotica/led/cmd";    // app → ESP32 (recibe)
const char* TOPIC_PUB = "domotica/estado";     // ESP32 → app (publica)

// ── Pines ─────────────────────────────────────────────────────
const int PIN_LED   = 2;
const int PIN_BOTON = 0;

// ── Variables globales ────────────────────────────────────────
WiFiClientSecure wifiClient;
PubSubClient     mqttClient(wifiClient);

bool ledEncendido  = false;
int  botonAnterior = HIGH;
unsigned long ultimoReconect = 0;

// ── Prototipos ────────────────────────────────────────────────
void conectarWifi();
bool conectarMQTT();
void callbackMQTT(char* topic, byte* payload, unsigned int length);
void publicarEstado(const char* evento);
void setLed(bool estado, bool publicar = true);

// ═════════════════════════════════════════════════════════════
//  SETUP
// ═════════════════════════════════════════════════════════════
void setup() {
    Serial.begin(115200);
    delay(500);
    Serial.println("\n[ESP32] Iniciando...");

    pinMode(PIN_LED,   OUTPUT);
    pinMode(PIN_BOTON, INPUT_PULLUP);
    digitalWrite(PIN_LED, LOW);

    conectarWifi();

    wifiClient.setHandshakeTimeout(30);
    wifiClient.setInsecure();

    mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
    mqttClient.setCallback(callbackMQTT);
    mqttClient.setBufferSize(512);

    conectarMQTT();
}

// ═════════════════════════════════════════════════════════════
//  LOOP
// ═════════════════════════════════════════════════════════════
void loop() {
    // ── Mantener conexión MQTT ───────────────────────────────
    if (!mqttClient.connected()) {
        unsigned long ahora = millis();
        if (ahora - ultimoReconect > 5000) {
            ultimoReconect = ahora;
            Serial.println("[MQTT] Reconectando...");
            conectarMQTT();
        }
    } else {
        mqttClient.loop();
    }

    // ── Botón BOOT con debounce ───────────────────────────────
    int estadoBoton = digitalRead(PIN_BOTON);

    if (estadoBoton == LOW && botonAnterior == HIGH) {
        delay(50);
        if (digitalRead(PIN_BOTON) == LOW) {
            Serial.println("[Botón] ¡Presionado!");
            bool nuevoEstado = !ledEncendido;
            setLed(nuevoEstado);
            if (nuevoEstado) {
                // Solo notifica al encender
                publicarEstado("boton:pressed");
            }
        }
    }

    botonAnterior = estadoBoton;
    delay(20);
}

// ═════════════════════════════════════════════════════════════
//  FUNCIONES
// ═════════════════════════════════════════════════════════════
void conectarWifi() {
    Serial.printf("[WiFi] Conectando a %s", WIFI_SSID);
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    int intentos = 0;
    while (WiFi.status() != WL_CONNECTED && intentos < 30) {
        delay(500);
        Serial.print(".");
        intentos++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.printf("\n[WiFi] ✅ Conectado: %s\n",
                      WiFi.localIP().toString().c_str());
    } else {
        Serial.println("\n[WiFi] ❌ Error. Reiniciando...");
        delay(3000);
        ESP.restart();
    }
}

bool conectarMQTT() {
    Serial.printf("[MQTT] Conectando a %s:%d...\n", MQTT_BROKER, MQTT_PORT);

    if (mqttClient.connect(CLIENT_ID, MQTT_USER, MQTT_PASSWORD)) {
        Serial.println("[MQTT] ✅ Conectado");
        mqttClient.subscribe(TOPIC_SUB);
        Serial.printf("[MQTT] Suscrito a: %s\n", TOPIC_SUB);
        // Publicar estado inicial
        publicarEstado(ledEncendido ? "led:1" : "led:0");
        return true;
    } else {
        Serial.printf("[MQTT] ❌ Error: %d\n", mqttClient.state());
        char lastError[100];
        wifiClient.lastError(lastError, 100);
        Serial.printf("[TLS] %s\n", lastError);
        return false;
    }
}

void callbackMQTT(char* topic, byte* payload, unsigned int length) {
    String msg = "";
    for (unsigned int i = 0; i < length; i++) msg += (char)payload[i];
    msg.trim();
    Serial.printf("[MQTT] Recibido [%s]: %s\n", topic, msg.c_str());

    if (String(topic) == TOPIC_SUB) {
        if (msg == "1") {
            setLed(true);
        } else if (msg == "0") {
            setLed(false);
        }
    }
}

void setLed(bool estado, bool publicar) {
    ledEncendido = estado;
    digitalWrite(PIN_LED, estado ? HIGH : LOW);
    Serial.printf("[LED] %s\n", estado ? "Encendido" : "Apagado");
    if (publicar) {
        publicarEstado(estado ? "led:1" : "led:0");
    }
}

void publicarEstado(const char* evento) {
    if (!mqttClient.connected()) return;
    mqttClient.publish(TOPIC_PUB, evento, true);
    Serial.printf("[MQTT] Publicado: %s\n", evento);
}
