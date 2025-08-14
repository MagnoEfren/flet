/*
========================================
PASOS PREVIOS:
========================================
1. Instalar soporte para la placa ESP32:
   - Abrir Arduino IDE.
   - Ir a: File -> Preferences (Archivo -> Preferencias).
   - En el campo "Additional Boards Manager URLs" (Gestor de URLs de tarjetas adicionales) agrega:
        https://dl.espressif.com/dl/package_esp32_index.json
   - Luego ir a: Tools -> Board -> Boards Manager (Herramientas -> Placa -> Gestor de tarjetas)
   - Buscar "ESP32" e instalar "esp32 by Espressif Systems".

2. Instalar librerías necesarias en Arduino IDE:
   - PubSubClient (para MQTT)
   - ArduinoJson (para manejar JSON)
   
   Ir a: Sketch -> Include Library -> Manage Libraries
   Buscar e instalar:
   - "PubSubClient" by Nick O'Leary
   - "ArduinoJson" by Benoit Blanchon

3. Configurar tu red WiFi en las variables WIFI_SSID y WIFI_PASSWORD
*/
/*
========================================
ESP32 MQTT SENSOR CONTROLLER
========================================
Este código permite:
- ENVIAR: 4 valores de sensores (temperatura, humedad, consumo, iluminación)
- RECIBIR: 2 valores booleanos (bool1, bool2) y 2 valores flotantes (float1, float2)
- Comunicación bidireccional vía MQTT usando UN SOLO TOPIC
========================================
*/

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ========================================
// CONFIGURACIÓN DE RED Y MQTT
// ========================================
const char* WIFI_SSID = "MagnoEfren";           // Cambiar por tu red WiFi
const char* WIFI_PASSWORD = "123456789";        // Cambiar por tu contraseña WiFi

const char* MQTT_BROKER = "test.mosquitto.org";
const int MQTT_PORT = 1883;
const char* MQTT_TOPIC = "ESP32/Datos";             // Topic único para enviar y recibir
const char* MQTT_CLIENT_ID = "esp32-sensor-001";

// ========================================
// VARIABLES GLOBALES
// ========================================
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

// Variables para los sensores (valores escalados a rangos reales)
float temperatura = 0.0;    // Rango: 0-40°C
float humedad = 0.0;        // Rango: 0-100%
float consumo = 0.0;        // Rango: 0-2000W
float iluminacion = 0.0;    // Rango: 0-10000 Lux

// Variables para comandos recibidos desde MQTT
bool bool1_received = false;  // Control digital 1
bool bool2_received = false;  // Control digital 2
float float1_received = 0.0;  // Control analógico 1 (0-100)
float float2_received = 0.0;  // Control analógico 2 (0-100)

// Control de tiempo para envío de datos
unsigned long lastSensorRead = 0;
unsigned long lastMqttSend = 0;
const unsigned long SENSOR_INTERVAL = 1000;  // Leer sensores cada 1 segundo
const unsigned long MQTT_INTERVAL = 2000;    // Enviar datos cada 2 segundos

// ========================================
// CONFIGURACIÓN INICIAL
// ========================================
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("🚀 Iniciando ESP32 MQTT Sensor Controller...");
  
  // Configurar pines de entrada y salida
  setupPins();
  
  // Conectar a WiFi
  connectWiFi();
  
  // Configurar servidor MQTT y callback
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setCallback(onMqttMessage);
  
  // Conectar a MQTT
  connectMQTT();
  
  Serial.println("✅ Sistema inicializado correctamente!");
}

// ========================================
// BUCLE PRINCIPAL
// ========================================
void loop() {
  // Mantener conexión MQTT activa
  if (!mqttClient.connected()) {
    connectMQTT();
  }
  mqttClient.loop();
  
  // Leer sensores cada segundo
  if (millis() - lastSensorRead >= SENSOR_INTERVAL) {
    readSensors();
    lastSensorRead = millis();
  }
  
  // Enviar datos por MQTT cada 2 segundos
  if (millis() - lastMqttSend >= MQTT_INTERVAL) {
    sendSensorData();
    lastMqttSend = millis();
  }
  
  // Aplicar comandos recibidos a las salidas
  applyReceivedCommands();
  
  delay(50);  // Pequeña pausa para estabilidad
}

// ========================================
// CONFIGURACIÓN DE PINES
// ========================================
void setupPins() {
  // ========================================
  // PINES DE ENTRADA ANALÓGICA (SENSORES)
  // ========================================
  pinMode(36, INPUT);  // Sensor de temperatura (0-40°C)
  pinMode(39, INPUT);  // Sensor de humedad (0-100%)
  pinMode(34, INPUT);  // Sensor de consumo eléctrico (0-2000W)
  pinMode(35, INPUT);  // Sensor de iluminación (0-10000 Lux)
  
  // ========================================
  // PINES DE SALIDA DIGITAL (CONTROLES BOOLEANOS)
  // ========================================
  pinMode(2, OUTPUT);   // Salida digital 1 (LED integrado)
  pinMode(4, OUTPUT);   // Salida digital 2 (LED/Relé externo)
  
  // ========================================
  // PINES DE SALIDA PWM (CONTROLES ANALÓGICOS)
  // ========================================
  pinMode(18, OUTPUT);  // Salida PWM 1 (Control de velocidad/intensidad)
  pinMode(19, OUTPUT);  // Salida PWM 2 (Control de velocidad/intensidad)
  
  Serial.println("📌 Pines configurados correctamente");
}

