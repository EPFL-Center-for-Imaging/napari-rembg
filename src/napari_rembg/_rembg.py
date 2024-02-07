import rembg

def rembg_predict(image):
    """Binary segmentation using rembg."""
    return rembg.remove(
        image, 
        only_mask=True, 
        post_process_mask=True,
    ).copy()  # copy() makes the array writeable


def rembg_predict_sam(image, input_labels=None, input_points=None):
    """Binary segmentation using rembg."""
    sam_session = rembg.new_session(model_name='sam')

    prompt = [{"type": "point", "data": list(point), "label": int(label)} for point, label in zip(input_points, input_labels)]

    return rembg.remove(
        image, 
        only_mask=True, 
        post_process_mask=True,
        session=sam_session,
        sam_prompt=prompt
    ).copy()  # copy() makes the array writeable
