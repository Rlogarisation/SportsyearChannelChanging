#include <FS.h>                                               // This needs to be first, or it all crashes and burns

#include <IRremoteESP8266.h>
#include <IRsend.h>
#include <IRrecv.h>
#include <IRutils.h>
#include <ESP8266WiFi.h>
#include <WiFiManager.h>                                      // https://github.com/tzapu/WiFiManager WiFi Configuration Magic
#include <ESP8266mDNS.h>                                      // Useful to access to ESP by hostname.local

#include <ArduinoJson.h>
#include <ESP8266WebServer.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266SSDP.h>
#include <ArduinoOTA.h>
#include "sha256.h"

#include <Ticker.h>                                           // For LED status
#include <TimeLib.h>

#include <LittleFS.h>

// User settings are below here
//+=============================================================================
const int timeZone = -5;                                       // Timezone (-5 is EST)

const bool enableMDNSServices = true;                          // Use mDNS services, must be enabled for ArduinoOTA

const unsigned int captureBufSize = 1024;                      // Size of the IR capture buffer.

const bool toggleRC = true;                                    // Toggle RC signals every other transmission

const int pins1 = 4;                                    // Transmitting preset 1
const int configpin = 5;
//+=============================================================================
// User settings are above here

const int ledpin = LED_BUILTIN;                                // Built in LED defined for WEMOS people
const char *wifi_config_name = "IR Controller Configuration";
int port = 80;
char host_name[20] = "";
char port_str[6] = "80";

// Do not modify these values with your own, they are placeholder values that WiFiManager will overwrite
char static_ip[16] = "10.0.1.10";
char static_gw[16] = "10.0.1.1";
char static_sn[16] = "255.255.255.0";
char static_dns[16] = "10.0.1.1";

DynamicJsonDocument deviceState(1024);

WiFiClient client;
ESP8266WebServer *server = NULL;
Ticker ticker;

bool shouldSaveConfig = false;                                 // Flag for saving data
bool holdReceive = false;                                      // Flag to prevent IR receiving while transmitting

IRsend irsend1(pins1);

static const char ntpServerName[] = "time.google.com";
unsigned int localPort = 8888;                                 // Local port to listen for UDP packets
void sendNTPpacket(IPAddress &address);
time_t getNtpTime();
WiFiUDP ntpUDP;

bool _rc5toggle = false;
bool _rc6toggle = false;

char _ip[16] = "";

class Code {
public:
    char encoding[14] = "";
    char address[20] = "";
    char command[40] = "";
    char data[40] = "";
    String raw = "";
    int bits = 0;
    time_t timestamp = 0;
    bool valid = false;
};

// Declare prototypes
void sendCodePage(Code selCode);
void sendCodePage(Code selCode, int httpcode);
String GetPowerCode(String type);
String GetLowerVolumeCode(String type);
String GetRaiseVolumeCode(String type);
String GetMuteCode(String type);
String GetCodeFromNumber(char channel, String type);
String GetRaiseChannelCode(String type);
String GetLowerChannelCode(String type);
void irblastlong(String type, String dataStr, int dataStrLen, unsigned int len, int rdelay, int pulse, int pdelay, int repeat, long address, IRsend irsend);

//+=============================================================================
// Callback notifying us of the need to save config
//
void saveConfigCallback () {
    Serial.println("Should save config");
    shouldSaveConfig = true;
}

//+=============================================================================
// EPOCH time to String
//
String epochToString(time_t timenow) {
    unsigned long hours = (timenow % 86400L) / 3600;
    String hourStr = hours < 10 ? "0" + String(hours) : String(hours);

    unsigned long minutes = (timenow % 3600) / 60;
    String minuteStr = minutes < 10 ? "0" + String(minutes) : String(minutes);

    unsigned long seconds = (timenow % 60);
    String secondStr = seconds < 10 ? "0" + String(seconds) : String(seconds);
    return hourStr + ":" + minuteStr + ":" + secondStr;
}

//+=============================================================================
// Toggle state
//
void tick() {
    int state = digitalRead(ledpin);  // get the current state of GPIO1 pin
    digitalWrite(ledpin, !state);     // set pin to the opposite state
}

//+=============================================================================
// Turn off the Led after timeout
//
void disableLed() {
    Serial.println("Turning off the LED to save power.");
    digitalWrite(ledpin, HIGH);                           // Shut down the LED
    ticker.detach();                                      // Stopping the ticker
}

//+=============================================================================
// Gets called when WiFiManager enters configuration mode
//
void configModeCallback (WiFiManager *myWiFiManager) {
    Serial.println("Entered config mode");
    Serial.println(WiFi.softAPIP());
    //if you used auto generated SSID, print it
    Serial.println(myWiFiManager->getConfigPortalSSID());
    //entered config mode, make led toggle faster
    ticker.attach(0.2, tick);
}

//+=============================================================================
// Gets called when device loses connection to the accesspoint
//
void lostWifiCallback (const WiFiEventStationModeDisconnected& evt) {
    Serial.println("Lost Wifi");
    // reset and try again, or maybe put it to deep sleep
    ESP.reset();
    delay(1000);
}

