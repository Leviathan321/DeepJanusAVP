import logging as log
import os
from typing import List, Tuple
from avp_integration.avp_evaluator import AVPEvaluator
from avp_integration.avp_member import AVPMember

from core.folder_storage import SeedStorage
from core.folders import folders
from core.log_setup import get_logger
from dummy.simulation.simulator import SimulationOutput
from dummy.evaluation import critical
from dummy.evaluation import fitness
from dummy.simulation import dummy_simulation
from avp_integration.avp_config import *

log = get_logger(__file__)

FloatDTuple = Tuple[float, float, float, float]


class AVP_Dummy_Evaluator(AVPEvaluator):
    def __init__(self, config: AVPConfig):
        self.config = config
        # self.brewer: BeamNGBrewer = None
        # self.model_file = str(folders.trained_models_colab.joinpath(config.keras_model_file))
        # if not os.path.exists(self.model_file):
        #     raise Exception(f'File {self.model_file} does not exist!')
        # self.model = None

    def evaluate(self, members: List[AVPMember]):

        for member in members:
            if not member.needs_evaluation():
                log.info(f'{member} is already evaluated. skipping')
                continue
            
            scenario = [member.velocity_ego, member.velocity_ped, member.orientation_ped]
            simout = self._run_simulation([scenario])
            ff_value = fitness.FitnessMinDistanceVelocityWeighted().eval(simout[0])
        
            # convert into one fitness value

            member.distance_to_boundary = ff_value
            member.simout = simout

            log.info(f'{member} AVP evaluation completed')
            log.info(f'distance to boundary set as: {ff_value}')

    def _run_simulation(self, scenario) -> SimulationOutput:

        simout = dummy_simulation.DummySimulator.simulate(scenario, 
                                                          variable_names=["vel_ego", "vel_ped", "orient_ped"],
                                                          scenario_path="",
                                                          sim_time=10)

        return simout

    # def end_iteration(self):
    #     try:
    #         if self.config.beamng_close_at_iteration:
    #             self._close()
    #         else:
    #             if self.brewer:
    #                 self.brewer.beamng.stop_scenario()
    #     except Exception as ex:
    #         log.debug('end_iteration() failed:')
    #         traceback.print_exception(type(ex), ex, ex.__traceback__)

    # def _close(self):
    #     if self.brewer:
    #         try:
    #             self.brewer.beamng.close()
    #         except Exception as ex:
    #             log.debug('beamng.close() failed:')
    #             traceback.print_exception(type(ex), ex, ex.__traceback__)
    #         self.brewer = None

# if __name__ == '__main__':
#     config = BeamNGConfig()
#     inst = AVP_Dummy_Evaluator(config)
#     while True:
#         seed_storage = SeedStorage('basic5')
#         for i in range(1, 11):
#             member = AVPMember.from_dict(seed_storage.load_json_by_index(i))
#             member.clear_evaluation()
#             inst.evaluate([member])
#             log.info(member)
