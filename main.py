from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import os
import uvicorn

from plate_recognition import detect_license_plate
from utils import read_config, write_config, base64_to_cv2, cv2_to_base64, merge_dict
from GenData2 import create_knn_data_from_rgb

# ================== CONFIG ==================
HOST = "0.0.0.0"
PORT = 8000
CONFIG_PATH = "config/config.yaml"

# ================== APP =====================
app = FastAPI()
config = read_config(CONFIG_PATH)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================== SCHEMAS ==================
class ImageData(BaseModel):
    image_base64: str


class TrainImage(BaseModel):
    image_base64: str
    label: str


class TrainRequest(BaseModel):
    data: list[TrainImage]


class UpdateConfig(BaseModel):
    data: dict   # nested partial update allowed


# ================== ENDPOINTS ==================

# ----------- Recognize Plate -----------
@app.post("/recognize/")
async def recognize_plate(data: ImageData):
    img = base64_to_cv2(data.image_base64)
    results = detect_license_plate(config, img)

    if not results:
        return {"status": "no_plate", "results": []}

    output = []
    for r in results:
        output.append({
            "plate_id": r["plate_id"],
            "text": r["text"],
            "image": cv2_to_base64(r["roi"])
        })

    return {"status": "ok", "results": output}


# ----------- Train KNN -----------
@app.post("/train/")
async def train_model(req: TrainRequest):
    try:
        dataset = []
        for item in req.data:
            img = base64_to_cv2(item.image_base64)
            dataset.append((img, item.label.strip().upper()))

        success = create_knn_data_from_rgb(config, dataset, show=False)
        return {"status": "ok" if success else "fail"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


# ----------- Get Config -----------
@app.get("/config/")
async def get_config():
    return {"status": "ok", "config": read_config(CONFIG_PATH)}


# ----------- Update Config -----------
@app.put("/config/")
async def update_config(req: UpdateConfig):
    try:
        cfg = read_config(CONFIG_PATH)
        merge_dict(cfg, req.data)
        write_config(CONFIG_PATH, cfg)

        global config
        config = read_config(CONFIG_PATH)

        return {"status": "ok", "updated": cfg}

    except Exception as e:
        return {"status": "error", "message": str(e)}


# ----------- Training Info -----------
@app.get("/training-info/")
async def training_info():
    model_cfg = config["model"]
    cls_path = model_cfg["classifications_path"]
    flat_path = model_cfg["flattened_images_path"]

    def count_lines(path):
        if not os.path.exists(path):
            return 0
        with open(path, "r") as f:
            return sum(1 for _ in f)

    return {
        "status": "ok",
        "samples": count_lines(cls_path),
        "images": count_lines(flat_path),
        "paths": {
            "classifications": cls_path,
            "flattened_images": flat_path
        }
    }


# ================== RUN ==================
if __name__ == "__main__":
    print(f"🚀 Backend running at http://{HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)