//+=============================================================================
// First setup of the Wifi.
// If return true, the Wifi is well connected.
// Should not return false if Wifi cannot be connected, it will loop
//
bool setupWifi(bool resetConf) {
    // start ticker with 0.5 because we start in AP mode and try to connect
    ticker.attach(0.5, tick);

    WiFi.mode(WIFI_STA); // To make sure STA mode is preserved by WiFiManager and resets it after config is done.

    // WiFiManager
    // Local intialization. Once its business is done, there is no need to keep it around
    WiFiManager wifiManager;

    // set callback that gets called when connecting to previous WiFi fails, and enters Access Point mode
    wifiManager.setAPCallback(configModeCallback);
    // set config save notify callback
    wifiManager.setSaveConfigCallback(saveConfigCallback);

    // Reset device if on config portal for greater than 3 minutes
    wifiManager.setConfigPortalTimeout(180);

    if (LittleFS.begin()) {
        Serial.println("mounted file system");
        if (LittleFS.exists("/config.json")) {
            //file exists, reading and loading
            Serial.println("reading config file");
            File configFile = LittleFS.open("/config.json", "r");
            if (configFile) {
                Serial.println("opened config file");
                size_t size = configFile.size();
                // Allocate a buffer to store contents of the file.
                std::unique_ptr<char[]> buf(new char[size]);

                configFile.readBytes(buf.get(), size);
                DynamicJsonDocument json(1024);
                DeserializationError error = deserializeJson(json, buf.get());
                serializeJson(json, Serial);
                if (!error) {
                    Serial.println("\nparsed json");

                    if (json.containsKey("hostname")) strncpy(host_name, json["hostname"], 20);
                    if (json.containsKey("port_str")) {
                        strncpy(port_str, json["port_str"], 6);
                        port = atoi(json["port_str"]);
                    }
                    if (json.containsKey("ip")) strncpy(static_ip, json["ip"], 16);
                    if (json.containsKey("gw")) strncpy(static_gw, json["gw"], 16);
                    if (json.containsKey("sn")) strncpy(static_sn, json["sn"], 16);
                    if (json.containsKey("dns")) strncpy(static_dns, json["dns"], 16);
                } else {
                    Serial.println("failed to load json config");
                }
            }
        }
    } else {
        Serial.println("failed to mount FS");
    }

    WiFiManagerParameter custom_hostname("hostname", "Choose a hostname to this IR Controller", host_name, 20);
    wifiManager.addParameter(&custom_hostname);
    WiFiManagerParameter custom_port("port_str", "Choose a port", port_str, 6);
    wifiManager.addParameter(&custom_port);

    wifiManager.setShowStaticFields(true);
    wifiManager.setShowDnsFields(true);

    IPAddress sip, sgw, ssn, dns;
    sip.fromString(static_ip);
    sgw.fromString(static_gw);
    ssn.fromString(static_sn);
    dns.fromString(static_dns);

    if (resetConf) {
        Serial.println("Reset triggered, launching in AP mode");
        wifiManager.startConfigPortal(wifi_config_name);
    } else {
        Serial.println("Setting static WiFi data from config");
        wifiManager.setSTAStaticIPConfig(sip, sgw, ssn, dns);
    }

    // fetches ssid and pass and tries to connect
    // if it does not connect it starts an access point with the specified name
    // and goes into a blocking loop awaiting configuration
    if (!wifiManager.autoConnect(wifi_config_name)) {
        Serial.println("Failed to connect and hit timeout");
        // reset and try again, or maybe put it to deep sleep
        ESP.reset();
        delay(1000);
    }

    // if you get here you have connected to the WiFi
    strncpy(host_name, custom_hostname.getValue(), 20);
    strncpy(port_str, custom_port.getValue(), 6);
    port = atoi(port_str);

    if (server != NULL) {
        delete server;
    }
    server = new ESP8266WebServer(port);

    // Reset device if lost wifi Connection
    WiFi.onStationModeDisconnected(&lostWifiCallback);

    Serial.println("WiFi connected! User chose hostname '" + String(host_name) + "' and port '" + String(port_str) + "'");

    // Save the custom parameters to FS
    if (shouldSaveConfig) {
        Serial.println(" config...");
        DynamicJsonDocument json(1024);
        json["hostname"] = host_name;
        json["port_str"] = port_str;
        json["ip"] = WiFi.localIP().toString();
        json["gw"] = WiFi.gatewayIP().toString();
        json["sn"] = WiFi.subnetMask().toString();
        json["dns"] = WiFi.dnsIP().toString();

        File configFile = LittleFS.open("/config.json", "w");
        if (!configFile) {
            Serial.println("failed to open config file for writing");
        }

        serializeJson(json, Serial);
        Serial.println("");
        Serial.println("Writing config file");
        serializeJson(json, configFile);
        configFile.close();
        json.clear();
        Serial.println("Config written successfully");
    }
    ticker.detach();

    // keep LED on
    digitalWrite(ledpin, LOW);
    return true;
}

//+=============================================================================
// Send CORS HTTP headers
//
void sendCorsHeaders() {
    server->sendHeader("Access-Control-Allow-Origin", "*");
    server->sendHeader("Access-Control-Allow-Methods", "GET, POST");
}

