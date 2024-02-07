import requests
import io
import tifffile

class SegmentationAPIClient():
    def __init__(self, endpoint=None) -> None:
        self._endpoint = endpoint
    
    @property
    def endpoint(self):
        return self._endpoint
    
    @endpoint.setter
    def endpoint(self, value):
        self._endpoint = value
        print(f'Set the API endpoint to {value}')

    def decode_contents(self, contents):
        image = tifffile.imread(io.BytesIO(contents))
        return image

    def encode_contents(self, image):
        img_byte_array = io.BytesIO()
        tifffile.imwrite(img_byte_array, image)
        img_byte_array.seek(0)
        return img_byte_array

    def predict_via_api(self, image):
        img_byte_array = self.encode_contents(image)
        response = requests.post(self._endpoint, data=img_byte_array)
        if response.status_code == 200:
            contents = self.decode_contents(response.content)
        else:
            print(f'{response.status_code=}')
            import sys; sys.exit(1)  # Is that too brutal?

        return contents