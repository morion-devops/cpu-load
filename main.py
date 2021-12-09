from flask import Flask
import socket
from cpu_load_generator import load_all_cores

app = Flask(__name__)

@app.route("/")
def hello():
    load_all_cores(duration_s=20, target_load=0.5)
    return("CPU load generated.<br/>")

if __name__ == "__main__":
    app.run(host='0.0.0.0')