//+=============================================================================
// Setup web server and IR receiver/blaster
//
void setup() {
    // Initialize serial
    Serial.begin(115200);

    // set led pin as output
    pinMode(ledpin, OUTPUT);

    Serial.println("");
    Serial.println("ESP8266 IR Controller");
    pinMode(configpin, INPUT_PULLUP);
    Serial.print("Config pin GPIO");
    Serial.print(configpin);
    Serial.print(" set to: ");
    Serial.println(digitalRead(configpin));
    if (!setupWifi(digitalRead(configpin) == LOW))
        return;

    Serial.println("WiFi configuration complete");

    if (strlen(host_name) > 0) {
        WiFi.hostname(host_name);
    } else {
        WiFi.hostname().toCharArray(host_name, 20);
    }

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    wifi_set_sleep_type(LIGHT_SLEEP_T);
    digitalWrite(ledpin, LOW);
    // Turn off the led in 2s
    ticker.attach(2, disableLed);

    Serial.print("Local IP: ");
    Serial.println(WiFi.localIP().toString());
    Serial.print("DNS IP: ");
    Serial.println(WiFi.dnsIP().toString());
    Serial.println("URL to send commands: http://" + String(host_name) + ".local:" + port_str);

    if (enableMDNSServices) {
        // Configure OTA Update
        ArduinoOTA.setPort(8266);
        ArduinoOTA.setHostname(host_name);
        ArduinoOTA.onStart([]() {
            Serial.println("Start");
        });
        ArduinoOTA.onEnd([]() {
            Serial.println("\nEnd");
        });
        ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
            Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
        });
        ArduinoOTA.onError([](ota_error_t error) {
            Serial.printf("Error[%u]: ", error);
            if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
            else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
            else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
            else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
            else if (error == OTA_END_ERROR) Serial.println("End Failed");
        });
        ArduinoOTA.begin();
        Serial.println("ArduinoOTA started");

        // Configure mDNS
        MDNS.addService("http", "tcp", port); // Announce the ESP as an HTTP service
        Serial.println("MDNS http service added. Hostname is set to " + String(host_name) + ".local:" + String(port));
    }

    // Configure the server
    server->on("/json", []() { // JSON handler for more complicated IR blaster routines
        Serial.println("Connection received endpoint '/json'");

        int simple = 0;
        if (server->hasArg("simple")) simple = server->arg("simple").toInt();
        String signature = server->arg("auth");
        String epid = server->arg("epid");
        String mid = server->arg("mid");
        String timestamp = server->arg("time");

        DynamicJsonDocument root(4096);
        DeserializationError error = deserializeJson(root, server->arg("plain"));
        int out = (server->hasArg("out")) ? server->arg("out").toInt() : 1;
        if (error) {
            Serial.println("JSON parsing failed");
            Serial.println(error.c_str());
            if (simple) {
            sendCorsHeaders();
            server->send(400, "text/plain", "JSON parsing failed, " + String(error.c_str()));
            } else {
            sendHomePage("JSON parsing failed", "Error", 3, 400); // 400
            }
            root.clear();
        } else {
            digitalWrite(ledpin, LOW);
            ticker.attach(0.5, disableLed);

            // Handle device state limitations for the global JSON command request
            if (server->hasArg("device")) {
                String device = server->arg("device");
                Serial.println("Device name detected " + device);
                int state = (server->hasArg("state")) ? server->arg("state").toInt() : 0;
                if (deviceState.containsKey(device)) {
                    Serial.println("Contains the key!");
                    Serial.println(state);
                    int currentState = deviceState[device];
                    Serial.println(currentState);
                    if (state == currentState) {
                        if (simple) {
                            sendCorsHeaders();
                            server->send(200, "text/html", "Not sending command to " + device + ", already in state " + state);
                        } else {
                            sendHomePage("Not sending command to " + device + ", already in state " + state, "Warning", 2); // 200
                        }
                        Serial.println("Not sending command to " + device + ", already in state " + state);
                        return;
                    } else {
                        Serial.println("Setting device " + device + " to state " + state);
                        deviceState[device] = state;
                    }
                } else {
                    Serial.println("Setting device " + device + " to state " + state);
                    deviceState[device] = state;
                }
            }

            if (simple) {
                sendCorsHeaders();
                server->send(200, "text/html", "Success, code sent");
            }

            String message = "Code sent";

            for (size_t x = 0; x < root.size(); x++) {
                String type = root[x]["type"];
                String ip = root[x]["ip"];
                int rdelay = root[x]["rdelay"];
                int pulse = root[x]["pulse"];
                int pdelay = root[x]["pdelay"];
                int repeat = root[x]["repeat"];
                int xout = root[x]["out"];
                if (xout == 0) {
                    xout = out;
                }
                int duty = root[x]["duty"];

                if (pulse <= 0) pulse = 1; // Make sure pulse isn't 0
                if (repeat <= 0) repeat = 1; // Make sure repeat isn't 0
                if (pdelay <= 0) pdelay = 100; // Default pdelay
                if (rdelay <= 0) rdelay = 1000; // Default rdelay
                if (duty <= 0) duty = 50; // Default duty

                // Handle device state limitations on a per JSON object basis
                String device = root[x]["device"];
                if (device != "null") {
                    int state = root[x]["state"];
                    if (deviceState.containsKey(device)) {
                        int currentState = deviceState[device];
                        if (state == currentState) {
                            Serial.println("Not sending command to " + device + ", already in state " + state);
                            message = "Code sent. Some components of the code were held because device was already in appropriate state";
                            continue;
                        } else {
                            Serial.println("Setting device " + device + " to state " + state);
                            deviceState[device] = state;
                        }
                    } else {
                        Serial.println("Setting device " + device + " to state " + state);
                        deviceState[device] = state;
                    }
                }

                if (type == "delay") {
                    delay(rdelay);
                } else if (type == "raw") {
                    JsonArray raw = root[x]["data"]; // Array of unsigned int values for the raw signal
                    int khz = root[x]["khz"];
                    if (khz <= 0) khz = 38; // Default to 38khz if not set
                    rawblast(raw, khz, rdelay, pulse, pdelay, repeat, pickIRsend(xout),duty);
                } else {
                    String data = root[x]["data"];
                    String addressString = root[x]["address"];
                    long address = strtoul(addressString.c_str(), 0, 0);
                    int len = root[x]["length"];
                    irblast(type, data, len, rdelay, pulse, pdelay, repeat, address, pickIRsend(xout));
                }
            }

            if (!simple) {
                Serial.println("Sending home page");
                sendHomePage(message, "Success", 1); // 200
            }
            root.clear();
        }
    });
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////WEBSERVER ROUTES ////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // Power route
    server->on("/ir/power", []() {
        Serial.println("Connection received endpoint '/ir/power'");

        int simple = 0;
        if (server->hasArg("simple")) simple = server->arg("simple").toInt();
        String signature = server->arg("auth");
        String epid = server->arg("epid");
        String mid = server->arg("mid");
        String timestamp = server->arg("time");

        digitalWrite(ledpin, LOW);
        ticker.attach(0.5, disableLed);
        String type = server->arg("type");
        String data = server->arg("data");
        String ip = server->arg("ip");

        // Handle device state limitations
        if (server->hasArg("device")) {
            String device = server->arg("device");
            Serial.println("Device name detected " + device);
            int state = (server->hasArg("state")) ? server->arg("state").toInt() : 0;
            if (deviceState.containsKey(device)) {
                Serial.println("Contains the key!");
                Serial.println(state);
                int currentState = deviceState[device];
                Serial.println(currentState);
                if (state == currentState) {
                    if (simple) {
                        sendCorsHeaders();
                        server->send(200, "text/html", "Not sending command to " + device + ", already in state " + state);
                    } else {
                        sendHomePage("Not sending command to " + device + ", already in state " + state, "Warning", 2); // 200
                    }
                    Serial.println("Not sending command to " + device + ", already in state " + state);
                    return;
                } else {
                    Serial.println("Setting device " + device + " to state " + state);
                    deviceState[device] = state;
                }
            } else {
                Serial.println("Setting device " + device + " to state " + state);
                deviceState[device] = state;
            }
        }

        int len = server->arg("length").toInt();
        long address = 0;
        if (server->hasArg("address")) {
            String addressString = server->arg("address");
            address = strtoul(addressString.c_str(), 0, 0);
        }

        int rdelay = (server->hasArg("rdelay")) ? server->arg("rdelay").toInt() : 1000;
        int pulse = (server->hasArg("pulse")) ? server->arg("pulse").toInt() : 1;
        int pdelay = (server->hasArg("pdelay")) ? server->arg("pdelay").toInt() : 100;
        int repeat = (server->hasArg("repeat")) ? server->arg("repeat").toInt() : 1;
        int out = (server->hasArg("out")) ? server->arg("out").toInt() : 1;

        if (server->hasArg("type")) {
            String type = server->arg("type");
            if (server->hasArg("length")) {
                len = server->arg("length").toInt();
            } else {
                len = 32;
            }
            String code = GetPowerCode(type);
            irblast(type, code, len, rdelay, pulse, pdelay, repeat, address, pickIRsend(out));
        }

        if (simple) {
            sendCorsHeaders();
            server->send(200, "text/html", "Success, code sent");
        }

        if (!simple) {
            sendHomePage("Code Sent", "Success", 1); // 200
        }
    });

    // Volume down route
    server->on("/ir/lower_volume", []() {
        Serial.println("Connection received endpoint '/ir/lower_volume'");

        int simple = 0;
        if (server->hasArg("simple")) simple = server->arg("simple").toInt();
        String signature = server->arg("auth");
        String epid = server->arg("epid");
        String mid = server->arg("mid");
        String timestamp = server->arg("time");

        digitalWrite(ledpin, LOW);
        ticker.attach(0.5, disableLed);
        String type = server->arg("type");
        String data = server->arg("data");
        String ip = server->arg("ip");

        // Handle device state limitations
        if (server->hasArg("device")) {
            String device = server->arg("device");
            Serial.println("Device name detected " + device);
            int state = (server->hasArg("state")) ? server->arg("state").toInt() : 0;
            if (deviceState.containsKey(device)) {
                Serial.println("Contains the key!");
                Serial.println(state);
                int currentState = deviceState[device];
                Serial.println(currentState);
                if (state == currentState) {
                    if (simple) {
                        sendCorsHeaders();
                        server->send(200, "text/html", "Not sending command to " + device + ", already in state " + state);
                    } else {
                        sendHomePage("Not sending command to " + device + ", already in state " + state, "Warning", 2); // 200
                    }
                    Serial.println("Not sending command to " + device + ", already in state " + state);
                    return;
                } else {
                    Serial.println("Setting device " + device + " to state " + state);
                    deviceState[device] = state;
                }
            } else {
                Serial.println("Setting device " + device + " to state " + state);
                deviceState[device] = state;
            }
        }

        int len = server->arg("length").toInt();
        long address = 0;
        if (server->hasArg("address")) {
            String addressString = server->arg("address");
            address = strtoul(addressString.c_str(), 0, 0);
        }

        int rdelay = (server->hasArg("rdelay")) ? server->arg("rdelay").toInt() : 1000;
        int pulse = (server->hasArg("pulse")) ? server->arg("pulse").toInt() : 1;
        int pdelay = (server->hasArg("pdelay")) ? server->arg("pdelay").toInt() : 100;
        int repeat = (server->hasArg("repeat")) ? server->arg("repeat").toInt() : 1;
        int out = (server->hasArg("out")) ? server->arg("out").toInt() : 1;

        if (server->hasArg("type")) {
            String type = server->arg("type");
            if (server->hasArg("length")) {
                len = server->arg("length").toInt();
            } else {
                len = 32;
            }
            String code = GetLowerVolumeCode(type);
            irblast(type, code, len, rdelay, pulse, pdelay, repeat, address, pickIRsend(out));
        }

        if (simple) {
            sendCorsHeaders();
            server->send(200, "text/html", "Success, code sent");
        }

        if (!simple) {
            sendHomePage("Code Sent", "Success", 1); // 200
        }
    });

    // Volume up route
    server->on("/ir/raise_volume", []() {
        Serial.println("Connection received endpoint '/ir/raise_volume'");

        int simple = 0;
        if (server->hasArg("simple")) simple = server->arg("simple").toInt();
        String signature = server->arg("auth");
        String epid = server->arg("epid");
        String mid = server->arg("mid");
        String timestamp = server->arg("time");

        digitalWrite(ledpin, LOW);
        ticker.attach(0.5, disableLed);
        String type = server->arg("type");
        String data = server->arg("data");
        String ip = server->arg("ip");

        // Handle device state limitations
        if (server->hasArg("device")) {
            String device = server->arg("device");
            Serial.println("Device name detected " + device);
            int state = (server->hasArg("state")) ? server->arg("state").toInt() : 0;
            if (deviceState.containsKey(device)) {
                Serial.println("Contains the key!");
                Serial.println(state);
                int currentState = deviceState[device];
                Serial.println(currentState);
                if (state == currentState) {
                    if (simple) {
                        sendCorsHeaders();
                        server->send(200, "text/html", "Not sending command to " + device + ", already in state " + state);
                    } else {
                        sendHomePage("Not sending command to " + device + ", already in state " + state, "Warning", 2); // 200
                    }
                    Serial.println("Not sending command to " + device + ", already in state " + state);
                    return;
                } else {
                    Serial.println("Setting device " + device + " to state " + state);
                    deviceState[device] = state;
                }
            } else {
                Serial.println("Setting device " + device + " to state " + state);
                deviceState[device] = state;
            }
        }

        int len = server->arg("length").toInt();
        long address = 0;
        if (server->hasArg("address")) {
            String addressString = server->arg("address");
            address = strtoul(addressString.c_str(), 0, 0);
        }

        int rdelay = (server->hasArg("rdelay")) ? server->arg("rdelay").toInt() : 1000;
        int pulse = (server->hasArg("pulse")) ? server->arg("pulse").toInt() : 1;
        int pdelay = (server->hasArg("pdelay")) ? server->arg("pdelay").toInt() : 100;
        int repeat = (server->hasArg("repeat")) ? server->arg("repeat").toInt() : 1;
        int out = (server->hasArg("out")) ? server->arg("out").toInt() : 1;

        if (server->hasArg("type")) {
            String type = server->arg("type");
            if (server->hasArg("length")) {
                len = server->arg("length").toInt();
            } else {
                len = 32;
            }
            String code = GetRaiseVolumeCode(type);
            irblast(type, code, len, rdelay, pulse, pdelay, repeat, address, pickIRsend(out));
        }

        if (simple) {
            sendCorsHeaders();
            server->send(200, "text/html", "Success, code sent");
        }

        if (!simple) {
            sendHomePage("Code Sent", "Success", 1); // 200
        }
    });

    // Mute route
    server->on("/ir/mute", []() {
        Serial.println("Connection received endpoint '/ir/mute'");

        int simple = 0;
        if (server->hasArg("simple")) simple = server->arg("simple").toInt();
        String signature = server->arg("auth");
        String epid = server->arg("epid");
        String mid = server->arg("mid");
        String timestamp = server->arg("time");

        digitalWrite(ledpin, LOW);
        ticker.attach(0.5, disableLed);
        String type = server->arg("type");
        String data = server->arg("data");
        String ip = server->arg("ip");

        // Handle device state limitations
        if (server->hasArg("device")) {
            String device = server->arg("device");
            Serial.println("Device name detected " + device);
            int state = (server->hasArg("state")) ? server->arg("state").toInt() : 0;
            if (deviceState.containsKey(device)) {
                Serial.println("Contains the key!");
                Serial.println(state);
                int currentState = deviceState[device];
                Serial.println(currentState);
                if (state == currentState) {
                    if (simple) {
                        sendCorsHeaders();
                        server->send(200, "text/html", "Not sending command to " + device + ", already in state " + state);
                    } else {
                        sendHomePage("Not sending command to " + device + ", already in state " + state, "Warning", 2); // 200
                    }
                    Serial.println("Not sending command to " + device + ", already in state " + state);
                    return;
                } else {
                    Serial.println("Setting device " + device + " to state " + state);
                    deviceState[device] = state;
                }
            } else {
                Serial.println("Setting device " + device + " to state " + state);
                deviceState[device] = state;
            }
        }

        int len = server->arg("length").toInt();
        long address = 0;
        if (server->hasArg("address")) {
            String addressString = server->arg("address");
            address = strtoul(addressString.c_str(), 0, 0);
        }

        int rdelay = (server->hasArg("rdelay")) ? server->arg("rdelay").toInt() : 1000;
        int pulse = (server->hasArg("pulse")) ? server->arg("pulse").toInt() : 1;
        int pdelay = (server->hasArg("pdelay")) ? server->arg("pdelay").toInt() : 100;
        int repeat = (server->hasArg("repeat")) ? server->arg("repeat").toInt() : 1;
        int out = (server->hasArg("out")) ? server->arg("out").toInt() : 1;

        if (server->hasArg("type")) {
            String type = server->arg("type");
            if (server->hasArg("length")) {
                len = server->arg("length").toInt();
            } else {
                len = 32;
            }
            String code = GetMuteCode(type);
            irblast(type, code, len, rdelay, pulse, pdelay, repeat, address, pickIRsend(out));
        }

        if (simple) {
            sendCorsHeaders();
            server->send(200, "text/html", "Success, code sent");
        }

        if (!simple) {
            sendHomePage("Code Sent", "Success", 1); // 200
        }
    });

    // set_channel route
    server->on("/ir/set_channel", []() {
        Serial.println("Connection received endpoint '/ir/set_channel'");

        int simple = 0;
        if (server->hasArg("simple")) simple = server->arg("simple").toInt();
        String signature = server->arg("auth");
        String epid = server->arg("epid");
        String mid = server->arg("mid");
        String timestamp = server->arg("time");

        digitalWrite(ledpin, LOW);
        ticker.attach(0.5, disableLed);
        String type = server->arg("type");
        String data = server->arg("data");
        String ip = server->arg("ip");

        // Handle device state limitations
        if (server->hasArg("device")) {
            String device = server->arg("device");
            Serial.println("Device name detected " + device);
            int state = (server->hasArg("state")) ? server->arg("state").toInt() : 0;
            if (deviceState.containsKey(device)) {
                Serial.println("Contains the key!");
                Serial.println(state);
                int currentState = deviceState[device];
                Serial.println(currentState);
                if (state == currentState) {
                    if (simple) {
                        sendCorsHeaders();
                        server->send(200, "text/html", "Not sending command to " + device + ", already in state " + state);
                    } else {
                        sendHomePage("Not sending command to " + device + ", already in state " + state, "Warning", 2); // 200
                    }
                    Serial.println("Not sending command to " + device + ", already in state " + state);
                    return;
                } else {
                    Serial.println("Setting device " + device + " to state " + state);
                    deviceState[device] = state;
                }
            } else {
                Serial.println("Setting device " + device + " to state " + state);
                deviceState[device] = state;
            }
        }

        int len = server->arg("length").toInt();
        long address = 0;
        if (server->hasArg("address")) {
            String addressString = server->arg("address");
            address = strtoul(addressString.c_str(), 0, 0);
        }

        int rdelay = (server->hasArg("rdelay")) ? server->arg("rdelay").toInt() : 1000;
        int pulse = (server->hasArg("pulse")) ? server->arg("pulse").toInt() : 1;
        int pdelay = (server->hasArg("pdelay")) ? server->arg("pdelay").toInt() : 100;
        int repeat = (server->hasArg("repeat")) ? server->arg("repeat").toInt() : 1;
        int out = (server->hasArg("out")) ? server->arg("out").toInt() : 1;
        if (server->hasArg("channel")) {
            String channel = server->arg("channel");
            if (server->hasArg("length")) {
                len = server->arg("length").toInt();
            } else {
                len = 32;
            }
            int expectedChannelLength = channel.length();
            irblastlong(type, channel, expectedChannelLength, len, rdelay, pulse, pdelay, repeat, address, pickIRsend(out));
        }

        if (simple) {
            sendCorsHeaders();
            server->send(200, "text/html", "Success, code sent");
        }

        if (!simple) {
            sendHomePage("Code Sent", "Success", 1); // 200
        }
    });

    // Raise channel by 1
    server->on("/ir/raise_channel", []() {
        Serial.println("Connection received endpoint '/ir/raise_channel'");

        int simple = 0;
        if (server->hasArg("simple")) simple = server->arg("simple").toInt();
        String signature = server->arg("auth");
        String epid = server->arg("epid");
        String mid = server->arg("mid");
        String timestamp = server->arg("time");

        digitalWrite(ledpin, LOW);
        ticker.attach(0.5, disableLed);
        String type = server->arg("type");
        String data = server->arg("data");
        String ip = server->arg("ip");

        // Handle device state limitations
        if (server->hasArg("device")) {
            String device = server->arg("device");
            Serial.println("Device name detected " + device);
            int state = (server->hasArg("state")) ? server->arg("state").toInt() : 0;
            if (deviceState.containsKey(device)) {
                Serial.println("Contains the key!");
                Serial.println(state);
                int currentState = deviceState[device];
                Serial.println(currentState);
                if (state == currentState) {
                    if (simple) {
                        sendCorsHeaders();
                        server->send(200, "text/html", "Not sending command to " + device + ", already in state " + state);
                    } else {
                        sendHomePage("Not sending command to " + device + ", already in state " + state, "Warning", 2); // 200
                    }
                    Serial.println("Not sending command to " + device + ", already in state " + state);
                    return;
                } else {
                    Serial.println("Setting device " + device + " to state " + state);
                    deviceState[device] = state;
                }
            } else {
                Serial.println("Setting device " + device + " to state " + state);
                deviceState[device] = state;
            }
        }

        int len = server->arg("length").toInt();
        long address = 0;
        if (server->hasArg("address")) {
            String addressString = server->arg("address");
            address = strtoul(addressString.c_str(), 0, 0);
        }

        int rdelay = (server->hasArg("rdelay")) ? server->arg("rdelay").toInt() : 1000;
        int pulse = (server->hasArg("pulse")) ? server->arg("pulse").toInt() : 1;
        int pdelay = (server->hasArg("pdelay")) ? server->arg("pdelay").toInt() : 100;
        int repeat = (server->hasArg("repeat")) ? server->arg("repeat").toInt() : 1;
        int out = (server->hasArg("out")) ? server->arg("out").toInt() : 1;

        if (server->hasArg("type")) {
            String type = server->arg("type");
            if (server->hasArg("length")) {
                len = server->arg("length").toInt();
            } else {
                len = 32;
            }
            String code = GetRaiseChannelCode(type);
            irblast(type, code, len, rdelay, pulse, pdelay, repeat, address, pickIRsend(out));
        }

        if (simple) {
            sendCorsHeaders();
            server->send(200, "text/html", "Success, code sent");
        }

        if (!simple) {
            sendHomePage("Code Sent", "Success", 1); // 200
        }
    });

    // Lower channel by 1
    server->on("/ir/lower_channel", []() {
        Serial.println("Connection received endpoint '/ir/lower_channel'");

        int simple = 0;
        if (server->hasArg("simple")) simple = server->arg("simple").toInt();
        String signature = server->arg("auth");
        String epid = server->arg("epid");
        String mid = server->arg("mid");
        String timestamp = server->arg("time");

        digitalWrite(ledpin, LOW);
        ticker.attach(0.5, disableLed);
        String type = server->arg("type");
        String data = server->arg("data");
        String ip = server->arg("ip");

        // Handle device state limitations
        if (server->hasArg("device")) {
            String device = server->arg("device");
            Serial.println("Device name detected " + device);
            int state = (server->hasArg("state")) ? server->arg("state").toInt() : 0;
            if (deviceState.containsKey(device)) {
                Serial.println("Contains the key!");
                Serial.println(state);
                int currentState = deviceState[device];
                Serial.println(currentState);
                if (state == currentState) {
                    if (simple) {
                        sendCorsHeaders();
                        server->send(200, "text/html", "Not sending command to " + device + ", already in state " + state);
                    } else {
                        sendHomePage("Not sending command to " + device + ", already in state " + state, "Warning", 2); // 200
                    }
                    Serial.println("Not sending command to " + device + ", already in state " + state);
                    return;
                } else {
                    Serial.println("Setting device " + device + " to state " + state);
                    deviceState[device] = state;
                }
            } else {
                Serial.println("Setting device " + device + " to state " + state);
                deviceState[device] = state;
            }
        }

        int len = server->arg("length").toInt();
        long address = 0;
        if (server->hasArg("address")) {
            String addressString = server->arg("address");
            address = strtoul(addressString.c_str(), 0, 0);
        }

        int rdelay = (server->hasArg("rdelay")) ? server->arg("rdelay").toInt() : 1000;
        int pulse = (server->hasArg("pulse")) ? server->arg("pulse").toInt() : 1;
        int pdelay = (server->hasArg("pdelay")) ? server->arg("pdelay").toInt() : 100;
        int repeat = (server->hasArg("repeat")) ? server->arg("repeat").toInt() : 1;
        int out = (server->hasArg("out")) ? server->arg("out").toInt() : 1;

        if (server->hasArg("type")) {
            String type = server->arg("type");
            if (server->hasArg("length")) {
                len = server->arg("length").toInt();
            } else {
                len = 32;
            }
            String code = GetLowerChannelCode(type);
            irblast(type, code, len, rdelay, pulse, pdelay, repeat, address, pickIRsend(out));
        }

        if (simple) {
            sendCorsHeaders();
            server->send(200, "text/html", "Success, code sent");
        }

        if (!simple) {
            sendHomePage("Code Sent", "Success", 1); // 200
        }
    });

    server->on("/", []() {
        Serial.println("Connection received endpoint '/'");
        String signature = server->arg("auth");
        String epid = server->arg("epid");
        String mid = server->arg("mid");
        String timestamp = server->arg("time");

        sendHomePage(); // 200
    });

    server->begin();
    Serial.println("HTTP Server started on port " + String(port));
    // Enable SSDP discoverability
    server->on("/description.xml", []() {
        SSDP.schema(server->client());

    });
    SSDP.setSchemaURL("description.xml");
    SSDP.setHTTPPort(port);
    SSDP.setName(String(host_name));
    SSDP.setModelName("esp8266 "+String(host_name));
    SSDP.setURL("/");
    SSDP.begin();
    SSDP.setDeviceType("upnp:rootdevice");
    Serial.println("Starting UDP");
    ntpUDP.begin(localPort);
    Serial.print("Local port: ");
    Serial.println(ntpUDP.localPort());
    Serial.println("Waiting for sync");
    setSyncProvider(getNtpTime);
    setSyncInterval(300);

    irsend1.begin();
    Serial.println("Ready to send and receive IR signals");
}

