#!/usr/bin/env python3
import time
import json
import random
import signal
import sys
import grpc
from google.protobuf import empty_pb2
import coco_planet_grpc_server_pb2 as pb2
import coco_planet_grpc_server_pb2_grpc as pb2_grpc

ADDRESS = "localhost:50051"   # 서버 주소
PERIOD_S = 1.0                # 폴링 주기(초)
TIMEOUT_S = 2.0               # RPC 타임아웃(초)
BACKOFF_INIT = 1.0            # 재시도 백오프 시작
BACKOFF_MAX = 10.0            # 재시도 백오프 최대

def setup_channel():
    # keepalive 옵션(장기 연결 안정성)
    options = [
        ("grpc.keepalive_time_ms", 30_000),
        ("grpc.keepalive_timeout_ms", 10_000),
        ("grpc.http2.max_pings_without_data", 0),
        ("grpc.keepalive_permit_without_calls", 1),
    ]
    return grpc.insecure_channel(ADDRESS, options=options)

def pretty_json(s: str) -> str:
    try:
        return json.dumps(json.loads(s), ensure_ascii=False, indent=2, sort_keys=True)
    except Exception:
        return s  # JSON이 아니면 원문 출력

def main():
    # Ctrl+C로 깔끔 종료
    stop = False
    def handle_sigint(signum, frame):
        nonlocal stop
        stop = True
        print("\n[클라] 종료 요청 수신… 정리 중...")
    signal.signal(signal.SIGINT, handle_sigint)

    channel = setup_channel()
    stub = pb2_grpc.CoCoPlanetStub(channel)

    last_json = None
    backoff = BACKOFF_INIT

    while not stop:
        start_t = time.time()
        try:
            # 서버 상태 요청(단발)
            reply = stub.SyncData(empty_pb2.Empty(), timeout=TIMEOUT_S, wait_for_ready=True)
            # 성공했으면 백오프 초기화
            if backoff != BACKOFF_INIT:
                print("[클라] 연결 복구됨")
            backoff = BACKOFF_INIT

            # 값이 바뀌었을 때만 출력(로그 과다 방지)
            if reply.json_string != last_json:
                last_json = reply.json_string
                print(f"[{time.strftime('%H:%M:%S')}] 변경됨:\n{pretty_json(reply.json_string)}\n")

        except grpc.RpcError as e:
            code = e.code().name
            details = e.details()
            print(f"[WARN] gRPC {code}: {details}")
            # 지수 백오프 + 지터
            sleep_s = min(backoff, BACKOFF_MAX) * (1 + random.random() * 0.25)
            time.sleep(sleep_s)
            backoff = min(backoff * 2, BACKOFF_MAX)
            continue

        # 주기 보정(호출 시간 제외)
        elapsed = time.time() - start_t
        if elapsed < PERIOD_S:
            time.sleep(PERIOD_S - elapsed)

    print("[클라] 종료 완료")

if __name__ == "__main__":
    main()
