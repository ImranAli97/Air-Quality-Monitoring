# Air Quality Monitoring with Raspberry Pi

This project measures **air quality (PM1, PM2.5, PM10)** and **temperature/humidity** using a Raspberry Pi.  
It integrates with **ThingSpeak Cloud** for data logging and visualization, while also showing real-time values on a **7-segment display** and **LED matrix**.

---

## Features
- Fetch and visualize **PM1, PM2.5, PM10** data from ThingSpeak
- Local **temperature and humidity** readings via DHT11 sensor
- **AQI (Air Quality Index)** calculation from PM values
- Real-time output on:
  - MAX7219 LED Matrix
  - I2C 7-Segment Display
- Upload processed AQI data back to **ThingSpeak**
- Optional graph visualization using Matplotlib

---

## Hardware Requirements
- Raspberry Pi (any model with GPIO + I2C/SPI support)
- DHT11 sensor (temperature & humidity)
- MAX7219 LED matrix
- I2C 7-segment display
- 2 push buttons (GPIO input)

---

## Software Requirements
- Python 3.x
- Libraries listed in [`requirements.txt`](requirements.txt)

Install dependencies:
```bash
pip install -r requirements.txt
