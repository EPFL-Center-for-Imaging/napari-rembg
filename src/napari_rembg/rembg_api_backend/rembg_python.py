import numpy as np
import rembg
from skimage.exposure import rescale_intensity

def rembg_predict(image: np.ndarray, is_rgb: bool) -> np.ndarray:
    """Binary segmentation using rembg."""
    if not is_rgb:
        # Rescale the image to the range (0-255)
        image = rescale_intensity(image, out_range=(0, 255))

    return rembg.remove(
        image, 
        only_mask=True, 
        post_process_mask=True,
    ).copy()  # copy() makes the array writeable


def rembg_predict_sam(image: np.ndarray, is_rgb: bool, input_labels: np.ndarray, input_points: np.ndarray) -> np.ndarray:
    """Binary segmentation using rembg."""
    if not is_rgb:
        # Rescale the image to the range (0-255)
        image = rescale_intensity(image, out_range=(0, 255))

    sam_session = rembg.new_session(model_name='sam')

    prompt = [{"type": "point", "data": list(point), "label": int(label)} for point, label in zip(input_points, input_labels)]

    return rembg.remove(
        image, 
        only_mask=True, 
        post_process_mask=True,
        session=sam_session,
        sam_prompt=prompt
    ).copy()  # copy() makes the array writeable