//+=============================================================================
// NTP Code
//
const int NTP_PACKET_SIZE = 48; // NTP time is in the first 48 bytes of message
byte packetBuffer[NTP_PACKET_SIZE]; //buffer to hold incoming & outgoing packets

time_t getNtpTime() {
    IPAddress ntpServerIP; // NTP server's ip address

    while (ntpUDP.parsePacket() > 0) ; // discard any previously received packets
    Serial.println("Transmit NTP Request");
    // get a random server from the pool
    WiFi.hostByName(ntpServerName, ntpServerIP);
    Serial.print(ntpServerName);
    Serial.print(": ");
    Serial.println(ntpServerIP);
    sendNTPpacket(ntpServerIP);
    uint32_t beginWait = millis();
    while (millis() - beginWait < 1500) {
        int size = ntpUDP.parsePacket();
        if (size >= NTP_PACKET_SIZE) {
        Serial.println("Receive NTP Response");
        ntpUDP.read(packetBuffer, NTP_PACKET_SIZE);  // read packet into the buffer
        unsigned long secsSince1900;
        // convert four bytes starting at location 40 to a long integer
        secsSince1900 =  (unsigned long)packetBuffer[40] << 24;
        secsSince1900 |= (unsigned long)packetBuffer[41] << 16;
        secsSince1900 |= (unsigned long)packetBuffer[42] << 8;
        secsSince1900 |= (unsigned long)packetBuffer[43];
        return secsSince1900 - 2208988800UL + timeZone * SECS_PER_HOUR;
        }
    }
    Serial.println("No NTP Response :-(");
    return 0; // return 0 if unable to get the time
}

