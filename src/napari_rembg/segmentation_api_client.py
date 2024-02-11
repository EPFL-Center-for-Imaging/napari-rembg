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
            # image = image.astype(np.uint8)
        # print(image.shape, image.dtype)
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
            
            response = requests.post(
                self._endpoint, 
                files=files, 
                data={
                    "model": model_name,
                    "om": True,  # Only mask
                    "ppm": True,  # Post-process mask
                },
                params={
                    "bgc": "255,255,128,0",
                    "extras": json.dumps({"sam_prompt": prompt})
                }
            )
        else:
            response = requests.post(
                self._endpoint, 
                files=files, 
                data={
                    "model": model_name,
                    "om": True,  # Only mask
                    "ppm": True  # Post-process mask
                }
            )


        if response.status_code == 200:
            contents = self._decode_contents(response.content)
            if model_name == 'sam':
                contents = (contents == 0).astype(np.uint8) # Invert it (for some reason)
        else:
            print(f"{response.status_code=}")
            import sys

            sys.exit(1)  # Is that too brutal?

        return contents


if __name__=='__main__':
    client = SegmentationAPIClient(endpoint="http://localhost:7000/api/remove")

    image = np.asarray(Image.open('/home/wittwer/code/napari_plugins/napari-rembg/data/car-1.jpg'))
    # image = np.mean(image, axis=-1).astype(np.uint8)
    print(f"{image.shape=}")

    out = client.predict_via_api(image, model_name='sam')
    print(f"{out.shape=}")