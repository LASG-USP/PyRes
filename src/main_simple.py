import os
import logging.config
from config import settings
from datetime import datetime
from modules import costfunc_simple, delete_files
from modules import ParticleSwarmOptimizer as PSO


def main(setup: dict = {}):
    # -------------------------------------------------------------------------------------- #
    #                                      Display Info                                      #
    # -------------------------------------------------------------------------------------- #
    logging.info("Display Settings")
    folder_label = datetime.now().strftime("%m%d%y_%H%M")
    os.makedirs(
        os.path.dirname(os.path.abspath(__file__)) + f"/../out/pso_max_{folder_label}",
        exist_ok=True,
    )

    # -------------------------------------------------------------------------------------- #
    #                                      Cost Function                                     #
    # -------------------------------------------------------------------------------------- #
    logging.info("Cost function")
    cost_func = costfunc_simple
    # -------------------------------------------------------------------------------------- #
    #                                   Optimization Stage                                   #
    # -------------------------------------------------------------------------------------- #
    logging.info("Optimization...")

    if setup["optimization_engine"].lower() == "pso":
        logging.info("Begin PS Optimizer")

        global_best = PSO(
            cost_function=cost_func,
            maximization=True,
            nvars=5,
            min_vars=[-1, -1, -1, -1, -1],
            max_vars=[99,99,99,99,99],
            npop=10,
            interation_limit=10,
            kappa=1,
            phis=[2.05, 2.05],
            wdamp=1,
            info_display=False,
            output_path=os.path.dirname(os.path.abspath(__file__))
            + f"/../out/pso_max_{folder_label}",
        ).executer()

    elif setup["optimization_engine"].lower() == "fga":
        pass

    # -------------------------------- Remove Useless Files -------------------------------- #
    delete_files(
        os.path.dirname(os.path.abspath(__file__)),
        [".dat", "irf", "out", ".rst", ".rwd", ".rwo", "sr3", "mrf"],
    )

    return True


# -------------------------------------------------------------------------------------- #
#                                      Execute Main                                      #
# -------------------------------------------------------------------------------------- #
if __name__ in "__main__":
    logging.config.fileConfig(
        os.path.dirname(os.path.abspath(__file__)) + "/logging_config.ini"
    )
    main(setup=settings)
