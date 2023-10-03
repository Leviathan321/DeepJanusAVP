import hashlib
import random
from typing import Tuple, Dict
from avp_integration.avp_problem import *
from avp_integration.avp_config import AVPConfig
from avp_integration.avp_evaluator import AVPEvaluator
from core.member import Member
from self_driving.edit_distance_polyline import iterative_levenshtein
from dummy.simulation.simulator import SimulationOutput
from pymoo.operators.mutation.pm import *
import numpy as np
from pymoo.core.population import *

Tuple4F = Tuple[float, float, float, float]
Tuple2F = Tuple[float, float]
Tuple3F = Tuple[float, float, float]



class AVPMember(Member):
    counter = 0

    def __init__(self, 
                orientation_ped: float, 
                velocity_ego: float,
                velocity_ped: float):
        super().__init__()
        AVPMember.counter += 1
        self.name = f'mbr{str(AVPMember.counter)}'
        self.name_ljust = self.name.ljust(7)
        self.vars = []
        self.config: AVPConfig = None
        self.problem: 'AVPProblem' = None
        self.simout: SimulationOutput = None
        self._evaluator: AVPEvaluator = None
        self.orientation_ped = orientation_ped # temporary
        self.velocity_ped = velocity_ped
        self.velocity_ego = velocity_ego
        self.distance_to_boundary = None

    def clone(self):
        res = AVPMember(self.orientation_ped, self.velocity_ego, self.velocity_ped)
        res.config = self.config
        res.problem = self.problem
        res.distance_to_boundary = self.distance_to_boundary
        res.simout = self.simout
        return res

    def to_dict(self) -> dict:
        return {
            'velocity_ego' : self.velocity_ego,
            'velocity_ped' : self.velocity_ped,
            'orientation_ped' : self.orientation_ped
        }

    @classmethod
    def from_dict(cls, dict: Dict):
        res = AVPMember(dict['distance_to_boundary'],
                        dict['orientation_ped'],
                        dict['velocity_ego'],
                        dict['velocity_ped'])
        res.distance_to_boundary = dict['distance_to_boundary']
        res.simout = dict['simout']
        return res

    def evaluate(self):
        if self.needs_evaluation():
            self.problem._get_evaluator().evaluate([self])
            print('eval mbr', self)

        assert not self.needs_evaluation()

    def needs_evaluation(self):
        return self.distance_to_boundary is None

    def clear_evaluation(self):
        self.distance_to_boundary = None
        self.simout = None

    # def is_valid(self):
    #     return (RoadPolygon.from_nodes(self.sample_nodes).is_valid() and
    #             self.road_bbox.contains(RoadPolygon.from_nodes(self.control_nodes[1:-1])))

    def distance(self, other: 'AVPMember'):
        return abs(self.velocity_ego - other.velocity_ego) + \
               + abs(self.velocity_ped - other.velocity_ped) + \
               + abs(self.orientation_ped - other.orientation_ped)

        # return frechet_dist(self.sample_nodes, other.sample_nodes)
        # return iterative_levenshtein(self.sample_nodes, other.sample_nodes)
        # return iterative_levenshtein(
        #                              [self.velocity_ped, 
        #                              self.velocity_ego, 
        #                              self.orientation_ped], 
        #                             [other.velocity_ped, 
        #                              other.velocity_ego, 
        #                              other.orientation_ped]
        #                             )

        #return frechet_dist(self.sample_nodes[0::3], other.sample_nodes[0::3])

    # def to_tuple(self):
    #     import numpy as np
    #     barycenter = np.mean(self.control_nodes, axis=0)[:2]
    #     return barycenter

    def mutate(self) -> 'AVPMember':
        scm = ScenarioMutator(self)
        scm.mutate()
        self.distance_to_boundary = None
        self.simout = None
        return self

    def __repr__(self):
        eval_boundary = 'na'
        if self.distance_to_boundary:
            eval_boundary = str(self.distance_to_boundary)
            # if self.distance_to_boundary > 0:
            #     eval_boundary = '+' + eval_boundary
            # eval_boundary = '~' + eval_boundary
        eval_boundary = eval_boundary[:7].ljust(7)
        h = hashlib.sha256(str([self.velocity_ego, self.velocity_ped, self.orientation_ped]).encode('UTF-8')).hexdigest()[-5:]
        return f'{self.name_ljust} h={h} b={eval_boundary}'

