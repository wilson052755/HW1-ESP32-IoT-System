#include <ESP8266WiFi.h> // 若使用 ESP32 請換成 <WiFi.h> 及對應函式庫
#include <ESP8266HTTPClient.h> // 實踐 HTTP GET
#include "DHT.h"

// 設定 DHT11 腳位與型號
#define DHTPIN 2       // D4 腳位 (GPIO2)
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// 設定 WiFi SSID 與密碼
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// 設定電腦的區域網路 IP 與 Flask Port
// 請在命令提示字元輸入 ipconfig 取得「IPv4 位址」並填入這裡
const char* serverName = "http://192.168.X.X:5000/addData"; 

// 設定延遲時間 (每 5 秒發送一次)
unsigned long timerDelay = 5000;
unsigned long lastTime = 0;

void setup() {
  Serial.begin(115200);
  dht.begin();
  
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi...");
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to WiFi Network with IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  if ((millis() - lastTime) > timerDelay) {
    if(WiFi.status() == WL_CONNECTED){
      
      float t = dht.readTemperature();
      float h = dht.readHumidity();

      // 確認感測器讀取是否正常
      if (isnan(h) || isnan(t)) {
        Serial.println("Failed to read from DHT sensor!");
        return;
      }
      
      WiFiClient client;
      HTTPClient http;
      
      // 組合 GET 請求 URL (例: http://192.168.X.X:5000/addData?temp=25.5&humid=60.0)
      String serverPath = String(serverName) + "?temp=" + String(t) + "&humid=" + String(h);
      
      http.begin(client, serverPath.c_str());
      
      // 傳送 HTTP GET 請求
      int httpResponseCode = http.GET();
      
      if (httpResponseCode > 0) {
        Serial.print("HTTP Response code: ");
        Serial.println(httpResponseCode);
        String payload = http.getString();
        Serial.println(payload);
      }
      else {
        Serial.print("Error code: ");
        Serial.println(httpResponseCode);
      }
      
      http.end();
    }
    else {
      Serial.println("WiFi Disconnected");
    }
    lastTime = millis();
  }
}
