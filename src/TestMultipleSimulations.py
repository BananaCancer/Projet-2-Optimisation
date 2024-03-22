import pandas as pd
from TestBlackBox import TestBlackBox
from typing import Iterator, List, Tuple
from plotFunctions import plot_differences, plot_time
import programmationDynamique as progDyn
import numpy as np
from time import time
class TestMultipleSimulations:
    def read_excel_yield(self, 
                         filename: str, 
                         starting_row: int, 
                         end_row: int) -> Iterator[pd.DataFrame]:
        yield pd.read_excel(filename, skiprows=starting_row , nrows=end_row+1)

    def __init__(self, file_name: str, first_row: int, 
                 row_count: int, simulationTypes: List[str]) -> None:
        with open(file_name, 'rb') as f:
            rows = self.read_excel_yield(f, first_row, row_count)
            self.df_file = next(rows)
        self.results = {}
        self.simulationTypes = simulationTypes
        for key in simulationTypes:
            self.results[key] = {
                "sumDifferences": 0,
                "nbImprovements": 0,
                "time_data": [],
                "diff_ttl_puissance_data": [],
                "diff_puissance_puissance_per_turbine_data": [[], [], [], [], []]
            }
        self.row_count = row_count
        self.color = []

    def get_active_turbines(self, line_index: int) -> List[bool]:
        active_turbines = [True if self.df_file.loc[line_index, f"P{i} (MW)"] else False for i in range(1, 6)]
        return active_turbines

    def getDataFromExcel(self, line_index: int) \
        -> Tuple[float, float, list[bool]]:
        debit_total = self.df_file.loc[line_index, "Qtot (m3/s)"]
        niveau_amont = self.df_file.loc[line_index, "Niv Amont (m)"]
        active_turbines : List[bool] = self.get_active_turbines(line_index)
        return debit_total, niveau_amont, active_turbines

    def runProgDyn(self, debit_total, niveau_amont, line_index):
        debit_total_computed = round(debit_total, 2)
        progDyn.DEBIT_TOTAL = debit_total_computed
        progDyn.niveau_amont = niveau_amont
        ref = np.arange(progDyn.DEBIT_TOTAL,progDyn.MIN_DEBIT - progDyn.PAS_DEBIT, - progDyn.PAS_DEBIT)
        progDyn.REF = [round(number,2) for number in ref if number >= 0]
        df_result : pd.DataFrame = progDyn.initialize_result_df(debit_total, 
                                            debit_total_computed, 
                                            self.df_file.iloc[line_index])
        excel_line_actives_turbines : List[bool] = progDyn.get_active_turbines(self.df_file, line_index)
        actives_turbines = [index for index, value in enumerate(excel_line_actives_turbines, start=1) if value]
        start = time()
        result = progDyn.dynamicProgrammingAlgorithm(excel_line_actives_turbines)
        ttl_time = time() - start
        self.results["ProgDyn"]["time_data"].append(ttl_time)
        progDyn.extractResults(df_result, actives_turbines, result)
        return df_result

    def runSimulations(self) -> None:
        for line_index in range(len(self.df_file)):
            debit_total, niveau_amont, active_turbines = self.getDataFromExcel(line_index)

            bb = TestBlackBox(debit_total, niveau_amont, active_turbines, 
                    self.df_file.iloc[line_index])
            self.results["BB"]["time_data"].append(bb.run())
            df_result = bb.df_result
            df_result = df_result.rename(index={'Computed': 'Computed BB'})
            if "ProgDyn" in self.simulationTypes:
                df_resultDyn = self.runProgDyn(debit_total, niveau_amont, line_index)
                row = df_resultDyn.loc[['Computed']].rename(index={'Computed': 'Computed ProgDyn'})
                df_result = pd.concat([df_result, row])
                
            print("----".center(200))
            print(df_result)
            self.color.append(sum(active_turbines))
            for method in self.simulationTypes:
                power_diff = df_result.loc[f"Computed {method}", "Puissance totale"] - df_result.loc["Original", "Puissance totale"]
                self.results[method]["diff_ttl_puissance_data"].append(power_diff)
                for i in range(5):
                    turbineDiff = df_result.loc[f"Computed {method}", f"Débit T{i+1}"] - df_result.loc["Original", f"Débit T{i+1}"]
                    self.results[method]["diff_puissance_puissance_per_turbine_data"][i].append(turbineDiff)
                currentDifference = df_result.loc[f"Computed {method}", "Puissance totale"] - df_result.loc["Original", "Puissance totale"]
                if currentDifference > 0:
                    self.results[method]["nbImprovements"] +=1
                self.results[method]["sumDifferences"] += currentDifference
    
    def getResults(self, doPlots: bool = True) -> None:
        for method in self.simulationTypes:
            print(f"The sum of the differences for the method {method} is {self.results[method]['sumDifferences']}.")
            print(f"The differences average for the method {method} is {self.results[method]['sumDifferences'] / self.row_count}.")
        print(f"The power was improved {self.results[method]['nbImprovements']} times for the method {method}.")
        print(f"Average execution time for method {method}: {sum(self.results[method]['time_data'])/self.row_count}")
        if doPlots:
            if "ProgDyn" in self.simulationTypes:
                plot_differences(self.results["BB"]["diff_ttl_puissance_data"], prog_dyn_data = self.results["ProgDyn"]["diff_ttl_puissance_data"], label="Total Power")
                plot_time(self.results["BB"]["time_data"], self.color, prog_dyn_data = self.results["ProgDyn"]["time_data"])
            else:
                plot_differences(self.results["BB"]["diff_ttl_puissance_data"],label="Total Power")
                plot_time(self.results["BB"]["time_data"], self.color)
            for i in range(5):
                if "ProgDyn" in self.simulationTypes:
                    plot_differences(self.results["BB"]["diff_puissance_puissance_per_turbine_data"][i],
                                 prog_dyn_data = self.results["ProgDyn"]["diff_puissance_puissance_per_turbine_data"][i], 
                                 label=f"Turbine {i+1} Power")
                else:
                    plot_differences(self.results["BB"]["diff_puissance_puissance_per_turbine_data"][i],
                                 label=f"Turbine {i+1} Power")
