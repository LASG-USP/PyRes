import os
import subprocess
import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from .util import create_empty_file


class CMG:
    def __init__(
        self,
        file: str,
        simulator: str = "IMEX",
        version: int = 2015,
        auto_exit: bool = True,
        rwd_type: str = "period",
    ) -> None:
        self.simulator = simulator
        self.version = version
        self.rwd_type = rwd_type
        self.auto_exit = "exit" if auto_exit else ""
        self.sim_trigger = "mx" if simulator == "IMEX" else "gm"
        self.file = file if file.find(".dat") == -1 else file.replace(".dat", "")

    @property
    def str_bat(self) -> str:
        return rf"""
            if not DEFINED IS_MINIMIZED set IS_MINIMIZED=1 && start "{self.file}" /min "%~dpnx0" %* && exit
            ECHO OFF
            color 0F
            START /MIN /WAIT /B cmd.exe /c "C:\Program Files (x86)\CMG\{self.simulator}\{self.verson}.10\Win_x64\EXE\{self.sim_trigger}{self.verson}10.exe" -f {self.file}.dat -dd
            START /MIN /WAIT /B cmd.exe /c "C:\Program self.files (x86)\CMG\BR\{self.verson}.10\Win_x64\EXE\report.exe" -f {self.file}.rwd -o {self.file}.rwo
            SET /A DD=\n
            ECHO {self.file} >> %0\..\Report.txt

            del %0\..\{self.file}.irf
            del %0\..\{self.file}.mrf
            del %0\..\{self.file}.rwd
            del %0\..\{self.file}.out
            del %0\..\{self.file}.rst
            {self.auto_exit}
            """

    @property
    def str_bat(self) -> str:
        return f"""
            if not DEFINED IS_MINIMIZED set IS_MINIMIZED=1 && start "{self.file}" /min "%~dpnx0" %* && exit
            ECHO OFF
            color 0F
            START /MIN /WAIT /B cmd.exe /c "C:\\Program Files (x86)\\CMG\\{self.simulator}\\{self.version}.10\\Win_x64\\EXE\\{self.sim_trigger}{self.version}10.exe" -f {self.file}.dat -dd
            START /MIN /WAIT /B cmd.exe /c "C:\\Program Files (x86)\\CMG\\BR\\{self.version}.10\\Win_x64\\EXE\\report.exe" -f {self.file}.rwd -o {self.file}.rwo
            SET /A DD=\\n
            ECHO {self.file} >> %0\\..\\Report.txt

            del %0\\..\\{self.file}.irf
            del %0\\..\\{self.file}.mrf
            del %0\\..\\{self.file}.rwd
            del %0\\..\\{self.file}.out
            del %0\\..\\{self.file}.rst
            {self.auto_exit}
        """

    @property
    def rwd_period(self) -> str:
        return rf"""
                *FILES      '{self.file}.irf'
                *LINES-PER-PAGE 200
                *TABLE-WIDTH 300
                *SPREADSHEET
                *TABLE-FOR
                    *COLUMN-FOR  *PARAMETERS 'Period Oil Production - Yearly SC' *GROUPS 'Default-Field-PRO' 
                    *COLUMN-FOR  *PARAMETERS 'Period Water Production - Yearly SC' *GROUPS 'Default-Field-PRO'
                    *COLUMN-FOR  *PARAMETERS 'Period Gas Production - Yearly SC' *GROUPS 'Default-Field-PRO'
                    *COLUMN-FOR  *PARAMETERS 'Period Water Production - Yearly SC' *GROUPS 'Default-Field-INJ'
                    *COLUMN-FOR  *PARAMETERS 'Period Gas Production - Yearly SC' *GROUPS 'Default-Field-INJ' 
                *TABLE-END
            """

    @property
    def rwd_rate(self) -> str:
        return rf"""
                *FILES      '{self.file}.irf'
                *LINES-PER-PAGE 200
                *TABLE-WIDTH 300
                *SPREADSHEET
                *TABLE-FOR
                    *COLUMN-FOR  *PARAMETERS 'Oil Rate SC' *WELLS *ALL-PRODUCERS     
                    *COLUMN-FOR  *PARAMETERS 'Water Rate SC' *WELLS *ALL-PRODUCERS  
                    *COLUMN-FOR  *PARAMETERS 'Cumulative Oil SC' *WELLS *ALL-PRODUCERS     
                    *COLUMN-FOR  *PARAMETERS 'Cumulative Water SC' *WELLS *ALL-PRODUCERS 
                *TABLE-END
            """

    def parallel_laucher(self) -> None:
        if self.rwd_type == "period":
            rwd = open(f"{self.file}.rwd", "w")
            rwd.write(self.rwd_period)
            rwd.close()
        else:
            rwd = open(f"{self.file}.rwd", "w")
            rwd.write(self.rwd_rate)
            rwd.close()

        bat_file = open(f"{self.file}.bat", "w")
        bat_file.write(self.rwd_rate)
        bat_file.close()
        os.system(f"start {self.file}.bat")

    def executer(self) -> None:
        cmd_command = f"C:\\Program Files (x86)\\CMG\\GEM\\{self.version}.10\\Win_x64\\EXE\\{self.sim_trigger}{self.version}10.exe"

        return os.system(
            f'cmd /k "{cmd_command} -f "{self.file}" -wait -doms -parasol {os.cpu_count()}"'
        )

    def parallel_executer(
        self, files: list = [], n_parallel_executions: int = None
    ) -> None:
        cpu = 0
        files = list[self.file] if files == [] else files
        self.file = files

        max_cpu = (
            os.cpu_count() if n_parallel_executions == None else n_parallel_executions
        )

        try:
            with open("Report.txt", "r+"):
                pass
        except FileNotFoundError:
            with open("Report.txt", "w+"):
                pass

        for file in range(files):
            self.parallel_laucher()

            cpu += 1

            if cpu == max_cpu:
                f = open("Report.txt", "r").readlines()
                while len(f) == 0:
                    f = open("Report.txt", "r").readlines()

                cpu -= 1
                f = open("Report.txt", "r+")
                f.truncate(0)
                f.close()

        f = open("Report.txt", "r+")
        f.truncate(0)
        f.close()

    def rwo_creator(self, filerwd: str = "", remove_files: int = 0) -> str:
        # import os
        Irf_file = self.file.replace(".dat", ".irf")
        Rwd_file = self.file.replace(".dat", ".rwd")
        Rwo_file = self.file.replace(".dat", ".rwo")

        fr = open(f"{filerwd}.rwd", "rt")
        fw = open(Rwd_file, "wt")
        for line in fr:
            fw.write(line.replace("$$", Irf_file))
        fr.close()
        fw.close()
        rwo = f'"C:\\Program Files (x86)\\CMG\\BR\\{self.version}.10\\Win_x64\\EXE\\report.exe"'
        os.system(f'cmd /k "{rwo} -f "{Rwd_file}" -o "{Rwo_file}"')

        if remove_files == 1:
            os.remove(Irf_file)
            mrf_file = self.file.replace(".dat", ".mrf")
            os.remove(mrf_file)
            out_file = self.file.replace(".dat", ".out")
            os.remove(out_file)
            rst_file = self.file.replace(".dat", ".rst")
            os.remove(rst_file)
            os.remove(Rwd_file)

    def rwo_load(self, Type: str = "Rate") -> pd.DataFrame:
        if Type == "Rate":
            with open(f"{self.file}.rwo") as f:
                lines = f.readlines()
            df = pd.DataFrame(lines[6:])
            df.columns = ["Col"]
            df = df["Col"].str.split("\t", n=5, expand=True)
            df = df.iloc[:, 0:5]
            df.rename(
                columns={
                    0: "Year",
                    1: "Oil_Rate",
                    2: "Water_Rate",
                    3: "Cumul_Oil",
                    4: "Cumul_Water",
                },
                inplace=True,
            )

            i = 0
            while i < 5:
                df.iloc[:, i] = pd.to_numeric(df.iloc[:, i], downcast="float")
                i += 1

            year = np.arange(0, 11315, 365)
            df = df.loc[df["Year"].isin(year)]

        elif Type == "Period":
            with open(f"{self.file}.rwo") as f:
                lines = f.readlines()
            df = pd.DataFrame(lines[6:])
            df.columns = ["Col"]
            df = df["Col"].str.split("\t", n=6, expand=True)
            df = df.iloc[:, 0:6]
            df.rename(
                columns={
                    0: "Year",
                    1: "Oil_Prd",
                    2: "Water_Prd",
                    3: "Gas_Prd",
                    4: "Water_Inj",
                    5: "Gas_Inj",
                },
                inplace=True,
            )

            i = 0
            while i < 5:
                df.iloc[:, i] = pd.to_numeric(df.iloc[:, i], downcast="float")
                i += 1

        return df


