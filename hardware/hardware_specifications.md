# IoT Tea Crop Monitoring System - Hardware Specifications

## Overview
Complete IoT-based tea crop monitoring system with real-time sensor data collection and ML-powered predictions.

## Hardware Components

### 1. Microcontroller Board
- **ESP32 Dev Kit V1**
- WiFi + Bluetooth connectivity
- Dual-core processor @ 240MHz
- 520KB SRAM, 4MB Flash
- Low power consumption

### 2. Environmental Sensors

#### Temperature & Humidity
- **DHT22 Digital Sensor**
- Range: -40°C to +80°C, 0-100% RH
- Accuracy: ±0.5°C, ±2% RH
- Digital output, no calibration needed

#### Soil Moisture
- **Capacitive Soil Moisture Sensor**
- Range: 0-100% VWC (Volumetric Water Content)
- Accuracy: ±3%
- Corrosion-resistant, long lifespan

#### Rainfall Measurement
- **Tipping Bucket Rain Gauge**
- Resolution: 0.279mm per tip
- Range: 0-999mm/hour
- Digital pulse output

#### Light Intensity
- **BH1750 Digital Light Sensor**
- Range: 1-65535 lux
- Accuracy: ±20%
- I2C interface, low power

#### Soil pH
- **Analog pH Sensor Probe**
- Range: pH 0-14
- Accuracy: ±0.1
- Requires calibration

### 3. Location & Navigation
- **NEO-6M GPS Module**
- Accuracy: 2.5m
- Update rate: 5Hz
- UART interface

### 4. Power System
- **6W Monocrystalline Solar Panel**
- **18650 Li-ion Battery** (3.7V, 2600mAh)
- **TP4056 Charging Module**
- **DC-DC Buck Converter** (5V output)

### 5. Communication
- **WiFi 802.11 b/g/n**
- **Bluetooth 4.2**
- **MQTT Protocol** for data transmission
- **HTTPS API** for server communication

## Circuit Diagram

```
ESP32 Pin Connections:
----------------------
GPIO4  -> DHT22 Data
GPIO34 -> Soil Moisture Analog
GPIO2  -> Rain Gauge Digital (Interrupt)
GPIO21 -> I2C SDA (BH1750)
GPIO22 -> I2C SCL (BH1750)
GPIO32 -> pH Sensor Analog
GPIO35 -> Battery Monitor Analog
GPIO16 -> GPS TX
GPIO17 -> GPS RX
3.3V   -> Sensor Power
GND    -> Common Ground
```

## Power Requirements

### Sensor Power Consumption
- DHT22: 2.5mA (active), 40µA (sleep)
- Soil Moisture: 35mA
- BH1750: 0.12mA
- pH Sensor: 5mA
- GPS Module: 45mA (active), 10mA (standby)
- ESP32: 160mA (WiFi active), 10µA (deep sleep)

### Total Current Draw
- **Active Mode**: ~250mA
- **Sleep Mode**: ~50µA
- **Battery Life**: ~7 days (no sun), ~30 days (partial sun)

## Data Collection Frequency

### Monitoring Schedule
- **Temperature/Humidity**: Every 5 minutes
- **Soil Moisture**: Every 15 minutes
- **Rainfall**: Event-driven (tipping bucket)
- **Light Intensity**: Every 10 minutes
- **pH Level**: Every 30 minutes
- **GPS Location**: Every hour (or on movement)

### Data Transmission
- **WiFi Upload**: Every 30 minutes
- **Buffer Storage**: 24 hours offline capability
- **Compression**: JSON format with timestamp

## Environmental Protection

### Weatherproofing
- **IP67 Enclosure** for electronics
- **UV-resistant** plastic housing
- **Ventilation** for humidity control
- **Desiccant packets** for moisture protection

### Installation Requirements
- **Height**: 1.5m above ground
- **Orientation**: Solar panel facing south (India)
- **Soil Contact**: 10cm depth for moisture sensor
- **Rain Exposure**: Open area for rain gauge

## Cost Breakdown

### Component Costs (USD)
- ESP32 Dev Kit: $8
- DHT22 Sensor: $4
- Soil Moisture Sensor: $6
- Rain Gauge: $12
- BH1750 Light Sensor: $3
- pH Sensor: $15
- GPS Module: $10
- Solar Panel: $15
- Battery & Charger: $8
- Enclosure & Wiring: $10

### Total Cost: ~$91 per unit

## Software Features

### Embedded Firmware
- **MicroPython** for rapid development
- **OTA Updates** over WiFi
- **Watchdog Timer** for reliability
- **Error Recovery** mechanisms

### Data Processing
- **Sensor Calibration** routines
- **Data Validation** and filtering
- **Power Management** optimization
- **Network Reconnection** logic

### Security Features
- **WPA2/WPA3** WiFi encryption
- **API Key** authentication
- **Data Encryption** in transit
- **Device Authentication** certificates

## Maintenance Requirements

### Regular Maintenance
- **Solar Panel Cleaning**: Monthly
- **Sensor Calibration**: Quarterly
- **Battery Check**: Every 6 months
- **Firmware Updates**: As needed

### Troubleshooting
- **LED Indicators** for status
- **Serial Debug** output
- **Remote Diagnostics** via API
- **Alert System** for failures

## Scalability

### Multi-Node Deployment
- **Mesh Networking** capability
- **Gateway Architecture** support
- **Load Balancing** for servers
- **Data Aggregation** points

### Cloud Integration
- **AWS IoT Core** or **Azure IoT Hub**
- **Time Series Database** (InfluxDB)
- **Real-time Dashboard** (Grafana)
- **ML Model** deployment

## Future Enhancements

### Advanced Sensors
- **NDVI Sensor** for plant health
- **Soil EC Sensor** for nutrients
- **Wind Speed/Direction** sensor
- **CO2 Sensor** for air quality

### Automation Features
- **Irrigation Control** relays
- **Fertilizer Dispensing** system
- **Pest Detection** cameras
- **Drone Integration** for monitoring
