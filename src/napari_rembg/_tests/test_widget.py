from napari_rembg import RemBGWidget

def test_example_q_widget(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    widget = RemBGWidget(viewer)
    assert 1 == 1
