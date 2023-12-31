# this classes are here in the belief that it is needed to have on a drive folder files a representation of the
# individual this representation is different from saving/loading a member. This folder structure is aimed to
# give the highest information to the human inspecting the individual
# ------------ o --------------- o ----------------
# it is advisable that the folder structure is hidden externally to this file source code
# this is in the aim to access the individuals information through save (and load)
# so, if the folder structure changes, the only source code affected should be in this file source code

import json
import os
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from core.archive import IndividualSet
from core.folders import folders
from avp_integration.avp_individual import AVPIndividual
from avp_integration.avp_member import AVPMember

class Singleton(object):
        def __new__(cls, *args, **kwds):
            it = cls.__dict__.get("__it__")
            if it is not None:
                return it
            cls.__it__ = it = object.__new__(cls)
            it.init(*args, **kwds)
            return it

        def init(self, *args, **kwds):
            pass

class AVPIndividualSetStore(Singleton):
    def init(self, folder: Path):
        self.folder = folder
        self.store = []

    def save(self, individuals: IndividualSet):
        print("Save in IndividualSet store")
        
        # store in variable
        for ind in individuals:
            # _AVPIndividualCompositeMembersStore(self.folder).save(ind)
            # _AVPIndividualSimpleStore().save(ind)
            self.store.append(ind)
        
        # store on hard drive
        self.folder.mkdir(parents=True, exist_ok=True)
        prefix = ind.name
        ind_path = self.folder.joinpath(prefix + '.json')
        ind_path.write_text(json.dumps(ind.to_dict()))


    def get_store(self):
        return self.store



class _AVPIndividualStore:
    def save(self, ind: AVPIndividual, prefix: str = None):
        raise NotImplemented()

    def load(self, prefix: str) -> AVPIndividual:
        raise NotImplemented()


# class _AVPIndividualSimpleStore:
#     store = []
#     def save(self, ind: AVPIndividual, prefix: str = None):
#         self.store.append(ind)

#     def load(self, prefix: str) -> AVPIndividual:
#         raise NotImplemented()



# class _AVPIndividualCompositeMembersStore:
#     def __init__(self, folder: Path):
#         self.folder = folder

#     def save(self, ind: AVPIndividual, prefix: str = None):
#         pass
#     #     if not prefix:
#     #         prefix = ind.name

#     #     self.folder.mkdir(parents=True, exist_ok=True)
#     #     ind_path = self.folder.joinpath(prefix + '.json')
#     #     ind_path.write_text(json.dumps(ind.to_dict()))

#     #     fig, (left, right) = plt.subplots(ncols=2)
#     #     fig.set_size_inches(15, 10)
#     #     ml, mr = ind.members_by_distance_to_boundary()

#     #     def plot(member: AVPMember, ax):
#     #         ax.set_title(f'dist to bound ~ {np.round(member.distance_to_boundary, 2)}', fontsize=12)
#     #         road_points = RoadPoints.from_nodes(member.sample_nodes)
#     #         road_points.plot_on_ax(ax)

#     #     plot(ml, left)
#     #     plot(mr, right)
#     #     fig.suptitle(f'members distance = {ind.members_distance} ; oob_ff = {ind.oob_ff}')
#     #     fig.savefig(self.folder.joinpath(prefix + '_both_roads.svg'))
#     #     plt.close(fig)

#     def load(self, prefix: str) -> AVPIndividual:
#         ind_path = self.folder.joinpath(prefix + '.json')
#         ind = AVPIndividual.from_dict(json.loads(ind_path.read_text()))
#         return ind


# if __name__ == '__main__':
#     store = _AVPIndividualCompositeMembersStore(folders.experiments.joinpath('exp1/gen0/population'))
#     ind = store.load('ind1')
#     store.save(ind, 'ind_xx')


# class _AVPIndividualSimpleStore:
#     def __init__(self, folder: Path):
#         self.folder = folder

#     def save(self, ind: AVPIndividual, prefix=None):
#         if not prefix:
#             prefix = ind.name

#         self.folder.mkdir(parents=True, exist_ok=True)

#         def save_road_img(member: AVPMember, name):
#             filepath = self.folder.joinpath(name)
#             # BeamNGRoadImagery.from_sample_nodes(member.sample_nodes).save(filepath.with_suffix('.jpg'))
#             BeamNGRoadImagery.from_sample_nodes(member.sample_nodes).save(filepath.with_suffix('.svg'))

#         ind_path = self.folder.joinpath(prefix + '.json')
#         ind_path.write_text(json.dumps(ind.to_dict()))
#         save_road_img(ind.m1, ind.name + '_m1_road')
#         save_road_img(ind.m2, ind.name + '_m2_road')
