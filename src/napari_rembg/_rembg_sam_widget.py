from ._rembg import rembg_predict_sam, rembg_predict
from ._generic_seg_widget import GenericSegWidget

from functools import partial

from qtpy.QtWidgets import  QGridLayout, QLabel, QGroupBox, QComboBox, QSizePolicy

import numpy as np
import napari.layers

class RemBGSAMWidget(GenericSegWidget):
    def __init__(self, napari_viewer):
        super().__init__(napari_viewer)
        self.points_layer = None

        sam_prompting_group = QGroupBox(self)
        sam_prompting_group.setTitle("SAM prompting")
        sam_layout = QGridLayout()
        sam_prompting_group.setLayout(sam_layout)
        sam_prompting_group.layout().setContentsMargins(10, 10, 10, 10)
        self.layout().addWidget(sam_prompting_group, 0, 0, 1, 2)

        # Points layer
        self.cb_points = QComboBox()
        self.cb_points.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sam_layout.addWidget(QLabel("Points", self), 0, 0)
        sam_layout.addWidget(self.cb_points, 0, 1)

        # Setup layer callbacks (Points)
        self.viewer.layers.events.inserted.connect(
            lambda e: e.value.events.name.connect(self._on_layer_change_points)
        )
        self.viewer.layers.events.inserted.connect(self._on_layer_change_points)
        self.viewer.layers.events.removed.connect(self._on_layer_change_points)
        self._on_layer_change_points(None)

        self.viewer.dims.events.current_step.connect(self._on_slice_change_points)

    def _on_layer_change_points(self, e):
        self.cb_points.clear()
        for x in self.viewer.layers:
            if isinstance(x, napari.layers.Points):
                if x.data.ndim in [2, 3]:
                    self.cb_points.addItem(x.name, x.data)
        
        if self.cb_points.currentText() != "":
            self.points_layer = self.viewer.layers[self.cb_points.currentText()]

    def _on_slice_change_points(self, event):
        if self.points_layer is not None:
            self.points_layer.data = []
            self.points_layer.refresh()

    @property
    def segmentation_function(self):

        input_points = self.points_layer.data
        input_labels = np.ones((len(input_points)))

        rembg_predict_sam_prompted = partial(
            rembg_predict_sam,
            input_labels=input_labels,
            input_points=input_points         
        )

        return rembg_predict_sam_prompted