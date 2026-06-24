import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

# 1. Configuration & Cities
CITIES = ['Kharkiv', 'Poltava', 'Dnipro', 'Kyiv']
START_DATE = datetime(2026, 6, 1)
DAYS_TO_SIMULATE = 30
TOTAL_ALERTS_KHARKIV = 150  # Base alerts originating near the border


def generate_realistic_alerts():
    """Generates synthetic but realistic air raid alert data based on geographic propagation."""
    records = []

    # Generate base alerts for Kharkiv (closest to border)
    np.random.seed(42)  # For reproducibility
    kharkiv_times = [START_DATE + timedelta(days=np.random.uniform(0, DAYS_TO_SIMULATE))
                     for _ in range(TOTAL_ALERTS_KHARKIV)]

    for k_time in sorted(kharkiv_times):
        duration = timedelta(minutes=np.random.randint(30, 120))
        records.append({'city': 'Kharkiv', 'start_time': k_time, 'end_time': k_time + duration})

        # Simulate propagation to Poltava (High probability, 10-25 min lag)
        if np.random.rand() > 0.3:
            p_lag = timedelta(minutes=np.random.randint(10, 25))
            p_time = k_time + p_lag
            records.append({'city': 'Poltava', 'start_time': p_time, 'end_time': p_time + duration})

            # Simulate propagation from Poltava to Kyiv (Medium probability, 25-45 min lag)
            if np.random.rand() > 0.4:
                ky_lag = timedelta(minutes=np.random.randint(25, 45))
                ky_time = p_time + ky_lag
                records.append({'city': 'Kyiv', 'start_time': ky_time, 'end_time': ky_time + duration})

        # Simulate propagation to Dnipro directly from East (Medium probability, 15-30 min lag)
        if np.random.rand() > 0.5:
            d_lag = timedelta(minutes=np.random.randint(15, 30))
            d_time = k_time + d_lag
            records.append({'city': 'Dnipro', 'start_time': d_time, 'end_time': d_time + duration})

    return pd.DataFrame(records).sort_values('start_time').reset_index(drop=True)


def calculate_lag_matrix(df):
    """Calculates the average time lag (in minutes) between alerts in different cities."""
    matrix = pd.DataFrame(index=CITIES, columns=CITIES, dtype=float)

    for city_a in CITIES:
        for city_b in CITIES:
            if city_a == city_b:
                matrix.loc[city_a, city_b] = 0.0
                continue

            lags = []
            alerts_a = df[df['city'] == city_a]['start_time'].tolist()
            alerts_b = df[df['city'] == city_b]['start_time'].tolist()

            for time_a in alerts_a:
                # Find alerts in city_b that happened AFTER city_a but within a 2-hour window
                valid_subsequent = [tb for tb in alerts_b if timedelta(0) < (tb - time_a) < timedelta(hours=2)]
                if valid_subsequent:
                    closest_time = min(valid_subsequent)
                    lag_minutes = (closest_time - time_a).total_seconds() / 60.0
                    lags.append(lag_minutes)

            # If there is a meaningful connection, record the average lag, else leave as NaN
            if len(lags) > 5:  # Minimum threshold of occurrences to establish a pattern
                matrix.loc[city_a, city_b] = np.mean(lags)
            else:
                matrix.loc[city_a, city_b] = np.nan

    return matrix


def plot_propagation_matrix(matrix):
    """Renders and saves the threat propagation heatmap."""
    plt.figure(figsize=(8, 6))
    sns.heatmap(matrix, annot=True, cmap='Reds', fmt='.1f',
                cbar_kws={'label': 'Average Lag (Minutes)'},
                mask=matrix.isnull())

    plt.title('Air Raid Threat Propagation Matrix\n(Average Latency Between Regional Alerts)', pad=20)
    plt.ylabel('Originating City')
    plt.xlabel('Receiving City')
    plt.tight_layout()
    plt.savefig('propagation_matrix.png', dpi=300)
    plt.close()


