import random

import numpy as np
from deap import creator

from core.config import Config
from core.log_setup import get_logger
from core.misc import evaluate_sparseness
from core.archive import Archive
from core.individual import Individual
from avp_integration.avp_member import AVPMember

log = get_logger(__file__)

class AVPIndividual(Individual):
    counter = 0

    def __init__(self, m1: AVPMember, m2: AVPMember, config: Config, archive: Archive):
        super().__init__(m1, m2)
        self.m1: AVPMember = self.m1
        self.m2: AVPMember = self.m2
        AVPIndividual.counter += 1
        self.name = f'ind{str(AVPIndividual.counter)}'
        self.name_ljust = self.name.ljust(6)
        self.config = config
        self.archive = archive
        self.m1.parent = self
        self.m2.parent = self
        self.sparseness = None
        self.aggregate = None
        self.seed: AVPMember

    def evaluate(self):
        #self._assert_members_not_equals()

        import timeit

        start = timeit.default_timer()

        self.members_distance = self.m1.distance(self.m2)

        stop = timeit.default_timer()
        print('Time to mem dist: ', stop - start)

        self.sparseness = evaluate_sparseness(self, self.archive)

        stop = timeit.default_timer()
        print('Time to sparseness: '+ str(stop - start)+ 'archive len: '+ str(len(self.archive)))

        self.m1.evaluate()
        self.m2.evaluate()
        stop = timeit.default_timer()
        print('Time to eval: ', stop - start)

        border = self.m1.distance_to_boundary * self.m2.distance_to_boundary
        self.oob_ff = border if border > 0 else -0.1
        ff1 = self.sparseness - (self.config.K_SD * self.members_distance)

        log.info(f'evaluated {self}')

        stop = timeit.default_timer()
        print('Total Time: ', stop - start)

        return ff1, self.oob_ff

    def clone(self) -> 'AVPIndividual':
        res: AVPIndividual = creator.Individual(self.m1.clone(), self.m2.clone(), self.config, self.archive)
        res.seed = self.seed
        log.info(f'cloned to {res} from {self}')
        return res

    def semantic_distance(self, i2: 'AVPIndividual'):
        """
        this distance exploits the behavioral information (member.distance_to_boundary)
        so it will compare distances for members on the same boundary side
        :param i2: Individual
        :return: distance
        """
        i1 = self

        i1_posi, i1_nega = i1.members_by_sign()
        i2_posi, i2_nega = i2.members_by_sign()

        return np.mean([i1_posi.distance(i2_posi), i1_nega.distance(i2_nega)])

    # def _assert_members_not_equals(self):
    #     assert self.m1.orientation_ped != self.m2.orientation_ped

    def to_dict(self):
        return {'name': self.name,
                'members_distance': self.members_distance,
                'm1': self.m1.to_dict(),
                'm2': self.m2.to_dict(),
                'seed': self.seed.to_dict()}

    @classmethod
    def from_dict(self, d):
        m1 = AVPMember.from_dict(d['m1'])
        m2 = AVPMember.from_dict(d['m2'])
        ind = AVPIndividual(m1, m2, None, None)
        ind.members_distance = d['members_distance']
        ind.name = d['name']
        return ind

    def __str__(self):
        dist = str(self.members_distance).ljust(4)[:4]
        return f'{self.name_ljust} dist={dist} m1[{self.m1}] m2[{self.m2}] seed[{self.seed}]'

    def mutate(self):
        road_to_mutate = self.m1 if random.randrange(2) == 0 else self.m2
        condition = False
        while not condition:
            road_to_mutate.mutate()
            #if self.m1.distance(self.m2) != 0.0:
            #if self.m1.control_nodes != self.m2.control_nodes:
            condition = True
        self.members_distance = None
        log.info(f'mutated {road_to_mutate}')
