from avp_integration.avp_config import AVPConfig
from core import nsga2
from core.archive_impl import SmartArchive
import matplotlib.pyplot as plt
from avp_integration.avp_problem import AVPProblem

config = AVPConfig()

problem = AVPProblem(config, SmartArchive(config.ARCHIVE_THRESHOLD))

if __name__ == '__main__':
    nsga2.main(problem)
    print('done')

    plt.ioff()
    plt.show()