// ========================================
// CONEXIÓN WIFI
// ========================================
void connectWiFi() {
  Serial.print("🌐 Conectando a WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println();
  Serial.println("✅ WiFi conectado exitosamente!");
  Serial.print("📍 Dirección IP: ");
  Serial.println(WiFi.localIP());
}

// ========================================
// CONEXIÓN MQTT
// ========================================
void connectMQTT() {
  while (!mqttClient.connected()) {
    Serial.print("🔄 Conectando a broker MQTT...");
    
    if (mqttClient.connect(MQTT_CLIENT_ID)) {
      Serial.println(" ✅ Conectado!");
      
      // Suscribirse al topic único para recibir comandos
      mqttClient.subscribe(MQTT_TOPIC);
      Serial.println("📥 Suscrito a: " + String(MQTT_TOPIC));
      
    } else {
      Serial.print(" ❌ Error de conexión: ");
      Serial.print(mqttClient.state());
      Serial.println(" Reintentando en 5 segundos...");
      delay(5000);
    }
  }
}

// ========================================
// LECTURA DE SENSORES CON ESCALADO
// ========================================
void readSensors() {
  // Leer valores analógicos (0-4095) y escalar a valores reales
  
  // Sensor de temperatura: escalado a 0-40°C con 2 decimales
  int tempRaw = analogRead(36);
  temperatura = map(tempRaw, 0, 4095, 0, 4000) / 100.0;
  
  // Sensor de humedad: escalado a 0-100% con 2 decimales
  int humRaw = analogRead(39);
  humedad = map(humRaw, 0, 4095, 0, 10000) / 100.0;
  
  // Sensor de consumo: escalado a 0-2000W con 2 decimales
  int consumoRaw = analogRead(34);
  consumo = map(consumoRaw, 0, 4095, 0, 200000) / 100.0;
  
  // Sensor de iluminación: escalado a 0-10000 Lux con 2 decimales
  int ilumRaw = analogRead(35);
  iluminacion = map(ilumRaw, 0, 4095, 0, 1000000) / 100.0;
}

// ========================================
// ENVÍO DE DATOS DE SENSORES POR MQTT
// ========================================
void sendSensorData() {
  // Crear objeto JSON con los 4 valores de sensores
  StaticJsonDocument<200> doc;
  
  // Redondear a 2 decimales para mayor precisión
  doc["temperatura"] = round(temperatura * 100) / 100.0;
  doc["humedad"] = round(humedad * 100) / 100.0;
  doc["consumo"] = round(consumo * 100) / 100.0;
  doc["iluminacion"] = round(iluminacion * 100) / 100.0;
  
  // Convertir JSON a string
  String jsonString;
  serializeJson(doc, jsonString);
  
  // Publicar datos en el topic único
  if (mqttClient.publish(MQTT_TOPIC, jsonString.c_str())) {
    Serial.println("📤 Sensores enviados: " + jsonString);
  } else {
    Serial.println("❌ Error al enviar datos de sensores");
  }
}

// ========================================
// CALLBACK PARA MENSAJES MQTT RECIBIDOS
// ========================================
void onMqttMessage(char* topic, byte* payload, unsigned int length) {
  // Convertir payload a string
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  
  Serial.println("📥 Comando recibido: " + message);
  
  // Parsear JSON recibido
  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, message);
  
  if (error) {
    Serial.println("❌ Error al parsear JSON: " + String(error.c_str()));
    return;
  }
  
  // Extraer valores booleanos si están presentes
  if (doc.containsKey("bool1")) {
    bool1_received = doc["bool1"];
    Serial.println("🔴 bool1 actualizado: " + String(bool1_received));
  }
  
  if (doc.containsKey("bool2")) {
    bool2_received = doc["bool2"];
    Serial.println("🔵 bool2 actualizado: " + String(bool2_received));
  }
  
  // Extraer valores flotantes si están presentes
  if (doc.containsKey("float1")) {
    float1_received = doc["float1"];
    Serial.println("📊 float1 actualizado: " + String(float1_received));
  }
  
  if (doc.containsKey("float2")) {
    float2_received = doc["float2"];
    Serial.println("📈 float2 actualizado: " + String(float2_received));
  }
}

// ========================================
// APLICAR COMANDOS RECIBIDOS A LAS SALIDAS
// ========================================
void applyReceivedCommands() {
  // Aplicar valores booleanos a salidas digitales
  digitalWrite(2, bool1_received ? HIGH : LOW);  // Controlar LED/Relé 1
  digitalWrite(4, bool2_received ? HIGH : LOW);  // Controlar LED/Relé 2
  
  // Aplicar valores flotantes a salidas PWM (convertir 0-100 a 0-255)
  if (float1_received >= 0 && float1_received <= 100) {
    int pwm1 = map(float1_received, 0, 100, 0, 255);
    analogWrite(18, pwm1);
  }
  
  if (float2_received >= 0 && float2_received <= 100) {
    int pwm2 = map(float2_received, 0, 100, 0, 255);
    analogWrite(19, pwm2);
  }
}


