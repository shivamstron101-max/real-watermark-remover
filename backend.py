import modal
import os
import io
import traceback
from pathlib import Path

app = modal.App(name="watermark-remover-v3")

def download_models():
    from simple_lama_inpainting import SimpleLama
    SimpleLama()

image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("git", "libgl1-mesa-glx", "libglib2.0-0") 
    .pip_install(
        "fastapi~=0.111.0",
        "uvicorn~=0.30.1",
        "python-multipart~=0.0.9",
        "opencv-python~=4.10.0.84",
        "numpy~=1.26.4",
        "Pillow~=10.4.0",
        "torch",
        "torchvision",
        "simple-lama-inpainting"
    )
    .run_function(download_models)
    .add_local_dir("./dist", remote_path="/dist")
    # force rebuild 2
)

@app.cls(image=image, gpu="A10G", timeout=3600, min_containers=1)
class WatermarkRemover:
    @modal.enter()
    def setup(self):
        from simple_lama_inpainting import SimpleLama
        print("Loading Simple Lama Model...")
        self.lama = SimpleLama()

    @modal.method()
    def process_image(self, image_bytes, x, y, width, height, debug=False):
        import cv2
        import numpy as np
        from PIL import Image
        
        # Load image
        img_np = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        if img_np is None:
            raise ValueError("Invalid image file.")
            
        h, w = img_np.shape[:2]
        
        # Create mask
        mask = np.zeros((h, w), dtype=np.uint8)
        b_x1, b_y1 = max(0, x), max(0, y)
        b_x2, b_y2 = min(w, x + width), min(h, y + height)
        mask[b_y1:b_y2, b_x1:b_x2] = 255
        
        # Optimize by downscaling if image is too large (Faster inference)
        MAX_DIM = 512 # Reduced from 1280 for faster processing
        if max(h, w) > MAX_DIM:
            scale = MAX_DIM / max(h, w)
            new_w, new_h = int(w * scale), int(h * scale)
            img_np = cv2.resize(img_np, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
            mask = cv2.resize(mask, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
        
        if debug:
            # Just draw red box
            result = img_np.copy()
            cv2.rectangle(result, (b_x1, b_y1), (b_x2, b_y2), (0, 0, 255), 3)
        else:
            # Inpaint using SimpleLama
            # simple_lama takes PIL images
            img_pil = Image.fromarray(cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB))
            mask_pil = Image.fromarray(mask)
            
            result_pil = self.lama(img_pil, mask_pil)
            result = cv2.cvtColor(np.array(result_pil), cv2.COLOR_RGB2BGR)

        # Return as JPEG
        _, encoded = cv2.imencode('.jpg', result)
        return encoded.tobytes()

@app.function(image=image, timeout=3600, min_containers=1)
@modal.asgi_app()
def web():
    from fastapi import FastAPI, Request
    from fastapi.responses import StreamingResponse, JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    web_app = FastAPI()
    web_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

    @web_app.post("/api/proxy")
    async def proxy_process(request: Request):
        print("Received request at /api/proxy")
        try:
            form = await request.form()
            image_file = form.get("image_file")
            if not image_file:
                return JSONResponse(status_code=400, content={"error": "No image file provided."})
            
            image_bytes = await image_file.read()
            
            try:
                x = int(form.get("x", 0))
                y = int(form.get("y", 0))
                width = int(form.get("width", 100))
                height = int(form.get("height", 100))
                debug = form.get("debug") == "true"
            except (ValueError, TypeError) as e:
                return JSONResponse(status_code=400, content={"error": f"Invalid parameters: {str(e)}"})
                
            remover = WatermarkRemover()
            result_bytes = await remover.process_image.remote.aio(
                image_bytes, x, y, width, height, debug
            )
            return StreamingResponse(io.BytesIO(result_bytes), media_type="image/jpeg")
        except Exception as e:
            traceback.print_exc()
            return JSONResponse(status_code=500, content={"error": str(e)})

    from fastapi.staticfiles import StaticFiles
    web_app.mount("/", StaticFiles(directory="/dist", html=True), name="static")
    return web_app