def generate_interactive_dashboard(matrix, filename="dashboard.svg"):
    """
    Dynamically generates an interactive SVG dashboard.
    It injects the actual calculated lag times from the pandas matrix
    directly into the SVG's javascript payload.
    """

    # Helper to safely extract and format matrix data
    def get_lag(orig, dest):
        val = matrix.loc[orig, dest]
        return f"{val:.1f}" if not pd.isna(val) else "N/A"

    lag_k_p = get_lag('Kharkiv', 'Poltava')
    lag_k_d = get_lag('Kharkiv', 'Dnipro')
    lag_p_ky = get_lag('Poltava', 'Kyiv')

    # The SVG payload with placeholders for our dynamic data
    svg_template = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 600" width="100%" height="100%">
  <defs>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="1"/>
    </pattern>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="5" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>

  <style>
    .bg { fill: #0a0f1a; }
    .text-title { fill: #f8fafc; font-family: 'Courier New', Courier, monospace; font-size: 22px; font-weight: bold; letter-spacing: 1px; }
    .text-sub { fill: #64748b; font-family: 'Courier New', Courier, monospace; font-size: 14px; }
    .node { fill: #3b82f6; cursor: pointer; transition: all 0.3s ease; }
    .node:hover { fill: #60a5fa; stroke: #fff; stroke-width: 2px; }
    .node-origin { fill: #ef4444; }
    .label { fill: #cbd5e1; font-family: sans-serif; font-size: 14px; font-weight: bold; pointer-events: none; }
    .edge { stroke: #334155; stroke-width: 2; stroke-dasharray: 6,6; transition: stroke 0.3s ease; }
    .edge-active { stroke: #ef4444; stroke-width: 3; stroke-dasharray: none; }
    .panel { fill: #1e293b; stroke: #475569; stroke-width: 1; rx: 6; ry: 6; }
    .panel-text { fill: #10b981; font-family: 'Courier New', monospace; font-size: 13px; pointer-events: none; }
    .panel-alert { fill: #ef4444; font-family: 'Courier New', monospace; font-size: 13px; font-weight: bold; pointer-events: none; }
    .particle { fill: #ef4444; opacity: 0; }
  </style>

  <rect width="100%" height="100%" class="bg" />
  <rect width="100%" height="100%" fill="url(#grid)" />

  <text x="30" y="40" class="text-title">SYSTEM: THREAT PROPAGATION OVERVIEW</text>
  <text x="30" y="65" class="text-sub">STATUS: ONLINE | INTERACTIVE: TRUE | CLICK NODES TO SIMULATE</text>

  <g id="info-panel" transform="translate(30, 450)">
    <rect width="320" height="120" class="panel" />
    <text x="15" y="25" class="panel-alert">>> TACTICAL DATA FEED</text>
    <text x="15" y="50" class="panel-text" id="data-city">Target: SELECT SECTOR</text>
    <text x="15" y="75" class="panel-text" id="data-lag">Calculated Latency: --</text>
    <text x="15" y="100" class="panel-text" id="data-risk">Risk Profile: --</text>
  </g>

  <path id="path-k-p" class="edge" d="M 700 250 L 500 300" />
  <path id="path-k-d" class="edge" d="M 700 250 L 550 450" />
  <path id="path-p-ky" class="edge" d="M 500 300 L 250 200" />

  <circle id="particle-k-p" r="6" class="particle" filter="url(#glow)">
    <animateMotion dur="1.5s" begin="indefinite" fill="freeze"><mpath href="#path-k-p"/></animateMotion>
  </circle>
  <circle id="particle-k-d" r="6" class="particle" filter="url(#glow)">
    <animateMotion dur="2s" begin="indefinite" fill="freeze"><mpath href="#path-k-d"/></animateMotion>
  </circle>
  <circle id="particle-p-ky" r="6" class="particle" filter="url(#glow)">
    <animateMotion dur="2.5s" begin="indefinite" fill="freeze"><mpath href="#path-p-ky"/></animateMotion>
  </circle>

  <g id="node-kyiv" transform="translate(250, 200)" onclick="triggerData('Kyiv', '~LAG_P_KY mins from Poltava', 'SECONDARY IMPACT')">
    <circle r="15" class="node" />
    <circle r="25" fill="none" stroke="#3b82f6" stroke-width="1" opacity="0.5" />
    <text x="-15" y="-25" class="label">Kyiv</text>
  </g>

  <g id="node-poltava" transform="translate(500, 300)" onclick="triggerData('Poltava', '~LAG_K_P mins from Kharkiv', 'PRIMARY TRANSIT')">
    <circle r="15" class="node" />
    <text x="-25" y="-25" class="label">Poltava</text>
  </g>

  <g id="node-dnipro" transform="translate(550, 450)" onclick="triggerData('Dnipro', '~LAG_K_D mins from Kharkiv', 'SOUTHERN VECTOR')">
    <circle r="15" class="node" />
    <text x="-25" y="-25" class="label">Dnipro</text>
  </g>

  <g id="node-kharkiv" transform="translate(700, 250)" onclick="triggerSim()">
    <circle r="18" class="node node-origin" filter="url(#glow)" />
    <circle r="30" fill="none" stroke="#ef4444" stroke-width="2" opacity="0.8">
      <animate attributeName="r" values="18; 50" dur="2s" repeatCount="indefinite" />
      <animate attributeName="opacity" values="0.8; 0" dur="2s" repeatCount="indefinite" />
    </circle>
    <text x="-25" y="-35" class="label">Kharkiv (ORIGIN)</text>
  </g>

  <script type="text/javascript">
    <![CDATA[
      function triggerData(city, lag, risk) {
        document.getElementById('data-city').textContent = 'Target: ' + city;
        document.getElementById('data-lag').textContent = 'Calculated Latency: ' + lag;
        document.getElementById('data-risk').textContent = 'Risk Profile: ' + risk;
      }

      function triggerSim() {
        triggerData('Kharkiv', '0.0 mins (Origin)', 'CRITICAL ORIGIN');

        const edges = ['path-k-p', 'path-k-d', 'path-p-ky'];
        edges.forEach(id => {
            const el = document.getElementById(id);
            el.setAttribute('class', 'edge edge-active');
            setTimeout(() => el.setAttribute('class', 'edge'), 3000);
        });

        const particles = ['particle-k-p', 'particle-k-d', 'particle-p-ky'];
        particles.forEach((id, index) => {
            const el = document.getElementById(id);
            el.style.opacity = 1;
            const anim = el.querySelector('animateMotion');

            if(id === 'particle-p-ky') {
               setTimeout(() => anim.beginElement(), 1500);
            } else {
               anim.beginElement();
            }

            setTimeout(() => el.style.opacity = 0, 4500);
        });
      }
    ]]>
  </script>
</svg>"""

    # Inject the calculated data into the SVG template
    svg_content = svg_template.replace('LAG_K_P', lag_k_p)
    svg_content = svg_content.replace('LAG_K_D', lag_k_d)
    svg_content = svg_content.replace('LAG_P_KY', lag_p_ky)

    # Write the file to disk
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(svg_content)


if __name__ == "__main__":
    print("1. Initializing Threat Simulation...")
    df_alerts = generate_realistic_alerts()
    print(f"   -> Generated {len(df_alerts)} total alerts across {len(CITIES)} cities.")

    print("2. Calculating Vector Lags...")
    lag_matrix = calculate_lag_matrix(df_alerts)
    print("   -> Matrix calculations complete.")

    print("3. Rendering Static Heatmap...")
    plot_propagation_matrix(lag_matrix)
    print("   -> Image saved as 'propagation_matrix.png'.")

    print("4. Generating Interactive SVG Dashboard...")
    generate_interactive_dashboard(lag_matrix)
    print("   -> Interactive dashboard saved as 'dashboard.svg'.")

    print("\n✅ All processes complete! You can now open 'dashboard.svg' in any web browser.")