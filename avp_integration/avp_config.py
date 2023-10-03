# this class must have simple fields in order to be serialized
from core.config import Config


# this class must have simple fields in order to be serialized
class AVPConfig(Config):
    EVALUATOR_FAKE = 'EVALUATOR_FAKE'
    EVALUATOR_REAL = 'EVALUATOR_REAL'

    MIN_SPEED = 1
    MAX_SPEED = 10

    MIN_PED_ORIENTATION = 0
    MAX_PED_ORIENTATION = 360

    def __init__(self):
        super().__init__()

        self.evaluator = AVPConfig.EVALUATOR_FAKE
        self.generator_name = Config.GEN_RANDOM



