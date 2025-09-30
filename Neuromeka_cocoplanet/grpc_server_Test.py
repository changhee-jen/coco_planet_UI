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
        # ✅ parse_grpc_data 구조에 맞춘 가짜 데이터
        fake = {
            "pickup_waiting_orders": {
                "id-1": {
                    "barcode": "202509300001",
                    "recipe": "Ice cream",
                    "sensor": "cup_detection_sensor_1"
                },
                "id-2": {
                    "barcode": "202509300002",
                    "recipe": "Hot-Latte",
                    "sensor": "cup_detection_sensor_2"
                }
            },
            "working_orders": {
                "id-3": {
                    "barcode": "202509300003",
                    "recipe": "Cappuccino",
                    "sensor": "cup_detection_sensor_3"
                },
                "id-4": {
                    "barcode": "202509300003",
                    "recipe": "ICEcream",
                    "sensor": "cup_detection_sensor_3"
                }
            },
            "pre_orders": {
                "id-4": {
                    "barcode": "202509300004",
                    "recipe": "Vanilla Latte"
                },
                "id-5": {
                    "barcode": "202509300005",
                    "recipe": "Espresso"
                },
                "id-6": {
                    "barcode": "202509300005",
                    "recipe": "Espresso"
                },
                "id-7": {
                    "barcode": "202509300005",
                    "recipe": "Espresso"
                },
                 "id-8": {
                    "barcode": "202509300005",
                    "recipe": "Espresso"
                },
                  "id-9": {
                    "barcode": "202509300005",
                    "recipe": "Espresso"
                },
                   "id-10": {
                    "barcode": "202509300005",
                    "recipe": ""
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
