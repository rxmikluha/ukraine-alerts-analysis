# 🚨 Vector-Lag: Air Raid Threat Propagation Analytics

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Pandas](https://img.shields.io/badge/Pandas-Data_Analysis-150458.svg)
![SVG](https://img.shields.io/badge/SVG-Interactive_Dashboard-FFB13B.svg)

## 📌 Overview
**Vector-Lag** is a defense analytics mini-project designed to model, calculate, and visualize the time-series propagation of air raid alerts across Ukrainian regions (Kharkiv → Poltava → Dnipro / Kyiv). 

Rather than relying on static datasets, this project features a custom-built, causal data simulator that mimics the physical kinematics of aerial threats. The crowning feature is a fully automated pipeline that calculates temporal latency and programmatically generates a **zero-dependency, interactive SVG dashboard** using embedded JavaScript and SMIL animations.

## ⚙️ Architecture & Pipeline

This project operates as a continuous pipeline script (`main.py`) that executes four distinct phases:
1. **Simulation:** Generates a 30-day synthetic dataset of realistic, geographically cascading alerts.
2. **Analysis:** Applies algorithmic time-windowing to calculate the average minute-delay (latency) between interconnected regional alerts.
3. **Static Rendering:** Outputs a traditional `seaborn` correlation heatmap (`propagation_matrix.png`).
4. **Dynamic Dashboard Injection:** Injects the calculated pandas matrix data directly into an SVG payload, writing a standalone interactive file (`dashboard.svg`) to the disk.

## ✨ Key Features

* **Causal Geographic Simulation:** Models threats originating in Eastern border regions (Kharkiv) and calculates the probabilistic cascade to central sectors based on randomized time offsets.
* **Vector Lag Matrix:** Cross-references thousands of simulated alert timestamps to find the exact average delay between a threat being detected in City A and arriving in City B.
* **Zero-Dependency Interactive UI:** The output `dashboard.svg` contains all necessary CSS and JavaScript internally. It requires no Node.js, no React, and no web hosting—just double-click to open in any browser.
* **Animated Threat Vectors:** Visualizes the "flight path" of alerts with animated particles scaled accurately to the simulated latency.

## 🛠️ Tech Stack
* **Core:** Python 3.9+
* **Data Processing:** `pandas`, `numpy`
* **Visualization (Static):** `seaborn`, `matplotlib`
* **Visualization (Dynamic):** Pure SVG, Embedded Vanilla JS, CSS3
