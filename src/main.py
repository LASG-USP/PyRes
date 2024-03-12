import os
import logging.config
from datetime import datetime
from config import settings, inv_path
from modules import ParticleSwarmOptimizer as PSO
from modules import CostFuncNPV, costfunc_simple, CMGv2, delete_files


def main(setup: dict = {}) -> bool:
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
    #                                    Simulation Setup                                    #
    # -------------------------------------------------------------------------------------- #
    cmg_instance = CMGv2(
        filename=setup["simulation_filename"],
        gem_app_path=setup["cmg_gem_path"],
        imex_app_path=setup["cmg_imex_path"],
        report_app_path=setup["cmg_report_path"],
        simulator=setup["simulator_type"],
        rwd_type=setup["rwd_file_type"],
        auto_exit=setup["auto_exit"],
    )

    # -------------------------------------------------------------------------------------- #
    #                                      Cost Function                                     #
    # -------------------------------------------------------------------------------------- #
    logging.info("Cost function")

    cost_func = CostFuncNPV(
        template_path=setup["simulation_template_path"],
        simulation_filename=setup["simulation_filename"],
        opt_keywords=setup["vars_keywords"],
        simulation_setup=cmg_instance,
        investiment_file_path=inv_path,
        setup=setup,
    ).costfunc_npv

    # -------------------------------------------------------------------------------------- #
    #                                   Optimization Stage                                   #
    # -------------------------------------------------------------------------------------- #
    logging.info("Optimization...")

    if setup["optimization_engine"].lower() == "pso":
        logging.info("Begin PS Optimizer")

        global_best = PSO(
            cost_function=cost_func,
            maximization=setup["maximization"],
            nvars=len(setup["low_range"]),
            min_vars=setup["low_range"],
            max_vars=setup["high_range"],
            npop=setup["population"],
            interation_limit=setup["interations"],
            kappa=setup["kappa"],
            phis=[setup["phi1"], setup["phi1"]],
            wdamp=setup["wdamp"],
            info_display=setup["show_info"],
            output_path=os.path.dirname(os.path.abspath(__file__))
            + f"/../out/pso_max_{folder_label}",
        ).executer()

    elif setup["optimization_engine"].lower() == "fga":
        pass

    # ------------------------------------ Save Results ------------------------------------ #
    logging.info("Save results")

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
