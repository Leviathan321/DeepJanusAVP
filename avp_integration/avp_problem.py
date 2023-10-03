import itertools
import json
import random
from typing import List

from core.archive import Archive
from core.folders import folders
from core.log_setup import get_logger
from core.member import Member
from core.metrics import get_diameter, get_radius_seed
from core.misc import delete_folder_recursively
from core.problem import Problem
from core.seed_pool_access_strategy import SeedPoolAccessStrategy
from core.seed_pool_impl import SeedPoolFolder, SeedPoolRandom
from deap import creator

from avp_integration.avp_config import AVPConfig
from avp_integration.avp_evaluator import AVPEvaluator
from avp_integration.avp_individual import AVPIndividual
from avp_integration.avp_individual_set_store import AVPIndividualSetStore
from avp_integration.avp_member import AVPMember
from avp_integration.scenario_generator import ScenarioGenerator

log = get_logger(__file__)

class AVPProblem(Problem):
    def __init__(self, config: AVPConfig, archive: Archive):
        #self.config: BeamNGConfig = config
        self._evaluator: AVPEvaluator = None
        super().__init__(config, archive)
        if self.config.generator_name == self.config.GEN_RANDOM:
            seed_pool = SeedPoolRandom(self, config.POPSIZE)
        else:
            seed_pool = SeedPoolFolder(self, config.seed_folder)
        self._seed_pool_strategy = SeedPoolAccessStrategy(seed_pool)
        self.experiment_path = folders.experiments.joinpath(self.config.experiment_name)
        delete_folder_recursively(self.experiment_path)

    def deap_generate_individual(self):
        seed = self._seed_pool_strategy.get_seed()
        scenario1 = seed.clone()
        scenario2 = seed.clone().mutate()
        scenario1.config = self.config
        scenario2.config = self.config
        individual: AVPIndividual = creator.Individual(scenario1, scenario2, self.config, self.archive)
        individual.seed = seed
        log.info(f'generated {individual}')

        return individual

    def deap_evaluate_individual(self, individual: AVPIndividual):
        return individual.evaluate()

    def on_iteration(self, idx, pop: List[AVPIndividual], logbook):
        # self.archive.process_population(pop)

        self.experiment_path.mkdir(parents=True, exist_ok=True)
        self.experiment_path.joinpath('config.json').write_text(json.dumps(self.config.__dict__))

        gen_path = self.experiment_path.joinpath(f'gen{idx}')
        gen_path.mkdir(parents=True, exist_ok=True)

        # Generate final report at the end of the last iteration.
        if idx + 1 == self.config.NUM_GENERATIONS:
            report = {
                'archive_len': len(self.archive),
                'radius': get_radius_seed(self.archive),
                'diameter_out': get_diameter([ind.members_by_sign()[0] for ind in self.archive]),
                'diameter_in': get_diameter([ind.members_by_sign()[1] for ind in self.archive])
            }
            gen_path.joinpath(f'report{idx}.json').write_text(json.dumps(report))

        AVPIndividualSetStore(gen_path.joinpath('population')).save(pop)
        # AVPIndividualSetStore(gen_path.joinpath('archive')).save(self.archive)

    def generate_random_member(self) -> Member:
        result = ScenarioGenerator().generate()
        result.config = self.config
        result.problem = self
        return result

    def deap_individual_class(self):
        return AVPIndividual

    def member_class(self):
        return AVPMember

    def reseed(self, pop, offspring):
        if len(self.archive) > 0:
            stop = self.config.RESEED_UPPER_BOUND + 1
            seed_range = min(random.randrange(0, stop), len(pop))
            #log.info(f'reseed{seed_range}')
            #for i in range(0, seed_range):
            #    ind1 = self.deap_generate_individual()
            #    rem_idx = -(i + 1)
            #    log.info(f'reseed rem {pop[rem_idx]}')
            #    pop[rem_idx] = ind1
            archived_seeds = [i.seed for i in self.archive]
            for i in range(len(pop)):
                if pop[i].seed in archived_seeds:
                    ind1 = self.deap_generate_individual()
                    log.info(f'reseed rem {pop[i]}')
                    pop[i] = ind1

    def _get_evaluator(self):
        if self._evaluator:
            return self._evaluator
        ev_name = self.config.evaluator
        if ev_name == AVPConfig.EVALUATOR_FAKE:
            from avp_integration.avp_dummy_evaluator import AVP_Dummy_Evaluator
            self._evaluator = AVP_Dummy_Evaluator(self.config)
        # elif ev_name == AVPConfig.EVALUATOR_REAL:
        #     from avp_integration.avp_real_evaluator import AVP_Prescan_Evaluator
        #     self._evaluator = AVP_Prescan_Evaluator(self.config)
        else:
            raise NotImplemented()

        return self._evaluator

    def pre_evaluate_members(self, individuals: List[AVPIndividual]):
        # return
        # the following code does not work as wanted or expected!
        all_members = list(itertools.chain(*[(ind.m1, ind.m2) for ind in individuals]))
        log.info('----evaluation warmup')
        self._get_evaluator().evaluate(all_members)
        log.info('----warmpup completed')
