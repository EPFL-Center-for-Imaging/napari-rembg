import numpy as np

from napari.qt.threading import thread_worker
import napari
import napari.layers
from qtpy.QtWidgets import (
    QComboBox,
    QGridLayout,
    QWidget,
    QSizePolicy,
    QLabel,
    QPushButton,
    QProgressBar,
    QCheckBox,
)
from napari.utils.notifications import show_error
from qtpy.QtCore import Qt

from skimage.exposure import rescale_intensity

from typing import Optional, List, Callable

MODELS = ["u2net", "u2netp", "sam", "silueta", "isnet-general-use"]


class BaseSegmentationWidget(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        self.image_layer = None
        self.labels_layer = None
        self.shapes_layer = None

        # Layout
        grid_layout = QGridLayout()
        grid_layout.setAlignment(Qt.AlignTop)
        self.setLayout(grid_layout)

        # Model selection
        self.cb_model_name = QComboBox()
        self.cb_model_name.addItems(MODELS)
        self.cb_model_name.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed
        )
        grid_layout.addWidget(QLabel("Model", self), 1, 0)
        grid_layout.addWidget(self.cb_model_name, 1, 1)

        # Image
        self.cb_image = QComboBox()
        self.cb_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        grid_layout.addWidget(QLabel("Image (2D / 3D / RGB)", self), 2, 0)
        grid_layout.addWidget(self.cb_image, 2, 1)

        # Result
        self.cb_mask = QComboBox()
        self.cb_mask.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        grid_layout.addWidget(QLabel("Mask (Labels, optional)", self), 3, 0)
        grid_layout.addWidget(self.cb_mask, 3, 1)

        # Regions of interest
        self.cb_roi = QComboBox()
        self.cb_roi.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        grid_layout.addWidget(QLabel("ROI (Shapes, optional)", self), 4, 0)
        grid_layout.addWidget(self.cb_roi, 4, 1)
        self.create_roi_layer_btn = QPushButton("Add", self)
        self.create_roi_layer_btn.clicked.connect(self._create_roi_layer)
        grid_layout.addWidget(self.create_roi_layer_btn, 4, 2)

        # Auto-increment labels
        grid_layout.addWidget(QLabel("Auto-increment label index", self), 5, 0)
        self.check_label_increment = QCheckBox()
        self.check_label_increment.setChecked(True)
        grid_layout.addWidget(self.check_label_increment, 5, 1)

        # Run button
        self.run_btn = QPushButton("Run", self)
        self.run_btn.clicked.connect(self._trigger_remove_background)
        grid_layout.addWidget(self.run_btn, 6, 0, 1, 2)

        # Progress bar
        self.pbar = QProgressBar(self, minimum=0, maximum=1)
        self.pbar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        grid_layout.addWidget(self.pbar, 7, 0, 1, 2)

        # Layer callbacks
        self.viewer.layers.events.inserted.connect(
            lambda e: e.value.events.name.connect(self._on_layer_change)
        )
        self.viewer.layers.events.inserted.connect(self._on_layer_change)
        self.viewer.layers.events.removed.connect(self._on_layer_change)
        self._on_layer_change(None)

    @property
    def image_data(self) -> Optional[np.ndarray]:
        """The image data."""
        if self.image_layer is None:
            return

        if self.image_layer.data is None:
            return

        return self.image_layer.data

    @property
    def is_in_3d_view(self) -> bool:
        return self.viewer.dims.ndisplay == 3

    @property
    def dims_displayed(self) -> List:
        return list(self.viewer.dims.displayed)

    @property
    def ndim(self) -> Optional[int]:
        if self.image_data is None:
            return

        if self.image_layer.rgb is True:
            return 2
        else:
            return self.image_layer.data.ndim

    @property
    def axes(self) -> Optional[List]:
        if self.is_in_3d_view:
            return

        axes = self.dims_displayed
        if self.ndim == 3:
            axes.insert(
                0, list(set(range(self.ndim)) - set(self.dims_displayed))[0]
            )

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
            if self.image_layer.rgb:
                return self.image_data
            else:
                return rescale_intensity(
                    self.image_data, out_range=(0, 255)
                ).astype(np.uint8)

        elif self.ndim == 3:
            data_slice = self.image_data.transpose(self.axes)[
                self.current_step
            ]
            return rescale_intensity(data_slice, out_range=(0, 255)).astype(
                np.uint8
            )

    @property
    def selected_label(self):
        if self.labels_layer is None:
            return 1

        return self.labels_layer.selected_label

    @selected_label.setter
    def selected_label(self, selected_label):
        if self.labels_layer is None:
            return

        self.labels_layer.selected_label = selected_label
        self.labels_layer.refresh()

    def segmentation_function(
        self, image: np.ndarray, model_name: str
    ) -> Callable:
        raise NotImplementedError

    def _create_roi_layer(self):
        """Create a Shapes Layer to draw a bounding box for the segmentation."""
        self.shapes_layer = self.viewer.add_shapes(
            data=None,
            shape_type="rectangle",
            edge_width=2,
            edge_color="red",
            face_color="transparent",
            name="ROIs (draw rectangles)",
            ndim=self.ndim,
        )
        self.shapes_layer.mode = "add_rectangle"
        self.shapes_layer.refresh()

        # Add a call to trigger the segmentation when new rectangles are drawn.
        self.shapes_layer.events.data.connect(self._handle_rectangle_drawn)

    def _handle_rectangle_drawn(self, e):
        """Trigger the segmentation when the bounding box is drawn."""
        if e.source.nshapes > 0:
            self._trigger_remove_background()

    def _on_layer_change(self, e):
        self.cb_image.clear()
        for x in self.viewer.layers:
            if isinstance(x, napari.layers.Image):
                if x.data.ndim in [2, 3]:
                    self.cb_image.addItem(x.name, x.data)

        if self.cb_image.currentText() != "":
            self.image_layer = self.viewer.layers[self.cb_image.currentText()]

        self.cb_mask.clear()
        for x in self.viewer.layers:
            if isinstance(x, napari.layers.Labels):
                self.cb_mask.addItem(x.name, x.data)

        if self.cb_mask.currentText() != "":
            self.labels_layer = self.viewer.layers[self.cb_mask.currentText()]

        self.cb_roi.clear()
        for x in self.viewer.layers:
            if isinstance(x, napari.layers.Shapes):
                self.cb_roi.addItem(x.name, x.data)

        if self.cb_roi.currentText() != "":
            self.shapes_layer = self.viewer.layers[self.cb_roi.currentText()]

    @thread_worker
    def _remove_background(self) -> np.ndarray:
        rx, ry = self.image_data_slice.shape[:2]

        if self.shapes_layer is not None:
            if self.shapes_layer.nshapes == 0:
                return

            shapes_data = self.shapes_layer.data[0].astype(int)
            if self.ndim == 3:
                shapes_data = shapes_data[:, self.axes][:, 1:]

            # Top-left corner
            x0, y0 = shapes_data[np.argmin(np.sum(shapes_data, axis=1))]

            # Bottom-right corner
            x1, y1 = shapes_data[np.argmax(np.sum(shapes_data, axis=1))]

        else:
            x0, y0, x1, y1 = 0, 0, rx, ry

        # Clip the bounding box if it is outside the image limits
        x0 = max(x0, 0)
        y0 = max(y0, 0)
        x1 = min(x1, rx)
        y1 = min(y1, ry)

        segmentation = np.zeros((rx, ry), dtype=np.uint8)
        segmentation_output = self.segmentation_function(
            image=self.image_data_slice[x0:x1, y0:y1],
            model_name=self.cb_model_name.currentText(),
        )
        if segmentation_output is not None:
            segmentation[x0:x1, y0:y1] = segmentation_output*self.selected_label

            # Increment the label index
            if self.check_label_increment.isChecked():
                self.selected_label = self.selected_label + 1
        else:
            show_error('Something went wrong with this API.')

        # Remove the shapes data
        if self.shapes_layer is not None:
            self.shapes_layer.data = []

        self.pbar.setMaximum(1)

        return segmentation

    def _trigger_remove_background(self):
        if self.is_in_3d_view:
            return

        if self.cb_image.currentText() == "":
            return

        self.image_layer = self.viewer.layers[self.cb_image.currentText()]

        if self.cb_roi.currentText() != "":
            self.shapes_layer = self.viewer.layers[self.cb_roi.currentText()]
        else:
            self.shapes_layer = None

        if self.cb_mask.currentText() == "":
            if self.image_layer.rgb is True:
                rx, ry = self.image_data.shape[:2]
                self.labels_layer = self.viewer.add_labels(
                    np.zeros((rx, ry), dtype=np.int_),
                    name="Foreground mask",
                )
            else:
                self.labels_layer = self.viewer.add_labels(
                    np.zeros_like(self.image_data, dtype=np.int_),
                    name="Foreground mask",
                )
        else:
            self.labels_layer = self.viewer.layers[self.cb_mask.currentText()]

        self.pbar.setMaximum(0)

        worker = self._remove_background()
        worker.returned.connect(self._thread_returned)
        worker.start()

    def _thread_returned(self, segmentation):
        if segmentation is not None:
            if self.ndim == 2:
                self.labels_layer.data += segmentation
            elif self.ndim == 3:
                self.labels_layer.data.transpose(self.axes)[
                    self.current_step
                ] += segmentation

            self.labels_layer.refresh()

            if self.shapes_layer is not None:
                self.viewer.layers.selection.active = self.shapes_layer

            self.pbar.setMaximum(1)
