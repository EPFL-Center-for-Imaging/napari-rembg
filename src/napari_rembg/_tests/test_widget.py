from napari_rembg import LocalPredictorWidget

def test_example_q_widget(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    widget = LocalPredictorWidget(viewer)
    assert 1 == 1
