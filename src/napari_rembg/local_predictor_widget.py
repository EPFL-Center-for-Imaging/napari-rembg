from ._rembg import rembg_predict
from ._base_segmentation_widget import BaseSegmentationWidget

class LocalPredictorWidget(BaseSegmentationWidget):
    def __init__(self, napari_viewer):
        super().__init__(napari_viewer)
    
    @property
    def segmentation_function(self):
        return rembg_predict