class CMGv2:
    def __init__(
        self,
        filename: str,
        gem_app_path: str,
        imex_app_path: str,
        report_app_path: str,
        simulator: str = "IMEX",
        rwd_type: str = "period",
        auto_exit: bool = True
    ) -> None:
        self.rwd_type = rwd_type
        self.simulator = simulator
        self.gem_app_path = gem_app_path
        self.imex_app_path = imex_app_path
        self.report_app_path = rf"{report_app_path}"
        self.auto_exit = auto_exit
        self.file = (
            filename if filename.find(".dat") == -1 else filename.replace(".dat", "")
        )

    @property
    def rwd_period(self) -> str:
        return rf"""
                *FILES      '{self.file}.irf'
                *LINES-PER-PAGE 200
                *TABLE-WIDTH 300
                *SPREADSHEET
                *TABLE-FOR
                    *COLUMN-FOR  *PARAMETERS 'Period Oil Production - Yearly SC' *GROUPS 'Default-Field-PRO' 
                    *COLUMN-FOR  *PARAMETERS 'Period Water Production - Yearly SC' *GROUPS 'Default-Field-PRO'
                    *COLUMN-FOR  *PARAMETERS 'Period Gas Production - Yearly SC' *GROUPS 'Default-Field-PRO'
                    *COLUMN-FOR  *PARAMETERS 'Period Water Production - Yearly SC' *GROUPS 'Default-Field-INJ'
                    *COLUMN-FOR  *PARAMETERS 'Period Gas Production - Yearly SC' *GROUPS 'Default-Field-INJ' 
                *TABLE-END
            """

    @property
    def rwd_rate(self) -> str:
        return rf"""
                *FILES      '{self.file}.irf'
                *LINES-PER-PAGE 200
                *TABLE-WIDTH 300
                *SPREADSHEET
                *TABLE-FOR
                    *COLUMN-FOR  *PARAMETERS 'Oil Rate SC' *WELLS *ALL-PRODUCERS     
                    *COLUMN-FOR  *PARAMETERS 'Water Rate SC' *WELLS *ALL-PRODUCERS  
                    *COLUMN-FOR  *PARAMETERS 'Cumulative Oil SC' *WELLS *ALL-PRODUCERS     
                    *COLUMN-FOR  *PARAMETERS 'Cumulative Water SC' *WELLS *ALL-PRODUCERS 
                *TABLE-END
            """

    def simulation_command(self, app_path, report: bool = False) -> str:
        ext = 'c' if self.auto_exit else 'k'
        if report:
            return rf'start cmd.exe /{ext} ""{app_path}" -f "{self.file}.rwd" -o "{self.file}.rwo""'
        else:
            return rf'start cmd.exe /{ext} ""{app_path}" -f "{self.file}.dat" -wait -doms -parasol {os.cpu_count()}"'

    def run_multiple_programs(self, commands):
        with ThreadPoolExecutor(
            max_workers=5
        ) as executor:  # Set max_workers to the desired number
            futures = [
                executor.submit(self.run_program, command) for command in commands
            ]

            for future in as_completed(futures):
                try:
                    # Get the result of the completed future (or raise an exception if an error occurred)
                    future.result()

                    # Proceed with the next steps in your application after the completion of each task

                except Exception as e:
                    # Handle exceptions from the run_program function
                    print("Exception in run_program:", str(e))

    def run_program(self, command):
        try:
            # Run the external program and capture its output
            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
            )
            output, error = process.communicate()

            # Check the return code to determine if the execution was successful
            if process.returncode == 0:
                # Process the output as needed
                pass
                # Proceed with the next steps in your application

            else:
                # Handle errors if the return code is non-zero
                print("Error:", error.decode())
                # Handle the error or raise an exception based on your requirements

        except Exception as e:
            # Handle any exceptions that may occur during the execution
            print("Exception:", str(e))

    def execute(self):
        if self.simulator == "IMEX":
            self.run_program(self.simulation_command(self.imex_app_path))

        elif self.simulator == "GEM":
            self.run_program(self.simulation_command(self.gem_app_path))

        create_empty_file(self.file + ".rwo")

        with open(self.file + ".rwd", "w") as write_file:
            if self.rwd_type == "period":
                write_file.write(self.rwd_period)
            if self.rwd_type == "rate":
                write_file.write(self.rwd_rate)

        self.run_program(self.simulation_command(self.report_app_path, report=True))
