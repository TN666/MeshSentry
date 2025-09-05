# MeshSentry

A **Meshtastic node monitoring solution** for comprehensive performance analytics and visualization.


## Overview

MeshSentry provides real-time monitoring and analysis of mesh node metrics, enabling users to track performance, traffic patterns, and overall network health.


## Features
![alt text](pictures/image.png)
![alt text](pictures/image-1.png)
![alt text](pictures/image-2.png)

- **Performance Analytics** - Detailed metrics collection and performance insights
- **Dashboard Visualization** - Interactive web-based monitoring interface

## Installation

```bash
# Clone the repo
git clone https://github.com/TN666/MeshSentry.git
cd MeshSentry

# Create and activate a virtual environment
python -m venv .venv

# On macOS/Linux
source .venv/bin/activate

# On Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

1. Connect your Meshtastic node to your host computer via serial port (or use BLE).
2. Start the monitoring service:
   ```bash
   docker compose up
   ```
3. Run the data collector:
   ```bash
   # Using Serial
   python main.py -c serial
  
   # Using BLE
   python main.py -c ble
   ```
4. Access the dashboard:
   ```bash
   http://localhost:3000
   ```
5. Log in with the default credentials:
   ```bash
   Username: admin
   Password: admin
   ```

## Configuration

Configure MeshSentry by editing the `.env` file with your specific settings

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details.

