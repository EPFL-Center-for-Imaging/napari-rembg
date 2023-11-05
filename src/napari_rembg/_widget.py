from typing import TYPE_CHECKING
import numpy as np
import PIL
import rembg
from napari.qt.threading import thread_worker
import napari.layers
from qtpy.QtWidgets import QComboBox, QGridLayout, QWidget, QSizePolicy, QLabel, QPushButton, QProgressBar
from qtpy.QtCore import Qt

if TYPE_CHECKING:
    import napari

def rembg_predict(image: np.ndarray) -> np.ndarray:
    """Binary segmentation using rembg."""
    seg = np.array(rembg.remove(PIL.Image.fromarray(image), post_process_mask=True))
    seg = np.mean(seg, axis=2)
    seg[seg != 0] = 1
    seg = seg.astype(np.uint8)
    return seg

class RemBGWidget(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        self.image_layer = None
        self.labels_layer = None

        # Layout
        grid_layout = QGridLayout()
        grid_layout.setAlignment(Qt.AlignTop)
        self.setLayout(grid_layout)

        # Image
        self.cb_image = QComboBox()
        self.cb_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        grid_layout.addWidget(QLabel("Image (2D / 3D / RGB)", self), 0, 0)
        grid_layout.addWidget(self.cb_image, 0, 1)

        # Result
        self.cb_result = QComboBox()
        self.cb_result.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        grid_layout.addWidget(QLabel("Labels (optional)", self), 1, 0)
        grid_layout.addWidget(self.cb_result, 1, 1)

        # Compute button
        self.remove_background_btn = QPushButton("Select foreground", self)
        self.remove_background_btn.clicked.connect(self._trigger_remove_background)
        grid_layout.addWidget(self.remove_background_btn, 2, 0, 1, 2)

        # Progress bar
        self.pbar = QProgressBar(self, minimum=0, maximum=1)
        self.pbar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        grid_layout.addWidget(self.pbar, 3, 0, 1, 2)

        # Setup layer callbacks
        self.viewer.layers.events.inserted.connect(
            lambda e: e.value.events.name.connect(self._on_layer_change)
        )
        self.viewer.layers.events.inserted.connect(self._on_layer_change)
        self.viewer.layers.events.removed.connect(self._on_layer_change)
        self._on_layer_change(None)

        # import skimage.data; self.viewer.add_image(skimage.data.brain())

    @property
    def image_data(self):
        """The image data, adjusted to handle the RGB case."""
        if self.image_layer is None:
            return
        
        if self.image_layer.data is None:
            return

        return self.image_layer.data
    
    @property
    def is_in_3d_view(self):
        return self.viewer.dims.ndisplay == 3

    @property
    def dims_displayed(self):
        return list(self.viewer.dims.displayed)
    
    @property
    def ndim(self):        
        if self.image_data is None:
            return
        
        if self.image_layer.rgb is True:
            return 2
        else:
            return self.image_layer.data.ndim
    
    @property
    def axes(self):
        if self.is_in_3d_view:
            return
        
        axes = self.dims_displayed
        if self.ndim == 3:
            axes.insert(0, list(set([0, 1, 2]) - set(self.dims_displayed))[0])
        
        return axes
    
    @property
    def current_step(self):
        """Current step, adjusted based on the layer transpose state."""
        return np.array(self.viewer.dims.current_step)[self.axes][0]
    
    @property
    def image_data_slice(self):
        """The currently visible 2D slice if the image is 3D, otherwise the image itself (if 2D)."""      
        if self.image_data is None:
            return
        
        if self.ndim == 2:
            return self.image_data
        
        elif self.ndim == 3:
            return self.image_data.transpose(self.axes)[self.current_step]
    
    @property
    def selected_label(self):
        if self.labels_layer is None:
            return
        
        return self.labels_layer.selected_label
    
    def _on_layer_change(self, e):
        self.cb_image.clear()
        for x in self.viewer.layers:
            if isinstance(x, napari.layers.Image):
                if x.data.ndim in [2, 3]:
                    self.cb_image.addItem(x.name, x.data)
        
        self.cb_result.clear()
        for x in self.viewer.layers:
            if isinstance(x, napari.layers.Labels):
                self.cb_result.addItem(x.name, x.data)

    @thread_worker
    def _remove_background(self) -> np.ndarray:
        segmentation = rembg_predict(self.image_data_slice)
        return segmentation
    
    def _trigger_remove_background(self):
        if self.cb_image.currentText() == '':
            return
        
        if self.is_in_3d_view:
            return
        
        self.image_layer = self.viewer.layers[self.cb_image.currentText()]

        self.pbar.setMaximum(0)
        worker = self._remove_background()
        worker.returned.connect(self._thread_returned)
        worker.start()

    def _thread_returned(self, segmentation):
        if self.cb_result.currentText() == '':
            if self.image_layer.rgb is True:
                self.labels_layer = self.viewer.add_labels(np.zeros_like(np.mean(self.image_data, axis=2), dtype=np.int_), name='Foreground mask')
            else:
                self.labels_layer = self.viewer.add_labels(np.zeros_like(self.image_data, dtype=np.int_), name='Foreground mask')
        else:
            self.labels_layer = self.viewer.layers[self.cb_result.currentText()]

        mask = segmentation > 0

        if self.ndim == 2:
            self.labels_layer.data[mask] = self.selected_label
        elif self.ndim == 3:
            self.labels_layer.data.transpose(self.axes)[self.current_step][mask] = self.selected_label

        self.labels_layer.refresh()

        self.pbar.setMaximum(1)