//+=============================================================================
// Send an NTP request to the time server at the given address
//
void sendNTPpacket(IPAddress &address) {
    // set all bytes in the buffer to 0
    memset(packetBuffer, 0, NTP_PACKET_SIZE);
    // Initialize values needed to form NTP request
    // (see URL above for details on the packets)
    packetBuffer[0] = 0b11100011;   // LI, Version, Mode
    packetBuffer[1] = 0;     // Stratum, or type of clock
    packetBuffer[2] = 6;     // Polling Interval
    packetBuffer[3] = 0xEC;  // Peer Clock Precision
    // 8 bytes of zero for Root Delay & Root Dispersion
    packetBuffer[12] = 49;
    packetBuffer[13] = 0x4E;
    packetBuffer[14] = 49;
    packetBuffer[15] = 52;
    // all NTP fields have been given values, now
    // you can send a packet requesting a timestamp:
    ntpUDP.beginPacket(address, 123); //NTP requests are to port 123
    ntpUDP.write(packetBuffer, NTP_PACKET_SIZE);
    ntpUDP.endPacket();
}

//+=============================================================================
// Split string by character
//
String getValue(String data, char separator, int index)
{
    int found = 0;
    int strIndex[] = {0, -1};
    int maxIndex = data.length() - 1;

    for (int i = 0; i <= maxIndex && found <= index; i++) {
        if (data.charAt(i) == separator || i == maxIndex) {
        found++;
        strIndex[0] = strIndex[1] + 1;
        strIndex[1] = (i == maxIndex) ? i + 1 : i;
        }
    }

    return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}