class ScenarioMutator:

    def __init__(self, scenario: AVPMember):
        self.scenario = scenario

    # def mutate_gene(self, index, lbound, ubound, xy_prob=0.5) -> Tuple[int, int]:
    #     scenario = self.scenario
    #     gene = list([scenario.velocity_ego, scenario.velocity_ped, scenario.orientation_ped])
    #     # Choose the mutation extent
    #     mut_value = random.randint(lbound, ubound)
    #     # Avoid to choose 0
    #     if mut_value == 0:
    #         mut_value == 1
    #     c = 0
    #     if random.random() < xy_prob:
    #         c = 1
    #     gene[c] += mut_value
    #     # self.road.control_nodes[index] = tuple(gene)
    #     # self.road.sample_nodes = catmull_rom(self.road.control_nodes, self.road.num_spline_nodes)
    #     return c, mut_value

    # def undo_mutation(self, index, c, mut_value):
    #     gene = list(self.road.control_nodes[index])
    #     gene[c] -= mut_value
    #     self.road.control_nodes[index] = tuple(gene)
    #     self.road.sample_nodes = catmull_rom(self.road.control_nodes, self.road.num_spline_nodes)

    # def mutate(self, num_undo_attempts=10):
    def mutate(self):
        # TOOD use pymoos polynmial mutation for the mutation
        scenario_in = [[self.scenario.velocity_ego, self.scenario.velocity_ped, self.scenario.orientation_ped]]
        ar_scenario = np.asarray(scenario_in).reshape((1,-1))
        xl = np.asarray([AVPConfig.MIN_SPEED,AVPConfig.MIN_SPEED, AVPConfig.MIN_PED_ORIENTATION])
        xu = np.asarray([AVPConfig.MAX_SPEED,AVPConfig.MAX_SPEED, AVPConfig.MAX_PED_ORIENTATION])

        scenario_new = mut_pm(
              ar_scenario,
               xl=xl,
               xu=xu,
               prob=np.asarray([1]),
               eta=np.asarray([20]),
               at_least_once=False)

        # Update scenario (TODO check why we need to overwrite the scenario)
        self.velocity_ego = scenario_new[0][0]
        self.velocity_ped = scenario_new[0][1]
        self.orientation_ped = scenario_new[0][2]

        # backup_nodes = list(self.road.control_nodes)
        # attempted_genes = set()
        # n = len(self.road.control_nodes) - 2

        # def next_gene_index() -> int:
        #     if len(attempted_genes) == n:
        #         return -1
        #     i = random.randint(3, n-3)
        #     while i in attempted_genes:
        #         i = random.randint(3, n-3)
        #     attempted_genes.add(i)
        #     assert 3 <= i <= n-3
        #     return i

        # gene_index = next_gene_index()

        # while gene_index != -1:
        #     c, mut_value = self.mutate_gene(gene_index, lbound, ubound)

        #     attempt = 0

        #     is_valid = self.road.is_valid()
        #     while not is_valid and attempt < num_undo_attempts:
        #         self.undo_mutation(gene_index, c, mut_value)
        #         c, mut_value = self.mutate_gene(gene_index)
        #         attempt += 1
        #         is_valid = self.road.is_valid()

        #     if is_valid:
        #         break
        #     else:
        #         gene_index = next_gene_index()

        # if gene_index == -1:
        #     raise ValueError("No gene can be mutated")

        # assert self.road.is_valid()
        # assert self.road.control_nodes != backup_nodes

