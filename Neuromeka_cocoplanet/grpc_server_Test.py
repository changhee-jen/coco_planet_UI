# mock_grpc_server.py
import time
import json
from concurrent import futures
import grpc
import coco_planet_grpc_server_pb2 as pb2
import coco_planet_grpc_server_pb2_grpc as pb2_grpc

ADDRESS = "0.0.0.0:50051"

class MockCoCoPlanetServicer(pb2_grpc.CoCoPlanetServicer):
    def SyncData(self, request, context):
        # 예시 가짜 데이터 (원하시면 구조 맞게 바꿔서 여러 케이스 준비)
        fake = {
            "orders": {},
            "pickup_doors": {
                "tray_1": {"is_opened": False},
                "tray_2": {"is_opened": True},
                "tray_3": {"is_opened": False},
                "tray_4": {"is_opened": False}
            },
            "waiting_orders": {
                "id-1": {
                    "barcode": "2025070210021",
                    "recipe": "100137",
                    "sensor": "cup_detection_sensor_2"
                },
                  "id-2": {
                    "barcode": "2025070210021",
                    "recipe": "100137",
                    "sensor": "cup_detection_sensor_2"
                }
            },
            "working_orders": {
                "id-2": {
                    "barcode": "2025070210022",
                    "recipe": "100094",
                    "sensor": "cup_detection_sensor_3"
                }
            }
        }
        return pb2.SyncDataReply(json_string=json.dumps(fake, ensure_ascii=False))


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    pb2_grpc.add_CoCoPlanetServicer_to_server(MockCoCoPlanetServicer(), server)
    server.add_insecure_port(ADDRESS)
    server.start()
    print(f"[mock grpc] serving on {ADDRESS}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == "__main__":
    serve()
