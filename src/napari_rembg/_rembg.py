import rembg
import numpy as np

# We keep the sessions open if the user switches model
sessions: dict[str, rembg.sessions.BaseSession] = {}


def rembg_predict(image: np.ndarray, model_name: str) -> np.ndarray:
    """
    Wrapper function around `rembg.remove` - handling both SAM and regular models.
    """
    session = sessions.setdefault(model_name, rembg.new_session(model_name))

    if model_name == "sam":
        x0, y0, x1, y1 = 0, 0, image.shape[0], image.shape[1]

        prompt = [
            {
                "type": "rectangle",
                "data": [y0, x0, y1, x1],
                "label": 2,  # `label` is irrelevant for SAM in bounding boxes mode
            }
        ]

        segmentation = rembg.remove(
            data=image,
            session=session,
            only_mask=True,
            post_process_mask=True,
            sam_prompt=prompt,
        )
        segmentation = (segmentation == 0)  # Invert it (for some reason)

    else:
        segmentation = rembg.remove(
            data=image,
            session=session,
            only_mask=True,
            post_process_mask=True,
        )
        segmentation = (segmentation == 255)

    segmentation = segmentation.astype(np.uint8)

    return segmentation
