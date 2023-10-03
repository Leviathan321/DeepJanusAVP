
from dummy.evaluation.critical import CriticalAdasBoxCollision, CriticalAdasExplicitRearCollision
from dummy.evaluation.fitness import FitnessMinDistanceVelocity
from dummy.simulation.dummy_simulation import DummySimulator
from visualization.scenario_plotter import plot_scenario_gif
import os
from datetime import datetime
from pathlib import Path

save_folder = str(
    os.getcwd()) + os.sep + "result" + os.sep # + \
    # datetime.now().strftime("%d-%m-%Y_%H-%M-%S")  + os.sep 
  
#print(f"save_folder created: {save_folder}")
Path(save_folder).mkdir(parents=True, exist_ok=True)

sim = DummySimulator()

variable_names = [
                                                    "velocity_ego",
                                                    "velocity_ped",
                                                    "orientation_ped"]

scenario = [           1,
                       2,
                     190
                       ]                           

simout = sim.simulate_single(vars=scenario,
                        variable_names=variable_names,
                        time_step=1,
                        sim_time=40,
                        filepath="",
                        detection_dist=4
                        )

plot_scenario_gif(simout = simout,
                  parameter_values = scenario,
                  savePath=save_folder,
                  fileName="test")

ff = FitnessMinDistanceVelocity()
fvalues = ff.eval(simout=simout)

cf = CriticalAdasExplicitRearCollision()
is_critical = cf.eval(vector_fitness=fvalues,simout=simout)

print(f"Fitness values: {fvalues}")
print(f"Is critical: {is_critical}")