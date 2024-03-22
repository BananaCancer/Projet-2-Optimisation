import pandas as pd
from TestBlackBox import TestBlackBox
from typing import Iterator, List, Tuple
import pandas as pd
from plotFunctions import plot_differences, plot_time

class TestMultipleBlackBox:
    def read_excel_yield(self, 
                         filename: str, 
                         starting_row: int, 
                         end_row: int) -> Iterator[pd.DataFrame]:
        yield pd.read_excel(filename, skiprows=starting_row , nrows=end_row+1)

    def __init__(self, file_name: str, 
                 first_row: int, row_count: int) -> None:
        with open(file_name, 'rb') as f:
            rows = self.read_excel_yield(f, first_row, row_count)
            self.df_file = next(rows)
        self.sumDifferences = 0
        self.nbImprovements = 0
        self.time_data = []
        self.diff_ttl_puissance_data = []
        self.diff_puissance_puissance_per_turbine_data = [[], [], [], [], []]
        self.color = []
        self.row_count = row_count

    def get_active_turbines(self, line_index: int) -> List[bool]:
        active_turbines = [True if self.df_file.loc[line_index, f"P{i} (MW)"] else False for i in range(1, 6)]
        return active_turbines

    def getDataFromExcel(self, line_index: int) \
        -> Tuple[float, float, list[bool]]:
        debit_total = self.df_file.loc[line_index, "Qtot (m3/s)"]
        niveau_amont = self.df_file.loc[line_index, "Niv Amont (m)"]
        active_turbines : List[bool] = self.get_active_turbines(line_index)
        return debit_total, niveau_amont, active_turbines

    def runSimulations(self) -> None:
        for line_index in range(len(self.df_file)):
            debit_total, niveau_amont, active_turbines = self.getDataFromExcel(line_index)
            bb = TestBlackBox(debit_total, niveau_amont, active_turbines, 
                        self.df_file.iloc[line_index])
            ttl_time = bb.run()
            print("----".center(200))
            bb.printResults()
            df_result = bb.df_result
            self.color.append(sum(active_turbines))
            self.time_data.append(ttl_time)
            self.diff_ttl_puissance_data.append(df_result.loc["Computed", "Puissance totale"] - df_result.loc["Original", "Puissance totale"])
            for i in range(5):
                self.diff_puissance_puissance_per_turbine_data[i].append(df_result.loc["Computed", f"Débit T{i+1}"] - df_result.loc["Original", f"Débit T{i+1}"])
            self.currentDifference = df_result.loc["Computed", "Puissance totale"] - df_result.loc["Original", "Puissance totale"]
            if self.currentDifference > 0:
                self.nbImprovements +=1
            self.sumDifferences += self.currentDifference
    
    def getResults(self, doPlots: bool = True) -> None:
        print(f"The sum of the differences is {self.sumDifferences}.")
        print(f"The differences average is {self.sumDifferences / self.row_count}.")
        print(f"The power was improved {self.nbImprovements} times")
        print(f"Average execution time: {sum(self.time_data)/self.row_count}")
        if doPlots:
            plot_differences(self.diff_ttl_puissance_data, label="Total Power")
            for i in range(5):
                plot_differences(self.diff_puissance_puissance_per_turbine_data[i], label=f"Turbine {i} Power")
            plot_time(self.time_data, self.color)

        

