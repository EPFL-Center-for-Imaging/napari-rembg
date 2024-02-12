from .remote_predictor_widget import RemotePredictorWidget
try:
    from .local_predictor_widget import LocalPredictorWidget
except ImportError:
    pass
