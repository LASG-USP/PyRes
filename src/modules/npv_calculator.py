import numpy as np
import pandas as pd
from config import inv_path
from datetime import datetime


class NetPresentValue:
    def __init__(self, setup, invest_path: str = inv_path) -> None:
        self.setup = setup
        self.oil_price = setup["oil_price"]
        self.oil_cost = setup["oil_cost"]
        self.oil_price_variation = setup["oil_price_variation"]
        self.oil_brent = setup["oil_brent"]
        self.gas_price = setup["gas_price"]
        self.gas_cost = setup["gas_cost"]
        self.gas_inj_cost = setup["gas_inj_cost"]
        self.water_prd_cost = setup["water_prd_cost"]
        self.water_inj_cost = setup["water_inj_cost"]
        self.water_prd_cost_variation = setup["water_prd_cost_variation"]
        self.water_inj_cost_variation = setup["water_inj_cost_variation"]
        self.royalties = setup["royalties"]
        self.pis = setup["pis"]
        self.cofins = setup["cofins"]
        self.taxes = setup["taxes"]
        self.social_contribution = setup["social_contribution"]
        self.depreciation_time = setup["depreciation_time"]
        self.start_date = datetime.strptime(setup["start_date"], "%m/%d/%Y")
        self.field_type = setup["field_type"]
        self.barrel = 6.28  # m3 to barrel
        self.invest_file_path = invest_path

    def calculate(
        self,
        oil_prd: np.array,
        gas_prd: np.array,
        water_prd: np.array,
        water_inj: np.array,
        gas_int: np.array,
    ) -> tuple:
        size = len(oil_prd)

        # Gross Revenue
        revenue = (
            oil_prd * self.oil_price * self.oil_brent
            + gas_prd * self.barrel * self.gas_price
        )

        # Operational Costs
        ope_cost = (
            oil_prd * self.barrel * self.oil_cost  # Oil production cost
            + gas_prd * self.gas_cost * self.barrel  # Gas production cost
            + water_prd * self.water_prd_cost * self.barrel  # Water production cost
            + water_inj * self.water_inj_cost * self.barrel  # Water injection cost
            + gas_int * self.gas_inj_cost * self.barrel  # Gas injection cost
        )

        # Production Taxes
        prd_taxes = revenue * (self.royalties + self.pis + self.cofins)

        # Investments
        ic, id_equip, id_wells, dpc_equip, dpc_wells = self.get_invest(size=size)

        # Taxable Profits
        tax_profits = revenue - prd_taxes - ope_cost - dpc_equip

        # Income Tax & Social Contribution
        itcs = np.zeros(size)
        tax = self.taxes + self.social_contribution

        for i, value in enumerate(tax_profits):
            if value <= 0 and i != size:
                itcs[i] = 0
                tax_profits[i] += value
            elif value > 0:
                itcs[i] = value * tax

        # Cash Flow
        cash_flow = revenue - ope_cost - ope_cost - itcs - ic - (id_equip + id_wells)

        # Net Present Value
        npv = np.zeros(size)

        for i, value in enumerate(cash_flow):
            npv[i] = value / ((1 + self.taxes) ** i)

        return (
            npv,  # Net Present Value
            sum(npv),  # Net Present Value Total
            max(npv),  # Net Present Value Max
            np.cumsum(npv),  # Net Present Value Accumulate
            cash_flow,
            tax_profits,
            revenue,
            ope_cost,
            prd_taxes,
            itcs,
            dpc_equip,
        )

    def get_invest(self, size: int) -> tuple:
        df_inv = pd.read_csv(self.invest_file_path)

        years = np.array(df_inv["year"])

        prd_delay = self.start_date.year - years[0]

        inv_ndpc = (
            np.array(df_inv["exploration"])
            + np.array(df_inv["formation_evaluation"])
            + np.array(df_inv["wells"])
            + np.array(df_inv["abandonment"])
        )

        inv_dpc_equip = np.array(df_inv["facility"])

        inv_dpc_wells = np.array(df_inv["wells"])

        ic = np.zeros(size)
        id_equip = np.zeros(size)
        id_wells = np.zeros(size)

        for i in range(size):
            if i <= prd_delay:
                ic[0] += inv_ndpc[i]
                id_equip[0] += inv_dpc_equip[i]
                id_wells[0] += inv_dpc_wells[i]
            else:
                ic[i - prd_delay] = inv_ndpc[i]
                id_equip[i - prd_delay] = inv_dpc_equip[i]
                id_wells[i - prd_delay] = inv_dpc_wells[i]

        dpc_equip = np.zeros(size)
        dpc_wells = np.zeros(size)

        # Equipments Depreciation over time
        for idx, value in enumerate(id_equip):
            if value != 0 and idx <= self.depreciation_time:
                dpc_equip[idx] = value / self.depreciation_time

        # Wells depreciation over time
        for idx, value in enumerate(id_wells):
            if value != 0 and idx <= self.depreciation_time:
                dpc_wells[idx] = value / self.depreciation_time

        ic_final = ic[:size]
        ic_final[-1:] = ic[0]

        id_equip_final = id_equip[:size]
        id_equip_final[-1:] = id_equip[0]
        id_wells_final = id_wells[:size]
        id_wells_final[-1:] = id_wells[0]

        return (ic_final, id_equip_final, id_wells_final, dpc_equip, dpc_wells)
