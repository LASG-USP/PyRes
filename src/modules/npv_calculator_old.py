# Load Libraries
import os
import pandas as pd
import numpy as np
import Functions as func
from ypstruct import structure


def npv_calc(data):
    # Import RWO data
    df_rwo = func.rwo_load(f"{data.filename}", Type="Period")
    fopt = np.array(df_rwo["Oil_Prd"].to_list(), dtype="float")
    fwpt = np.array(df_rwo["Water_Prd"].to_list(), dtype="float")
    fgpt = np.array(df_rwo["Gas_Prd"].to_list(), dtype="float")
    fwit = np.array(df_rwo["Water_Inj"].to_list(), dtype="float")
    fgit = np.array(df_rwo["Gas_Inj"].to_list(), dtype="float")

    # Import Economic Data
    # filename = 'U2H'
    df = pd.read_csv(f"{data.filename}.eco")
    df.set_index(["variavel"], inplace=True)

    oleo = float(df["valor"]["preco_oleo"])
    gas = float(df["valor"]["preco_gas"])
    coleo = float(df["valor"]["custo_oleo"])
    cgas = float(df["valor"]["custo_gas"])
    cpagua = float(df["valor"]["custo_agua_prd"])
    cigas = float(df["valor"]["custo_gas_inj"])
    ciagua = float(df["valor"]["custo_agua_inj"])
    roy = float(df["valor"]["royalties"])
    pis = float(df["valor"]["pis"])
    cofins = float(df["valor"]["cofins"])
    tx_ir = float(df["valor"]["imp_renda"])
    tx_cs = float(df["valor"]["contrib_social"])
    txanual = float(df["valor"]["taxa_atrativ"])
    kbrent = float(df["valor"]["oleo_brent"])
    tdeprec = float(df["valor"]["temp_deprec"])
    campo_par = float(df["valor"]["tip_campo"])
    inicio = str(df["valor"]["inicio_simulacao"])

    conver = 6.28

    #   Receita Bruta
    Rbruta = fopt * oleo * conver * kbrent + fgpt * conver * gas

    #   Custos Operacionais                                                                  No     gas injection
    Coper = (
        fopt * conver * coleo
        + fgpt * cgas * conver
        + fwpt * cpagua * conver
        + fwit * ciagua * conver
        + fgit * cigas * conver
    )
    #   Impostos proporcionais a producao
    Ipp = Rbruta * (roy + pis + cofins)

    #   Investimento depreciável e não depreciável e depreciação
    # Filename = 'U2H'
    FileInv = f"{data.filename}"
    PathInv = data.PathInv
    aa = len(fopt)
    bb = 1

    #   Investimento depreciável e não depreciável e depreciação
    [IC2, deprec_equip, deprec_pocos, ID_equip2, ID_pocos2] = func.invest(
        FileInv, PathInv, inicio, tdeprec, aa, bb
    )

    #   Lucro tributável para incidência do imposto de renda e da contribuição social
    LT = (
        Rbruta.reshape(-1, 1)
        - Ipp.reshape(-1, 1)
        - Coper.reshape(-1, 1)
        - IC2
        - deprec_equip
    )

    IRCS = np.zeros(len(fopt))

    tx_IRCS = tx_ir + tx_cs

    for ii in range(aa):
        if LT[ii] <= 0 and ii != (aa - 1):
            LT[ii + 1] = LT[ii + 1] + LT[ii]
            IRCS[ii] = 0
        elif LT[ii] > 0:
            IRCS[ii] = LT[ii] * tx_IRCS

    #   Fluxo de caixa
    FCL = (
        Rbruta.reshape(-1, 1)
        - Coper.reshape(-1, 1)
        - Ipp.reshape(-1, 1)
        - IRCS.reshape(-1, 1)
        - IC2
        - (ID_equip2 + ID_pocos2)
    )

    #   VPL
    VPL = np.zeros(len(fopt))

    VPLacum = np.zeros(len(fopt))

    for ii in range(aa):
        VPL[ii] = FCL[ii] / ((1 + txanual) ** (ii))
        if ii == 0:
            VPLacum[ii] = VPL[ii]
        else:
            VPLacum[ii] = VPL[ii] + VPLacum[ii - 1]

    VPL_total = np.sum(VPL)

    VPL_max = np.max(VPLacum)

    out = structure()
    out.VPL = VPL
    out.VPL_total = VPL_total
    out.VPLacum = VPLacum
    out.FCL = FCL
    out.LT = LT
    out.Rbruta = Rbruta
    out.Coper = Coper
    out.Ipp = Ipp
    out.PE = 0
    out.IRCS = IRCS
    out.deprec_equip = deprec_equip
    out.VPL_max = VPL_max
    return out
