import requests
import io
from PIL import Image
import numpy as np
import json


class SegmentationAPIClient:
    def __init__(self, endpoint=None) -> None:
        self._endpoint = endpoint

    @property
    def endpoint(self):
        return self._endpoint

    @endpoint.setter
    def endpoint(self, value):
        self._endpoint = value

    def _decode_contents(self, contents):
        return np.asarray(Image.open(io.BytesIO(contents)))
    
    def _encode_contents(self, image):
        if len(image.shape) == 2:
            image = np.repeat(image[..., None], 3, axis=-1)

        pil_image = Image.fromarray(image)
        buffer = io.BytesIO()
        pil_image.save(buffer, format='PNG')
        buffer.seek(0)

        return {'file': ('image.png', buffer, 'image/png')}

    def predict_via_api(self, image: np.ndarray, model_name: str="u2net"):
        files = self._encode_contents(image)
        
        if model_name == 'sam':
            x0, y0, x1, y1 = 0, 0, image.shape[0], image.shape[1]

            prompt = [
                {
                    "type": "rectangle",
                    "data": [y0, x0, y1, x1],  # Has to be inverted in XY
                    "label": 2  # Irrelevant for sam with bounding boxes
                }
            ]
            try:
                response = requests.post(
                    self._endpoint, 
                    files=files, 
                    data={
                        "model": model_name,
                        "om": True,  # Only mask
                        "ppm": True,  # Post-process mask
                    },
                    params={
                        "extras": json.dumps({"sam_prompt": prompt})
                    }
                )
            except:
                print(f"Could not connect to this endpoint: {self._endpoint}")
                return
        else:
            try:
                response = requests.post(
                    self._endpoint, 
                    files=files, 
                    data={
                        "model": model_name,
                        "om": True,  # Only mask
                        "ppm": True  # Post-process mask
                    }
                )
            except:
                print(f"Could not connect to this endpoint: {self._endpoint}")
                return

        if response.status_code == 200:
            segmentation = self._decode_contents(response.content)
            if model_name == 'sam':
                segmentation = (segmentation == 0) # Invert it (for some reason)
            else:
                segmentation = (segmentation == 255)
        else:
            print(f"Unsuccessful status: {response.status_code=}")
            return

        segmentation = segmentation.astype(np.uint8)

        return segmentation


if __name__=='__main__':
    client = SegmentationAPIClient(endpoint="http://localhost:7000/api/remove")

    image = np.asarray(Image.open('./data/car-1.jpg'))
    print(f"{image.shape=}")

    out = client.predict_via_api(image, model_name='sam')
    print(f"{out.shape=}")