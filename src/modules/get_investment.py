import pandas as pd

# year,exploration,formation_evaluation,wells,facility,abandonment


def get_invest(file_path:str, start_date:str):
    df_inv = pd.read_csv(file_path, header=False)

    years = df_inv["year"].to_list()

    inv_ndeprec = (
        df_inv["exploration"]
        + df_inv["formation_evaluation"]
        + df_inv["wells"]
        + df_inv["abandonment"]
    )
    
    inv_dpc_equip = df_inv['facility'].to_list()
    
    inv_dpc_wells = df_inv['wells'].to_list()
    
    