//+=============================================================================
// Return which IRsend object to act on
//
IRsend pickIRsend (int out) {
    return irsend1;
}

//+=============================================================================
// Display encoding type
//
String encoding(decode_results *results) {
  return typeToString(results->decode_type);
}

//+=============================================================================
// Send header HTML
//
void sendHeader() {
  sendHeader(200);
}

void sendHeader(int httpcode) {
    server->setContentLength(CONTENT_LENGTH_UNKNOWN);
    server->send(httpcode, "text/html; charset=utf-8", "");
    server->sendContent("<!DOCTYPE html PUBLIC '-//W3C//DTD XHTML 1.0 Strict//EN' 'http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd'>\n");
    server->sendContent("<html xmlns='http://www.w3.org/1999/xhtml' xml:lang='en'>\n");
    server->sendContent("  <head>\n");
    server->sendContent("    <meta name='viewport' content='width=device-width, initial-scale=.75' />\n");
    server->sendContent("    <link rel='stylesheet' href='https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css' />\n");
    server->sendContent("    <style>@media (max-width: 991px) {.nav-pills>li {float: none; margin-left: 0; margin-top: 5px; text-align: center;}}</style>\n");
    server->sendContent("    <title>ESP8266 IR Controller (" + String(host_name) + ")</title>\n");
    server->sendContent("  </head>\n");
    server->sendContent("  <body>\n");
    server->sendContent("    <div class='container'>\n");
    server->sendContent("      <h1>" + String(host_name) + "</h1>\n");
    server->sendContent("      <div class='row'>\n");
    server->sendContent("        <div class='col-md-12'>\n");
    server->sendContent("          <ul class='nav nav-pills'>\n");
    server->sendContent("            <li class='active'>\n");
    server->sendContent("              <a href='http://" + String(host_name) + ".local" + ":" + String(port) + "'>Hostname <span class='badge'>" + String(host_name) + ".local" + ":" + String(port) + "</span></a></li>\n");
    server->sendContent("            <li class='active'>\n");
    server->sendContent("              <a href='http://" + WiFi.localIP().toString() + ":" + String(port) + "'>Local <span class='badge'>" + WiFi.localIP().toString() + ":" + String(port) + "</span></a></li>\n");
    server->sendContent("            <li class='active'>\n");
    server->sendContent("              <a href='http://" + WiFi.dnsIP().toString() + "'>DNS <span class='badge'>" + WiFi.dnsIP().toString() + "</span></a></li>\n");
    server->sendContent("            <li class='active'>\n");
    server->sendContent("              <a>MAC <span class='badge'>" + String(WiFi.macAddress()) + "</span></a></li>\n");
    server->sendContent("          </ul>\n");
    server->sendContent("        </div>\n");
    server->sendContent("      </div><hr />\n");
}

