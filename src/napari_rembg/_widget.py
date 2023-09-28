from typing import TYPE_CHECKING
import numpy as np
import PIL
import rembg
from napari.qt.threading import thread_worker
import napari.layers
from napari_tools_menu import register_dock_widget
from qtpy.QtWidgets import QComboBox, QGridLayout, QWidget, QSizePolicy, QLabel, QPushButton, QProgressBar
from qtpy.QtCore import Qt

if TYPE_CHECKING:
    import napari

def rembg_predict(image: np.ndarray) -> np.ndarray:
    """Binary segmentation using rembg."""
    seg = np.array(rembg.remove(PIL.Image.fromarray(image)))
    seg = np.mean(seg, axis=2)
    seg[seg != 0] = 1
    seg = seg.astype(np.uint8)
    return seg

@register_dock_widget(menu="RemBG > Select foreground")
class RemBGWidget(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        # Layout
        grid_layout = QGridLayout()
        grid_layout.setAlignment(Qt.AlignTop)
        self.setLayout(grid_layout)

        # Image
        self.cb_image = QComboBox()
        self.cb_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        grid_layout.addWidget(QLabel("Image (2D RGB or gray)", self), 0, 0)
        grid_layout.addWidget(self.cb_image, 0, 1)

        # Compute button
        self.remove_background_btn = QPushButton("Select foreground", self)
        self.remove_background_btn.clicked.connect(self._trigger_remove_background)
        grid_layout.addWidget(self.remove_background_btn, 1, 0, 1, 2)

        # Progress bar
        self.pbar = QProgressBar(self, minimum=0, maximum=1)
        self.pbar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        grid_layout.addWidget(self.pbar, 2, 0, 1, 2)

        # Setup layer callbacks
        self.viewer.layers.events.inserted.connect(
            lambda e: e.value.events.name.connect(self._on_layer_change)
        )
        self.viewer.layers.events.inserted.connect(self._on_layer_change)
        self.viewer.layers.events.removed.connect(self._on_layer_change)
        self._on_layer_change(None)

    def _on_layer_change(self, e):
        self.cb_image.clear()
        for x in self.viewer.layers:
            if isinstance(x, napari.layers.Image):
                if (len(x.data.shape) == 2) | x.rgb:
                    self.cb_image.addItem(x.name, x.data)

    @thread_worker
    def _remove_background(self) -> np.ndarray:
        self.image = self.cb_image.currentData()
        segmentation = rembg_predict(self.image)
        return segmentation
    
    def _trigger_remove_background(self):
        self.pbar.setMaximum(0)
        worker = self._remove_background()
        worker.returned.connect(self._thread_returned)
        worker.start()

    def _thread_returned(self, segmentation):
        self.viewer.add_labels(segmentation, name='mask')
        self.pbar.setMaximum(1)