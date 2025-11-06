from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import cv2
import numpy as np
from plate_recognition import detect_license_plate
from utils import read_config
import uvicorn  # ✅ use uvicorn programmatically

# ================== CONFIG ==================
HOST = "0.0.0.0"
PORT = 8000
CONFIG_PATH = "config/config.yaml"

# ================== APP =====================
app = FastAPI()
config = read_config(CONFIG_PATH)

# ✅ CORS fix
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow any frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ImageData(BaseModel):
    image_base64: str


def base64_to_cv2(base64_str):
    """Convert base64 string to OpenCV image"""
    img_data = base64.b64decode(base64_str.split(",")[-1])
    np_arr = np.frombuffer(img_data, np.uint8)
    return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)


def cv2_to_base64(img):
    """Convert OpenCV image to base64"""
    _, buffer = cv2.imencode(".jpg", img)
    return "data:image/jpeg;base64," + base64.b64encode(buffer).decode("utf-8")


@app.post("/recognize/")
async def recognize_plate(data: ImageData):
    img = base64_to_cv2(data.image_base64)
    results = detect_license_plate(config, img)

    if not results:
        return {"status": "no_plate", "results": []}

    output = []
    for r in results:
        encoded_img = cv2_to_base64(r["roi"])
        output.append({
            "plate_id": r["plate_id"],
            "text": r["text"],
            "image": encoded_img
        })

    return {"status": "ok", "results": output}


# ✅ Run normally (no CLI args)
if __name__ == "__main__":
    print(f"🚀 Running backend on http://{HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)
