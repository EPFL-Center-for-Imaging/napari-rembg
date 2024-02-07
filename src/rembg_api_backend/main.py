import tifffile
import io
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

from rembg_python import rembg_predict

app = FastAPI()

def decode_contents(contents):
    image = tifffile.imread(io.BytesIO(contents))
    return image

def encode_contents(image):
    img_byte_array = io.BytesIO()
    tifffile.imwrite(img_byte_array, image)
    img_byte_array.seek(0)
    return img_byte_array

@app.get("/")
def read_root():
    return {"Hello": "world"}

@app.post("/process_image/")
async def upload_image(request: Request):
    contents = await request.body()
    image = decode_contents(contents)

    segmentation = rembg_predict(image, is_rgb=False)
    
    img_byte_array = encode_contents(segmentation)

    return StreamingResponse(img_byte_array, media_type="image/tif")