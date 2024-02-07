from ._rembg import rembg_predict
from ._generic_seg_widget import GenericSegWidget


class RemBGWidget(GenericSegWidget):
    def __init__(self, napari_viewer):
        super().__init__(napari_viewer)
    
    @property
    def segmentation_function(self):
        return rembg_predict