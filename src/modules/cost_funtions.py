from .cmg import CMGv2
from .get_rwo import rwo_data_reader
from .npv_calculator import NetPresentValue
from .util import replacer, create_empty_file, add_dat_extension


def costfunc_simple(param):
    """
    Example of a function with five parameters.

    Parameters:
    - a, b, c, d, e: Input parameters.

    Returns:
    - Result based on the input parameters.
    """
    result = param[0] * param[1] + param[2] / param[3] - param[4]
    return result


class CostFuncNPV:
    def __init__(
        self,
        template_path: str,
        simulation_filename: str,
        opt_keywords: list,
        simulation_setup: dict,
        investiment_file_path: str,
        setup: dict,
    ) -> None:
        self.template_path = template_path
        self.simulation_filename = simulation_filename
        self.opt_keywords = opt_keywords
        self.simulation_setup = simulation_setup
        self.investiment_file_path = investiment_file_path
        self.setup = setup

    def costfunc_npv(self, param):
        # Create a empty simulation_file
        create_empty_file(add_dat_extension(self.simulation_filename, ".dat"))

        # replace parameters from template into empty file
        replacer(
            template_file=self.template_path,
            simulation_file=self.simulation_filename,
            variable=self.opt_keywords,
            values=param,
        )

        # Simulate Setup Execution Step
        self.simulation_setup.execute()

        # Read production Results
        df_prd = rwo_data_reader(
            add_dat_extension(self.simulation_filename, ".rwo"),
            Type=self.setup["rwd_file_type"],
        )

        # Net Present Value calculation
        npv = NetPresentValue(
            setup=self.setup, invest_path=self.investiment_file_path
        ).calculate(
            oil_prd=df_prd["Oil_Prd"],
            gas_prd=df_prd["Water_Prd"],
            water_prd=df_prd["Gas_Prd"],
            water_inj=df_prd["Water_Inj"],
            gas_int=df_prd["Gas_Inj"],
        )

        return npv[2]  # Max NPV
        
