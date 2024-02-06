import requests
import io
import tifffile

def decode_contents(contents):
    image = tifffile.imread(io.BytesIO(contents))
    return image

def encode_contents(image):
    img_byte_array = io.BytesIO()
    tifffile.imwrite(img_byte_array, image)
    img_byte_array.seek(0)
    return img_byte_array

def rembg_predict_via_api(image, endpoint, is_rgb: False):
    img_byte_array = encode_contents(image)
    response = requests.post(endpoint, data=img_byte_array)
    print(f'{response.status_code=}')
    if response.status_code == 200:
        contents = decode_contents(response.content)
    else:
        print(f'{response.status_code=}')
        import sys; sys.exit(1)

    return contents