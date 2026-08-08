class PipelineError(Exception):
    """Base class for exceptions in this module."""
    pass

class ExtractStageError(PipelineError):
    """Exception raised for errors in the extract stage of the pipeline."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
class TransformStageError(PipelineError):
    """Exception raised for errors in the transform stage of the pipeline."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class QualityCheckError(PipelineError):
    """Exception raised for errors in the quality check stage of the pipeline."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
 
class LoadStageError(PipelineError):
    """Exception raised for errors in the load stage of the pipeline."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)