//+=============================================================================
// Send footer HTML
//
void sendFooter() {
    server->client().stop();
}

//+=============================================================================
// Stream home page HTML
//
void sendHomePage() {
  sendHomePage("", "");
}

void sendHomePage(String message, String header) {
  sendHomePage(message, header, 0);
}

void sendHomePage(String message, String header, int type) {
  sendHomePage(message, header, type, 200);
}

void sendHomePage(String message, String header, int type, int httpcode) {
    sendHeader(httpcode);
    if (type == 1)
    server->sendContent("      <div class='row'><div class='col-md-12'><div class='alert alert-success'><strong>" + header + "!</strong> " + message + "</div></div></div>\n");
    if (type == 2)
    server->sendContent("      <div class='row'><div class='col-md-12'><div class='alert alert-warning'><strong>" + header + "!</strong> " + message + "</div></div></div>\n");
    if (type == 3)
    server->sendContent("      <div class='row'><div class='col-md-12'><div class='alert alert-danger'><strong>" + header + "!</strong> " + message + "</div></div></div>\n");
    sendFooter();
}

//+=============================================================================
// Stream code page HTML
//
void sendCodePage(Code selCode) {
  sendCodePage(selCode, 200);
}

void sendCodePage(Code selCode, int httpcode){
    sendHeader(httpcode);
    server->sendContent("      <div class='row'>\n");
    server->sendContent("        <div class='col-md-12'>\n");
    server->sendContent("          <h2><span class='label label-success'>" + String(selCode.data) + ":" + String(selCode.encoding) + ":" + String(selCode.bits) + "</span></h2><br/>\n");
    server->sendContent("          <dl class='dl-horizontal'>\n");
    server->sendContent("            <dt>Data</dt>\n");
    server->sendContent("            <dd><code>" + String(selCode.data)  + "</code></dd></dl>\n");
    server->sendContent("          <dl class='dl-horizontal'>\n");
    server->sendContent("            <dt>Type</dt>\n");
    server->sendContent("            <dd><code>" + String(selCode.encoding)  + "</code></dd></dl>\n");
    server->sendContent("          <dl class='dl-horizontal'>\n");
    server->sendContent("            <dt>Length</dt>\n");
    server->sendContent("            <dd><code>" + String(selCode.bits)  + "</code></dd></dl>\n");
    server->sendContent("          <dl class='dl-horizontal'>\n");
    server->sendContent("            <dt>Address</dt>\n");
    server->sendContent("            <dd><code>" + String(selCode.address)  + "</code></dd></dl>\n");
    server->sendContent("          <dl class='dl-horizontal'>\n");
    server->sendContent("            <dt>Raw</dt>\n");
    server->sendContent("            <dd><code>" + String(selCode.raw)  + "</code></dd></dl>\n");
    server->sendContent("          <dl class='dl-horizontal'>\n");
    server->sendContent("            <dt>Timestamp</dt>\n");
    server->sendContent("            <dd><code>" + epochToString(selCode.timestamp)  + "</code></dd></dl>\n");
    server->sendContent("        </div></div>\n");
    server->sendContent("      <div class='row'>\n");
    server->sendContent("        <div class='col-md-12'>\n");
    server->sendContent("          <div class='alert alert-warning'>Don't forget to add your passcode to the URLs below if you set one</div>\n");
    server->sendContent("      </div></div>\n");
    if (String(selCode.encoding) == "UNKNOWN") {
    server->sendContent("      <div class='row'>\n");
    server->sendContent("        <div class='col-md-12'>\n");
    server->sendContent("          <ul class='list-unstyled'>\n");
    server->sendContent("            <li>Hostname <span class='label label-default'>JSON</span></li>\n");
    server->sendContent("            <li><pre>http://" + String(host_name) + ".local:" + String(port) + "/json?plain=[{data:[" + String(selCode.raw) + "],type:'raw',khz:38}]</pre></li>\n");
    server->sendContent("            <li>Local IP <span class='label label-default'>JSON</span></li>\n");
    server->sendContent("            <li><pre>http://" + WiFi.localIP().toString() + ":" + String(port) + "/json?plain=[{data:[" + String(selCode.raw) + "],type:'raw',khz:38}]</pre></li>\n");
    } else if (String(selCode.encoding) == "PANASONIC" || String(selCode.encoding) == "NEC") {
    //} else if (strtoul(selCode.address, 0, 0) > 0) {
    server->sendContent("      <div class='row'>\n");
    server->sendContent("        <div class='col-md-12'>\n");
    server->sendContent("          <ul class='list-unstyled'>\n");
    server->sendContent("            <li>Hostname <span class='label label-default'>MSG</span></li>\n");
    server->sendContent("            <li><pre>http://" + String(host_name) + ".local:" + String(port) + "/msg?code=" + String(selCode.data) + ":" + String(selCode.encoding) + ":" + String(selCode.bits) + "&address=" + String(selCode.address) + "</pre></li>\n");
    server->sendContent("            <li>Local IP <span class='label label-default'>MSG</span></li>\n");
    server->sendContent("            <li><pre>http://" + WiFi.localIP().toString() + ":" + String(port) + "/msg?code=" + String(selCode.data) + ":" + String(selCode.encoding) + ":" + String(selCode.bits) + "&address=" + String(selCode.address) + "</pre></li>\n");
    server->sendContent("            <li>External IP <span class='label label-default'>MSG</span></li>\n");
    server->sendContent("          <ul class='list-unstyled'>\n");
    server->sendContent("            <li>Hostname <span class='label label-default'>JSON</span></li>\n");
    server->sendContent("            <li><pre>http://" + String(host_name) + ".local:" + String(port) + "/json?plain=[{data:'" + String(selCode.data) + "',type:'" + String(selCode.encoding) + "',length:" + String(selCode.bits) + ",address:'" + String(selCode.address) + "'}]</pre></li>\n");
    server->sendContent("            <li>Local IP <span class='label label-default'>JSON</span></li>\n");
    server->sendContent("            <li><pre>http://" + WiFi.localIP().toString() + ":" + String(port) + "/json?plain=[{data:'" + String(selCode.data) + "',type:'" + String(selCode.encoding) + "',length:" + String(selCode.bits) + ",address:'" + String(selCode.address) + "'}]</pre></li>\n");
    } else {
    server->sendContent("      <div class='row'>\n");
    server->sendContent("        <div class='col-md-12'>\n");
    server->sendContent("          <ul class='list-unstyled'>\n");
    server->sendContent("            <li>Hostname <span class='label label-default'>MSG</span></li>\n");
    server->sendContent("            <li><pre>http://" + String(host_name) + ".local:" + String(port) + "/msg?code=" + String(selCode.data) + ":" + String(selCode.encoding) + ":" + String(selCode.bits) + "</pre></li>\n");
    server->sendContent("            <li>Local IP <span class='label label-default'>MSG</span></li>\n");
    server->sendContent("            <li><pre>http://" + WiFi.localIP().toString() + ":" + String(port) + "/msg?code=" + String(selCode.data) + ":" + String(selCode.encoding) + ":" + String(selCode.bits) + "</pre></li>\n");
    server->sendContent("            <li>External IP <span class='label label-default'>MSG</span></li>\n");
    server->sendContent("          <ul class='list-unstyled'>\n");
    server->sendContent("            <li>Hostname <span class='label label-default'>JSON</span></li>\n");
    server->sendContent("            <li><pre>http://" + String(host_name) + ".local:" + String(port) + "/json?plain=[{data:'" + String(selCode.data) + "',type:'" + String(selCode.encoding) + "',length:" + String(selCode.bits) + "}]</pre></li>\n");
    server->sendContent("            <li>Local IP <span class='label label-default'>JSON</span></li>\n");
    server->sendContent("            <li><pre>http://" + WiFi.localIP().toString() + ":" + String(port) + "/json?plain=[{data:'" + String(selCode.data) + "',type:'" + String(selCode.encoding) + "',length:" + String(selCode.bits) + "}]</pre></li>\n");
    }
    server->sendContent("        </div>\n");
    server->sendContent("     </div>\n");
    sendFooter();
}

