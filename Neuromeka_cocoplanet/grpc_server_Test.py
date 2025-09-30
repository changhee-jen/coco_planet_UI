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
        fake = {
            "pickup_doors": {
                "tray_1": {"is_opened": False},
                "tray_2": {"is_opened": False},
                "tray_3": {"is_opened": False},
                "tray_4": {"is_opened": False}
            },
            "pre_orders": {
                "pre_001": {
                    "sensor": "cup_detection_sensor_2",
                    "barcode": "2025093009001",
                    "recipe": "Green Tea Latte",
                    "recipekr": "그린티 라떼",
                    "progress": 0
                },
                "pre_002": {
                    "sensor": "cup_detection_sensor_3",
                    "barcode": "2025093009002",
                    "recipe": "Ice Cream",
                    "recipekr": "아이스크림",
                    "progress": 0
                }
            },
            "working_orders": {
                "78d6e12a-3e75-469b-9f23-939f26f19b96": {
                    "sensor": "cup_detection_sensor_1",
                    "barcode": "2025070210022",
                    "recipe": "Iced Americano",
                    "recipekr": "아이스 아메리카노",
                    "progress": 30
                },
                "order_002": {
                    "sensor": "cup_detection_sensor_2",
                    "barcode": "2025093010011",
                    "recipe": "ice cream",
                    "recipekr": "아이스크림",
                    "progress": 55
                },
                "order_003": {
                    "sensor": "cup_detection_sensor_3",
                    "barcode": "2025093010012",
                    "recipe": "Hot Latte",
                    "recipekr": "라떼",
                    "progress": 80
                }
            },
            "pickup_waiting_orders": {
                "pw_001": {
                    "sensor": "cup_detection_sensor_4",
                    "barcode": "2025093011001",
                    "recipe": "Mocha",
                    "recipekr": "모카",
                    "progress": 100
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
