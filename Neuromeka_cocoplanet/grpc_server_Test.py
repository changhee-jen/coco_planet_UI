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
        fake ={

  "pickup_doors": {

    "tray_1": {

      "is_opened": False

    },

    "tray_2": {

      "is_opened": False

    },

    "tray_3": {

      "is_opened": False

    },

    "tray_4": {

      "is_opened": False

    }

  },

  "pre_orders": {},

  "working_orders": {

    "78d6e12a-3e75-469b-9f23-939f26f19b96": {

      "sensor": "cup_detection_sensor_1",

      "barcode": "2025070210022",

      "recipe": "Iced Americano",

      "recipekr": "아이스 아메리카노",

      "progress": 30

    }

  },

  "pickup_waiting_orders": {}

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
