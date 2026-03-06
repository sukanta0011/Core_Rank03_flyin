# *********************************************
# *                                           *
# *           MLX related error               *
# *                                           *
# *********************************************

class MLXError(Exception):
    "Handle error related to base Mlx"
    pass

# *********************************************
# *                                           *
# *       Image related error handlers        *
# *                                           *
# *********************************************


class ImgError(MLXError):
    "Handle image creation errors"
    pass


class ParametersError(ImgError):
    "Handle error for wrong image dimensions"
    pass


class InitializationError(ImgError):
    "Handle error for image initialization"
    pass


class OperationError(ImgError):
    "Handle failure of any kind of image operation"
    pass