//+=============================================================================
// Send IR codes to variety of sources
//
void irblast(String type, String dataStr, unsigned int len, int rdelay, int pulse, int pdelay, int repeat, long address, IRsend irsend) {
    Serial.println("Blasting off");
    type.toLowerCase();
    uint64_t data = strtoull(("0x" + dataStr).c_str(), 0, 0);
    Serial.println("Blocking incoming IR signals");
    // Repeat Loop
    for (int r = 0; r < repeat; r++) {
        // Pulse Loop
        for (int p = 0; p < pulse; p++) {
        serialPrintUint64(data, HEX);
        if (type == "nec") {
            irsend.sendNEC(data, len);
        } else if (type == "lg") {
            irsend.sendLG(data, len);
        }
        if (p + 1 < pulse) delay(pdelay);
        }
        if (r + 1 < repeat) delay(rdelay);

        if (toggleRC) {
        if (type == "rc5") { _rc5toggle = !_rc5toggle; }
        if (type == "rc6") { _rc6toggle = !_rc6toggle; }
        }
    }

    Serial.println("Transmission complete");
}

void irblastlong(String type, String dataStr, int dataStrLen, unsigned int len, int rdelay, int pulse, int pdelay, int repeat, long address, IRsend irsend) {
    type.toLowerCase();
    for (int i = 0; i < dataStrLen; i++) {
        char number = dataStr[i];
        String code = GetCodeFromNumber(number, type);
        uint64_t data = strtoull(("0x" + code).c_str(), 0, 0);
        // Repeat Loop
        for (int r = 0; r < repeat; r++) {
            // Pulse Loop
            for (int p = 0; p < pulse; p++) {
                serialPrintUint64(data, HEX);
                if (type == "nec") {
                    irsend.sendNEC(data, len);
                } else if (type == "lg") {
                    irsend.sendLG(data, len);
                }
                if (p + 1 < pulse) delay(pdelay);
            }
                if (r + 1 < repeat) delay(rdelay);
            if (toggleRC) {
                if (type == "rc5") { _rc5toggle = !_rc5toggle; }
                if (type == "rc6") { _rc6toggle = !_rc6toggle; }
            }
        }
        delay(1000);
    }
    Serial.println("Transmission complete");
}

void rawblast(JsonArray &raw, int khz, int rdelay, int pulse, int pdelay, int repeat, IRsend irsend,int duty) {
    Serial.println("Raw transmit");
    holdReceive = true;
    Serial.println("Blocking incoming IR signals");
    // Repeat Loop
    for (int r = 0; r < repeat; r++) {
        // Pulse Loop
        for (int p = 0; p < pulse; p++) {
        Serial.println("Sending code");
        irsend.enableIROut(khz,duty);
        for (unsigned int i = 0; i < raw.size(); i++) {
            int val = raw[i];
            if (i & 1) irsend.space(std::max(0, val));
            else       irsend.mark(val);
        }
        irsend.space(0);
        if (p + 1 < pulse) delay(pdelay);
        }
        if (r + 1 < repeat) delay(rdelay);
    }

    Serial.println("Transmission complete");
}

String GetPowerCode(String type) {
    if (type == "NEC" || type == "LG") return "20DF10EF";
}

String GetLowerVolumeCode(String type) {
    if (type == "NEC" || type == "LG") return "20DFC03F";
}

String GetRaiseVolumeCode(String type) {
    if (type == "NEC" || type == "LG") return "20DF40BF";
}

String GetMuteCode(String type) {
    if (type == "NEC" || type == "LG") return "20DF906F";
}

String GetCodeFromNumber(char number, String type) {
    if (type == "nec" || type == "lg") {
        switch (number) {
            case '0': return "20DF08F7";
            case '1': return "20DF8877";
            case '2': return "20DF48B7";
            case '3': return "20DFC837";
            case '4': return "20DF28D7";
            case '5': return "20DFA857";
            case '6': return "20DF6897";
            case '7': return "20DFE817";
            case '8': return "20DF18E7";
            case '9': return "20DF9867";
        }
    }
}

String GetRaiseChannelCode(String type) {
    if (type == "NEC" || type == "LG") return "20DF00FF";
}

String GetLowerChannelCode(String type) {
    if (type == "NEC" || type == "LG") return "20DF807F";
}

void loop() {
    ArduinoOTA.handle();
    server->handleClient();
    decode_results  results;
    delay(200);
}
