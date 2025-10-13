#!/usr/bin/env python3
import time
import json
import random
import signal
import threading
import grpc
import subprocess
from google.protobuf import empty_pb2
from flask import Flask, render_template, jsonify

import coco_planet_grpc_server_pb2 as pb2
import coco_planet_grpc_server_pb2_grpc as pb2_grpc


# ---------------------------
# gRPC 설정
# ---------------------------
ADDRESS = "localhost:50051"
PERIOD_S = 1.0
TIMEOUT_S = 2.0
BACKOFF_INIT = 1.0
BACKOFF_MAX = 10.0

latest_data = {
    "pickup_list": [],
    "order_status": [],
    "processing": {"order_no": "-", "menu": "-"}
}
last_json = None


def setup_channel():
    options = [
        ("grpc.keepalive_time_ms", 30_000),
        ("grpc.keepalive_timeout_ms", 10_000),
        ("grpc.http2.max_pings_without_data", 0),
        ("grpc.keepalive_permit_without_calls", 1),
    ]
    return grpc.insecure_channel(ADDRESS, options=options)


def parse_grpc_data(grpc_json: dict):
    pickup_list = []
    order_status = []
    processing = [] 

    for oid, order in grpc_json.get("pickup_waiting_orders", {}).items():
        order_no = order["barcode"][-4:]
        menu = order["recipe"]
        sensor = order.get("sensor", "")
        pick_pos = int(sensor.split("_")[-1]) if sensor else None

        pickup_list.append({
            "pick": pick_pos,
            "order_no": order_no,
            "menu": menu
        })

    # working_orders → processing 
    for oid, order in grpc_json.get("working_orders", {}).items():
        order_no = order["barcode"][-4:]
        menu = order["recipe"]
        processing.append({
            "order_no": order_no,
            "menu": menu,
            "progress": order.get("progress", 0)  
        })

    # pre_orders → order_status
    for oid, order in grpc_json.get("pre_orders", {}).items():
        order_no = order["barcode"][-4:]
        menu = order["recipe"]
        order_status.append({
            "order_no": order_no,
            "menu": menu
        })

    return {
        "pickup_list": pickup_list,
        "order_status": order_status,
        "processing": processing  
    }


def grpc_loop(stop_event):
    global latest_data, last_json

    channel = setup_channel()
    stub = pb2_grpc.CoCoPlanetStub(channel)

    backoff = BACKOFF_INIT
    connected = False  

    while not stop_event.is_set():
        start_t = time.time()
        try:
            reply = stub.SyncData(empty_pb2.Empty(), timeout=TIMEOUT_S, wait_for_ready=True)

            if not connected:
                print("[GRPC] gRPC 서버 연결 성공")
                connected = True

            if backoff != BACKOFF_INIT:
                print("[GRPC] 연결 복구됨")
            backoff = BACKOFF_INIT

            if reply.json_string != last_json:
                last_json = reply.json_string
                try:
                    parsed = json.loads(reply.json_string)
                    latest_data = parse_grpc_data(parsed)

                    print(f"[{time.strftime('%H:%M:%S')}] gRPC 데이터 수신:")
                    print(json.dumps(parsed, ensure_ascii=False, indent=2))
                    print("→ 변환 결과:")
                    print(json.dumps(latest_data, ensure_ascii=False, indent=2))

                except Exception:
                    print("[WARN] JSON 파싱 실패, 원문 출력:")
                    print(reply.json_string)
                    latest_data = {"raw": reply.json_string}

        except grpc.RpcError as e:
            if connected:
                print("[WARN] gRPC 연결 끊김")
                connected = False
            code = e.code().name
            details = e.details()
            print(f"[WARN] gRPC {code}: {details}")
            sleep_s = min(backoff, BACKOFF_MAX) * (1 + random.random() * 0.25)
            time.sleep(sleep_s)
            backoff = min(backoff * 2, BACKOFF_MAX)
            continue

        elapsed = time.time() - start_t
        if elapsed < PERIOD_S:
            time.sleep(PERIOD_S - elapsed)

# ---------------------------
# Flask 설정
# ---------------------------
app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def get_status():
    return jsonify(latest_data)

if __name__ == "__main__":
    stop_event = threading.Event()
    t = threading.Thread(target=grpc_loop, args=(stop_event,), daemon=True)
    t.start()

    try:
        app_thread = threading.Thread(
            target=lambda: app.run(debug=True, use_reloader=False, port=5050),
            daemon=True
        )
        app_thread.start()

        time.sleep(3)
        subprocess.Popen([
            "firefox",
            "--kiosk",
            "http://localhost:5050"
        ])

        app_thread.join()

    finally:
        stop_event.set()
        t.join()
# if __name__ == "__main__":
#     stop_event = threading.Event()
#     t = threading.Thread(target=grpc_loop, args=(stop_event,), daemon=True)
#     t.start()

#     try:
#         # Flask 서버 실행
#         app_thread = threading.Thread(
#             target=lambda: app.run(debug=True, use_reloader=False, port=5050),
#             daemon=True
#         )
#         app_thread.start()
#         # subprocess.Popen([
#         #     r"C:\Program Files\Google\Chrome\Application\chrome.exe",
#         #     "--start-fullscreen",   # 크롬은 --kiosk 대신 이걸 권장
#         #     "--disable-infobars",
#         #     "http://localhost:5050"
#         # ])


#         subprocess.Popen([
#             "chromium-browser",
#             "--noerrdialogs",
#             "--disable-infobars",
#             "--kiosk",
#             "http://localhost:5050"
#         ])

#         # 메인 스레드는 대기
#         app_thread.join()

#     finally:
#         stop_event.set()
#         t.join()

