from flask import Flask, render_template, jsonify

app = Flask(__name__)

# 임시 데이터
pickup_list = [
    {"pick": 1, "order_no": 103, "menu": "아이스 아메리카노"},
    {"pick": 2, "order_no": 103, "menu": "헤이즐넛 아메리카노"},
    {"pick": 3, "order_no": 121, "menu": "히비스커스 자몽블랙티"},
    {"pick": 4, "order_no": 122, "menu": "카페라떼"},
    {"pick": 13, "order_no": 122, "menu": "바닐라 라떼"},
    {"pick": 7, "order_no": 123, "menu": "아이스 아메리카노"},
    {"pick": 8, "order_no": 124, "menu": "카푸치노"},
    {"pick": 12, "order_no": 126, "menu": "아이스티"},
]

order_status = [
    {"order_no": 101, "menu": "Americano"},
    {"order_no": 101, "menu": "Americano"},
    {"order_no": 101, "menu": "Americano"}
]

processing = {"order_no": 101, "menu": "Americano"}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def get_status():
    data = {
        "pickup_list": pickup_list,
        "order_status": order_status,
        "processing": processing
    }
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
