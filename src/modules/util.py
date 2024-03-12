import os
import logging
from datetime import datetime


def init_info(optzer: str = "") -> str:
    start_info = f"""
            **********************************************************
                                                                                                                      
                              PYTHON OPTIMIZER {optzer}                     
                                                                     
                                  
                                      LASG                           
                                                                     
                    LABORATÓRIO DE SIMULAÇÃO E GERENCIAMENTO         
                            DE RESERVATÓRIOS DE PETRÓLEO             
                                                                     
                                                                                                       
                         FINANCIAMENTO: POLI-USP E FAPESP             
                                                                     
                                                                     
                               {datetime.now().strftime('%d/%m/%Y %H:%M')}                       
            **********************************************************

            
                                 ==>  START  <==
"""
    return print(start_info)


def pso_info(
    obj: str = "", optm_type: str = "", maxit: int = None, npop: int = None
) -> str:
    if obj == "VPL" and optm_type == "max":
        fo = "Net Present Value - MAXIMIZATION"

    elif obj == "VPL" and optm_type == "min":
        fo = "Net Present Value - MINIMIZATION"

    txt = f"""\n
            **********************************************************
                       
                            PSO Optimizer Configuration        

              O.F.: {fo}     

              Iteration: {maxit} 

              Population: {npop}                          
            
            **********************************************************

                                 ==>  START  <==
    """
    return print(txt)


def add_dat_extension(file_name: str, ext: str) -> str:
    return file_name + ext if ext not in file_name else file_name


def replacer(
    template_file: str, simulation_file: str, variable: list, values: list
) -> bool:
    template_file = add_dat_extension(template_file, ".dat")
    simulation_file = add_dat_extension(simulation_file, ".dat")

    with open(f"{template_file}", "r") as infile, open(
        f"{simulation_file}", "w"
    ) as outfile:
        for line in infile:
            for check, rep in zip(variable, values):
                line = line.replace(str(check), str(rep))
            outfile.write(line)

    return True


def create_empty_file(file_name: str) -> None:
    try:
        with open(file_name, "x"):
            pass
    except FileExistsError:
        pass
        # print(f"The file '{file_name}' already exists.")


def nmse(x: float, y: float) -> float:
    z = 0
    if len(x) == len(y):
        for k in range(len(x)):
            z = z + (((x[k] - y[k]) ** 2) / x[k])
            z = z / (len(x))
    return z


def rmv_files(dir_name: str, file_extension: str = ".bat") -> bool:
    # dir_name = os.path.dirname(os.path.abspath(__file__))

    file_list = os.listdir(dir_name)

    for item in file_list:
        if item.endswith(f"{file_extension}"):
            os.remove(os.path.join(dir_name, item))

    return True


def delete_files(directory_path:str, extensions:list) -> None:
    try:
        # List all files in the directory
        files = os.listdir(directory_path)

        for file in files:
            # Check if the file has an allowed extension
            if any(file.lower().endswith(ext) for ext in extensions):
                file_path = os.path.join(directory_path, file)

                # Delete the file
                os.remove(file_path)
                logging.info(f"Deleted: {file_path}")

        logging.info("Deletion complete.")
    except FileNotFoundError:
        logging.error(f"Directory not found: {directory_path}")
    except Exception as e:
        logging.error(f"Error deleting files: {e}")
