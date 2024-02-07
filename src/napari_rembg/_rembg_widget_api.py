from qtpy.QtWidgets import  QGridLayout, QLabel, QGroupBox, QLineEdit, QSpinBox

from ._api_client import SegmentationAPIClient
from ._generic_seg_widget import GenericSegWidget

class RemBGWidgetAPI(GenericSegWidget):
    def __init__(self, napari_viewer):
        super().__init__(napari_viewer)

        self.segmentation_api_client = SegmentationAPIClient()

        api_group = QGroupBox(self)
        api_group.setTitle("API settings")
        api_layout = QGridLayout()
        api_group.setLayout(api_layout)
        api_group.layout().setContentsMargins(10, 10, 10, 10)
        self.layout().addWidget(api_group, 0, 0, 1, 2)

        api_layout.addWidget(QLabel("Network", self), 0, 0)
        self.network_field = QLineEdit(self)
        self.network_field.setText('localhost')
        api_layout.addWidget(self.network_field, 0, 1)

        api_layout.addWidget(QLabel("Port", self), 1, 0)
        self.port_field = QSpinBox(self)
        self.port_field.setMinimum(1000)
        self.port_field.setMaximum(100000)
        self.port_field.setValue(8000)
        api_layout.addWidget(self.port_field, 1, 1)

    @property
    def segmentation_function(self):
        network = self.network_field.text()
        port = self.port_field.value()
        self.segmentation_api_client.endpoint = f'http://{network}:{port}/process_image/'
        return self.segmentation_api_client.predict_via_api