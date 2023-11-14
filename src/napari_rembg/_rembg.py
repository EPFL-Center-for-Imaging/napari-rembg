import numpy as np
import rembg
import PIL
from skimage.exposure import rescale_intensity

def rembg_predict(image: np.ndarray, is_rgb: bool) -> np.ndarray:
    """Binary segmentation using rembg."""
    if not is_rgb:
        # Rescale the image to the range (0-255)
        image = rescale_intensity(image, out_range=(0, 255))
    
    seg = np.array(rembg.remove(PIL.Image.fromarray(image), post_process_mask=True))
    seg = np.mean(seg, axis=2)
    seg[seg != 0] = 1
    seg = seg.astype(np.uint8)
    return seg