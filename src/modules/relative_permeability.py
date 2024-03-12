from tqdm import tqdm
import numpy as np
from typing import Any
import pandas as pd
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt


class RelativePermeability:
    def __init__(
        self, sw:list, kro:list, krw:list, flag_plot: bool = False
    ) -> None:
        self.sw = np.array(sw)
        self.so = 1 - np.array(sw)
        self.kro = np.array(kro)
        self.krw = np.array(krw)
        self.flg_plot = flag_plot
        self.no_nw_array = np.arange(1, 15, 0.02)

    def plot(self, kro_c:list, krw_c:list) -> plt.plot:
        sw = self.sw
        plt.figure(figsize=[12, 8])
        plt.plot(sw, kro_c, "black", sw, self.kro, "green")
        plt.plot(sw, krw_c, "black", sw, self.krw, "blue")

    def brooks_corey_equations(
        self, krw_iro, sw_crit, so_irw, nw, kro_cw, so_rw, sw_con, no
    ) -> list:
        # Water
        krw_corey = krw_iro * (
            ((self.sw - sw_crit) / (1 - sw_crit - (1 - so_irw))) ** nw
        )
        # Oil
        kro_corey = kro_cw * (
            ((self.so - (1 - so_rw)) / (1 - sw_con - (1 - so_rw))) ** no
        )
        return krw_corey, kro_corey

    def corey_parameters(self) -> list:
        r2_o = []
        r2_w = []

        # Oil Equation Parameters
        kro_cw = self.kro.max()
        sw_con = self.sw.min()
        so_rw = self.sw.max()

        # Water Equation Parameters
        krw_iro = self.krw.max()
        so_irw = self.sw.max()
        sw_crit = np.array(self.sw[self.sw > 0]).min()

        for n in tqdm(self.no_nw_array, desc="Processing", unit="iteration"):
            # Corey Equations
            nw = n
            no = n

            krw_c, kro_c = self.brooks_corey_equations(
                krw_iro, sw_crit, so_irw, nw, kro_cw, so_rw, sw_con, no
            )

            r2_o.append(r2_score(kro_c, self.kro))
            r2_w.append(r2_score(krw_c, self.krw))

        final_no = self.no_nw_array[np.array(r2_o).argmax()]
        final_nw = self.no_nw_array[np.array(r2_w).argmax()]

        krw_c, kro_c = self.brooks_corey_equations(
            krw_iro, sw_crit, so_irw, final_nw, kro_cw, so_rw, sw_con, final_no
        )
        if self.flg_plot:
            self.plot(kro_c, krw_c)

        return [final_no, final_nw, so_rw, so_irw, sw_con, sw_crit, kro_cw, krw_iro]

    def corey2curve(
        self, sw, no, nw, so_rw, so_irw, sw_con, sw_crit, kro_cw, krw_iro, save_file:bool=False, file_name:str=''
    ) -> list:
        self.sw = np.array(sw)
        self.so = 1 - self.sw

        krw_c, kro_c = self.brooks_corey_equations(
            krw_iro, sw_crit, so_irw, nw, kro_cw, so_rw, sw_con, no
        )

        if save_file:
            kr_curve = pd.DataFrame()
            kr_curve["sw"] = sw
            kr_curve["kro"] = kro_c
            kr_curve["krw"] = krw_c

            np.savetxt(f"{file_name}.inc", kr_curve.values, fmt="%.5f", delimiter="\t")

        return krw_c, kro_c
