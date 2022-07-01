from flask import Flask
from LGTV import LGTVScan
import json
app = Flask(__name__)

@app.route("/scan")
def ScanTV():
    results = LGTVScan()
    if len(results) > 0:
        print (json.dumps({
            "result": "ok",
            "count": len(results),
            "list": results
        }, sort_keys=True, indent=4))
    else:
        print (json.dumps({
            "result": "failed",
            "count": len(results)
        }, sort_keys=True, indent=4))
    return {
        "scan" : results
    }

if __name__ == "__main__":
  app.run()