# 🌍 Air Quality Monitoring with Raspberry Pi

A smart environmental monitoring system built with **Raspberry Pi** to measure and visualize:  
- Air quality (PM1, PM2.5, PM10)  
- Temperature and humidity  

Data is logged to **ThingSpeak Cloud** for real-time analysis and visualization, while local readings are displayed instantly on a **7-segment display** and an **LED matrix**.

---

## ✨ Features
- Fetch and visualize **PM1, PM2.5, PM10** data from ThingSpeak
- Local **temperature & humidity** readings via DHT11 sensor
- Automatic **AQI (Air Quality Index)** calculation
- Real-time output on:
  - MAX7219 **LED Matrix**
  - I2C **7-Segment Display**
- Upload processed AQI data back to ThingSpeak
- Optional graph plotting with **Matplotlib**

---

## 🛠 Hardware Requirements
- Raspberry Pi (any model with GPIO + I2C/SPI support)
- DHT11 sensor (temperature & humidity)
- MAX7219 LED matrix
- I2C 7-segment display
- 2 push buttons (GPIO input)

---

## 💻 Software Requirements
- Python 3.x  
- Libraries listed in [`requirements.txt`](requirements.txt)

Install dependencies:
```bash
pip install -r requirements.txt
