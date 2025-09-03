import meshtastic
import meshtastic.serial_interface
import time
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import os
from dotenv import load_dotenv
import threading


def write_to_influxdb(url, token, org, bucket, data):
    client = InfluxDBClient(url=url, token=token, org=org)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    point = (
        Point("meshtastic_node")
        .tag("id", data["user"]["id"])
        .tag("shortName", data["user"]["shortName"])
        .tag("longName", data["user"]["longName"])
        .tag("fw_version", data["fw_version"])
        .tag("macaddr", data["user"]["macaddr"])
        .field("hwModel", data["user"]["hwModel"])
        .field("batteryLevel", data["deviceMetrics"]["batteryLevel"])
        .field("voltage", data["deviceMetrics"]["voltage"])
        .field("latitude", data["position"]["latitude"])
        .field("longitude", data["position"]["longitude"])
        .field("altitude", data["position"]["altitude"])
        .field("channelUtilization", data["deviceMetrics"]["channelUtilization"])
        .field("airUtilTx", data["deviceMetrics"]["airUtilTx"])
        .field("uptimeSeconds", data["deviceMetrics"]["uptimeSeconds"])
        .field("isFavorite", int(data["isFavorite"]))
        .field("localUptimeSeconds", data["localStats"]["uptimeSeconds"])
        .field("localChannelUtilization", data["localStats"]["channelUtilization"])
        .field("localAirUtilTx", data["localStats"]["airUtilTx"])
        .field("localNumPacketsTx", data["localStats"]["numPacketsTx"])
        .field("localNumPacketsRx", data["localStats"]["numPacketsRx"])
        .field("localNumPacketsRxBad", data["localStats"]["numPacketsRxBad"])
        .field("localNumOnlineNodes", data["localStats"]["numOnlineNodes"])
        .field("localNumTotalNodes", data["localStats"]["numTotalNodes"])
        .field("localNumRxDupe", data["localStats"]["numRxDupe"])
        .field("localNumTxRelay", data["localStats"]["numTxRelay"])
        .field("localNumTxRelayCanceled", data["localStats"]["numTxRelayCanceled"])
        .field("localHeapTotalBytes", data["localStats"]["heapTotalBytes"])
        .field("localHeapFreeBytes", data["localStats"]["heapFreeBytes"])
    )

    try:
        write_api.write(bucket=bucket, org=org, record=point)
        print("Data written to InfluxDB successfully.")
    except Exception as e:
        print(f"Error writing to InfluxDB: {e}")

    client.close()


def get_node_data(node, fw_version):
    # Extract relevant data from node object
    data = {
        "num": node.get("num"),
        "fw_version": fw_version,
        "user": {
            "id": node.get("user", {}).get("id"),
            "longName": node.get("user", {}).get("longName"),
            "shortName": node.get("user", {}).get("shortName"),
            "macaddr": node.get("user", {}).get("macaddr"),
            "hwModel": node.get("user", {}).get("hwModel"),
            "publicKey": node.get("user", {}).get("publicKey"),
            "isUnmessagable": node.get("user", {}).get("isUnmessagable"),
        },
        "position": {
            "latitudeI": node.get("position", {}).get("latitudeI"),
            "longitudeI": node.get("position", {}).get("longitudeI"),
            "altitude": node.get("position", {}).get("altitude"),
            "locationSource": node.get("position", {}).get("locationSource"),
            "latitude": node.get("position", {}).get("latitude"),
            "longitude": node.get("position", {}).get("longitude"),
        },
        "deviceMetrics": {
            "batteryLevel": node.get("deviceMetrics", {}).get("batteryLevel"),
            "voltage": node.get("deviceMetrics", {}).get("voltage"),
            "channelUtilization": node.get("deviceMetrics", {}).get(
                "channelUtilization"
            ),
            "airUtilTx": node.get("deviceMetrics", {}).get("airUtilTx"),
            "uptimeSeconds": node.get("deviceMetrics", {}).get("uptimeSeconds"),
        },
        "isFavorite": node.get("isFavorite"),
        "localStats": {
            "uptimeSeconds": node.get("localStats", {}).get("uptimeSeconds"),
            "channelUtilization": node.get("localStats", {}).get("channelUtilization"),
            "airUtilTx": node.get("localStats", {}).get("airUtilTx"),
            "numPacketsTx": node.get("localStats", {}).get("numPacketsTx"),
            "numPacketsRx": node.get("localStats", {}).get("numPacketsRx"),
            "numPacketsRxBad": node.get("localStats", {}).get("numPacketsRxBad"),
            "numOnlineNodes": node.get("localStats", {}).get("numOnlineNodes"),
            "numTotalNodes": node.get("localStats", {}).get("numTotalNodes"),
            "numRxDupe": node.get("localStats", {}).get("numRxDupe"),
            "numTxRelay": node.get("localStats", {}).get("numTxRelay"),
            "numTxRelayCanceled": node.get("localStats", {}).get("numTxRelayCanceled"),
            "heapTotalBytes": node.get("localStats", {}).get("heapTotalBytes"),
            "heapFreeBytes": node.get("localStats", {}).get("heapFreeBytes"),
        },
    }
    return data


def monitor_port(port, url, token, org, bucket, time_interval):
    try:
        interface = meshtastic.serial_interface.SerialInterface(devPath=port)
        while True:
            try:
                fw_version = interface.metadata.firmware_version
                info = interface.getMyNodeInfo()
                print(f"Port {port} - node info: {info}")
                node_data = get_node_data(info, fw_version)
                print(f"Port {port} - Writing to InfluxDB:", node_data)
                write_to_influxdb(url, token, org, bucket, node_data)
                time.sleep(int(time_interval))
            except Exception as e:
                print(f"Error monitoring port {port}: {e}")
                break
    except Exception as e:
        print(f"Failed to connect to port {port}: {e}")
    finally:
        if "interface" in locals():
            interface.close()


load_dotenv(".env")
url = os.getenv("INFLUXDB_URL", "http://localhost:8086")
token = os.getenv("DOCKER_INFLUXDB_INIT_ADMIN_TOKEN")
org = os.getenv("DOCKER_INFLUXDB_INIT_ORG", "Meshtastic")
bucket = os.getenv("DOCKER_INFLUXDB_INIT_BUCKET", "node_info")
time_interval = os.getenv("TIME_INTERVAL", 30)

ports = meshtastic.util.findPorts(True)
print("list port", ports)

threads = []
for port in ports:
    thread = threading.Thread(
        target=monitor_port,
        args=(port, url, token, org, bucket, time_interval)
    ).start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down...")
    for thread in threads:
        thread.join(timeout=1)