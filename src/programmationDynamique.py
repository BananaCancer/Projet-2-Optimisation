import copy
from typing import Dict, Iterator, List, Union
from time import time
import numpy as np
import pandas as pd
from plotFunctions import plot_differences, plot_time
MIN_DEBIT = 0
MAX_DEBIT = 160
PAS_DEBIT = 5

# debit_total = 0
niveau_amont = 0

# Paramètres

# L’élévation avale en fonction du débit total
# f(x) = p1*x^2 + p2*x + p3	

COEFFICIENTS_ELEV_AVAL = [-1.453*10**(-6), 0.007022, 99.9812] # [p1, p2, p3] 

# puissance turbine 1 = 1.1018 − 0.0487x − 0.0319y + 0.0022x2 + 0.0033xy
# puissance turbine 2 = 0.6987 − 0.1750x − 0.0201y + 0.0036x2 + 0.0042xy − 1.6988 × 10−5x3 + 3.5401 × 10−5x2y
# puissance turbine 3 = 0.7799 + 0.1995x − 0.0226y − 0.0017xy + 0.0001x2y 
# puissance turbine 4 = 0.2212 − 0.0487x − 0.0319y + 0.0022x2 + 0.0033xy

# La puissance produite en fonction de la hauteur de chute nette et du débit turbiné
# f(x,y) = p00 + p10*x + p01*y + p20*x^2 + p11*x*y + p02*y^2 + p30*x^3 + p21*x^2*y + p12*x*y^2 + p03*y^3 + p40*x^4 + p31*x^3*y + p22*x^2*y^2 + p13*x*y^3 + p04*y^4

# x : debit
# y : Chute nette

# turbine 1            p00   |    x    |    y    |   x^2   |
#                      x*y   |   y^2   |   x^3   |   x^2*y |         
puissance_turbine_1 = [1.1018, -0.04866, -0.03187, 0.002182, 
                       0.003308, 0, -1.2771e-05, 3.683e-05]

# turbine 2             p00   |    x    |    y    |   x^2   |
#                       x*y   |   y^2   |   x^3   |   x^2*y |
puissance_turbine_2 = [0.6987, -0.175, -0.02011, 0.003632, 
                       0.004154, 0, -1.6988e-05, 3.5401e-05]

# turbine 3             p00   |    x    |    y    |   x^2   |
#                       x*y   |   y^2   |   x^3   |   x^2*y |
puissance_turbine_3 = [0.7799,  0.1995 , -0.02261, -3.519e-05 , 
                       -0.001695, 0, -9.338e-06, 7.235e-05]

# turbine 4             p00   |    x    |    y    |   x^2   |
#                       x*y   |   y^2   |   x^3   |   x^2*y |
puissance_turbine_4 = [20.2212 , -0.4586, -0.5777, 0.004886, 
                       0.01151, 0, -1.882e-05,   1.379e-05]

# turbine 5             p00   |    x    |    y    |   x^2   |
#                       x*y   |   y^2   |   x^3   |   x^2*y |
puissance_turbine_5 = [1.9786, 0.004009, -0.05699, 0.001064, 
                       0.005456, 0,  -8.162e-06,   2.849e-05]
		

ARRAY_COEFFICIENTS_TURBINES = [puissance_turbine_1, puissance_turbine_2, 
                               puissance_turbine_3, puissance_turbine_4, 
                               puissance_turbine_5]


def getChuteNette(debit_turbine: Union[int,float]) -> Union[int,float]:
  # Vérifier si le débit est dans la plage admissible
  if debit_turbine < MIN_DEBIT or debit_turbine > MAX_DEBIT:
    raise ValueError(f"Le débit doit être compris entre {MIN_DEBIT} et {MAX_DEBIT} m³/s. now is more {debit_turbine}")
  # Déterminer l'élévation avale en fonction du débit total
  elevation_avale = COEFFICIENTS_ELEV_AVAL[0] * DEBIT_TOTAL**2 + \
                    COEFFICIENTS_ELEV_AVAL[1] * DEBIT_TOTAL + \
                    COEFFICIENTS_ELEV_AVAL[2]

  # Calculer la chute nette
  chute_nette = niveau_amont - elevation_avale \
  - (0.5 * (10**-5) * (debit_turbine**2))

  return chute_nette


def getStates(turbines: list) -> Dict[int,List[int]]:
  """
  return A dictionnary containing a list of every state possible for each
  available turbine
  """
  nb_turbines = len(turbines)
  result: Dict[int, List[int]] = {}
  result[turbines[0]] = [DEBIT_TOTAL]

  for i, turbine in enumerate(turbines[1:]):
    # Débit max restant: Max débit * nb turbines restantes 
    # ou QTot si Max débit * nb turbines restantes > Qtot
    if MAX_DEBIT * (nb_turbines - i - 1) < DEBIT_TOTAL:
      debit_restant_max = MAX_DEBIT * (nb_turbines - i - 1)
    else:
      debit_restant_max = DEBIT_TOTAL
    debit_restant_max = find_nearest_number(reference_list=REF,number=debit_restant_max, is_max=True)
    debit_restant_max = round(debit_restant_max,2)

    # Débit min restant: Débit total - DébitMax * Nb turbines avant (ou 0)
    if (DEBIT_TOTAL - MAX_DEBIT * (i + 1)) > 0:
      debit_restant_min = DEBIT_TOTAL - MAX_DEBIT * (i + 1)
    else:
      debit_restant_min = 0
    debit_restant_min = find_nearest_number(reference_list=REF,number=debit_restant_min, is_max=False)
    debit_restant_min = round(debit_restant_min,2)

    debit_restant = list(np.arange(debit_restant_min,
                                   debit_restant_max,
                                   PAS_DEBIT))
    debit_restant = round_list(debit_restant)
    if not (debit_restant[-1] == debit_restant_max):
      debit_restant.append(debit_restant_max)

    
    
    result[turbine] = debit_restant
  return result
  

def getPossibleValues():
  """
  return All the values that a step can take
  """
  max_for_turbine = DEBIT_TOTAL if MAX_DEBIT > DEBIT_TOTAL else MAX_DEBIT
  debit_turbine = list(np.arange(MIN_DEBIT, max_for_turbine + PAS_DEBIT,
                                  PAS_DEBIT))
  debit_turbine[-1] = max_for_turbine
  debit_turbine = round_list(debit_turbine)

  return debit_turbine


def getOptimalSolution(stage: pd.DataFrame, turbineID: int) -> pd.DataFrame:
  xn = f"X{turbineID}"
  fn = f"F{turbineID}"

  for debit_restant in stage.index:
    # Filter out non-numeric values and convert to float
    numeric_values = stage.loc[debit_restant, 
                               stage.columns.difference([fn, xn])]
    numeric_values = numeric_values.apply(pd.to_numeric, errors='coerce')
    numeric_values = numeric_values.dropna()  # Drop NaN values

    if not numeric_values.empty:
      max_value = numeric_values.max()
      max_column = numeric_values.idxmax()
      stage.at[debit_restant, fn] = max_value
      stage.at[debit_restant, xn] = max_column
  
  return stage


def createStages(turbines: list,
                 listeEtats: Dict[int,List[int]],
                 debits_possible: List[int]):
  
  result = {}
  for i in turbines[:-1]:
    df = pd.DataFrame(index = listeEtats.get(i), columns = debits_possible)
    result[i] = df
  # La dernière turbine n'a pas de colonnes car on utilise tout le débit possible
  result[turbines[-1]] = pd.DataFrame(index = listeEtats.get(turbines[-1]), 
                                      columns = [])
  return result

def addOptimalResultCols(stage: pd.DataFrame, turbineID: int):
  xn = f"X{turbineID}"
  fn = f"F{turbineID}"
  stage[xn] = None
  stage[fn] = None
  return xn, fn

def powerFunction(debit_turbine: Union[int,float],
                  chute_nette: Union[int,float],
                  coefficients: list):
  return coefficients[0] + \
         coefficients[1] * debit_turbine +\
         coefficients[2] * chute_nette + \
         coefficients[3] * debit_turbine**2 +\
         coefficients[4] * debit_turbine * chute_nette +\
         coefficients[5] * chute_nette**2 +\
         coefficients[6] * debit_turbine**3 +\
         coefficients[7] * debit_turbine**2*chute_nette

def fillLastStage(stage: pd.DataFrame,
                  fonctionPuissance: list,
                  turbineID: int) -> pd.DataFrame: 
  
  xn, fn = addOptimalResultCols(stage, turbineID)

  for debit_restant in stage.index:
    # print(debit_restant)
    debit_turbine = debit_restant
    stage.loc[debit_restant, xn] = debit_restant
    
    chute_nette = getChuteNette(debit_turbine)
    puissance = powerFunction(debit_turbine, chute_nette, fonctionPuissance)
    stage.loc[debit_restant, fn] = puissance
  return stage



def fillPreviousStages(stage: pd.DataFrame,
                       previousStage: pd.DataFrame,
                       fonctionPuissance: list,
                       turbineID: int,
                       previousTurbineID: int,
                       turbineIndex: int,
                       nb_turbines: int) -> pd.DataFrame: 
  if MAX_DEBIT * (nb_turbines - turbineIndex) < DEBIT_TOTAL:
    debit_restant_max_for_turbine_after = MAX_DEBIT * (nb_turbines - turbineIndex) 
  else:
    debit_restant_max_for_turbine_after = DEBIT_TOTAL

  # print(f"debit total : {debit_restant_max_for_turbine_after} ")
  debit_turbine_columns = stage.columns
  addOptimalResultCols(stage, turbineID)


  for debit_restant in stage.index:
    for debit_turbine in debit_turbine_columns:
      chute_nette = getChuteNette(debit_turbine)

      debit_for_turbine_after = round(debit_restant - debit_turbine,2)
      if debit_for_turbine_after < 0 \
      or  debit_for_turbine_after > debit_restant_max_for_turbine_after \
      or  debit_for_turbine_after not in previousStage.index :
        stage.loc[debit_restant, debit_turbine] = "-"
        debit_for_turbine_after = None

      if debit_for_turbine_after != None:
        # print(f"debit_for_turbine_after")
        # print(previousStage.index)
        puissance_add = previousStage.loc[debit_for_turbine_after, f"F{previousTurbineID}"]
        puissance = puissance_add + powerFunction(debit_turbine, chute_nette, 
                                                  fonctionPuissance)       
        stage.loc[debit_restant, debit_turbine] = puissance
  
    stage = getOptimalSolution(stage, turbineID)
    
  return stage

def backwardPass(turbines: list, emptyStages):
  nb_turbines = len(turbines)
  filledStages = {}
  for i, turbineID in enumerate(turbines[::-1]):
    # print(f"Turbine {turbineID}")
    if turbineID == turbines[-1]:
      filledStages[turbineID] = fillLastStage(copy.copy(emptyStages[turbineID]),
                                  ARRAY_COEFFICIENTS_TURBINES[turbineID - 1],
                                  turbineID)
    else:
      # print("normal")
      filledStages[turbineID] = fillPreviousStages(copy.copy(emptyStages[turbineID]),
                                  copy.copy(filledStages[prevStage]),
                                  ARRAY_COEFFICIENTS_TURBINES[turbineID - 1],
                                  turbineID,
                                  prevStage,
                                  nb_turbines - i,
                                  nb_turbines)
    prevStage = turbineID
  return filledStages

def forward_pass(stage : pd.DataFrame,
                 df_tableau_turbine_after :pd.DataFrame,
                 prevStageID: int) -> pd.DataFrame:
  debit_restant = stage.index[0]
  debit_choose = stage.loc[debit_restant,f"X{prevStageID}"]

  debit_restant_after = debit_restant - debit_choose
  debit_restant_after = round(debit_restant_after,2)

  final_df = df_tableau_turbine_after.loc[[debit_restant_after]]
  return final_df

def loopForwardPass(turbines, filledStages):
    dfs_choose = {}
    prevStage = turbines[0]
    dfs_choose[prevStage] = copy.copy(filledStages[prevStage])

    for i in turbines[1:]:
      dfs_choose[i] = forward_pass(stage = copy.copy(dfs_choose[prevStage]),
                                 df_tableau_turbine_after = copy.copy(filledStages[i]),
                                 prevStageID = prevStage)
      prevStage = i
    return dfs_choose

def dynamicProgrammingAlgorithm(turbines_working):
  
  turbines = [index for index, value in enumerate(turbines_working, start=1) if value]

  listeEtats = getStates(turbines)
  # print(listeEtats)
  debits_possible = getPossibleValues()
  
  emptyStages = createStages(turbines, listeEtats, debits_possible)

  filledStages = backwardPass(turbines, emptyStages)
  # print(filledStages)
  dfs_choose = loopForwardPass(turbines, filledStages)
  return dfs_choose

def initResultDf():
  dfResult = pd.DataFrame(index=["Original", "Computed"], columns = ["Débit disponible", "Puissance totale"])
  dfResult.loc[:, "Puissance totale"] = 0
  return dfResult

def extractResults(dfResult, actives_turbines, result):
    for i, IDturbine in enumerate(actives_turbines):
      colNameDebit = "Débit T" + str(IDturbine)
      colNamePuissance = "Puissance T" + str(IDturbine)
      if (i < len(actives_turbines) - 1):
        nextTurbine = actives_turbines[i+1]
        # print(f'{IDturbine}/ {result[IDturbine]} => {nextTurbine}/{result[nextTurbine]}')


        currentPuissance = result[IDturbine][f"F{IDturbine}"].values[0] - result[nextTurbine][f'F{nextTurbine}'].values[0]
      else:
        currentPuissance = result[IDturbine]['F' + str(IDturbine)].values[0]
      currentDebit = result[IDturbine]['X'+str(IDturbine)].values[0]
      dfResult.loc["Computed", colNameDebit] = currentDebit
      dfResult.loc["Computed", colNamePuissance] = currentPuissance
      dfResult.loc["Computed", "Puissance totale"] += currentPuissance


def get_active_turbines(df_file: pd.DataFrame, excel_line_index: int) -> List[bool]:
    active_turbines = [True if df_file.loc[excel_line_index, f"P{i} (MW)"] else False for i in range(1, 6)]
    return active_turbines

def initialize_result_df(debit_total: float, debit_total_computed: float, df_file_row: pd.Series) -> pd.DataFrame:
    df_result = initResultDf()

    df_result.at["Original", "Débit disponible"] = debit_total
    df_result.at["Computed", "Débit disponible"] = debit_total_computed
    
    puissance_totale = 0
    for i in range(1, 5+1, 1):
        df_result.loc["Original", f"Débit T{i}"] = df_file_row[f"Q{i} (m3/s)"]
        df_result.loc["Original", f"Puissance T{i}"] = df_file_row[f"P{i} (MW)"]
        df_result.loc["Computed", f"Débit T{i}"] = 0
        df_result.loc["Computed", f"Puissance T{i}"] = 0
        puissance_totale += df_file_row[f"P{i} (MW)"]

    df_result.at["Original", "Puissance totale"] = puissance_totale
    
    return df_result

def find_nearest_number(reference_list, number, is_max=True):
    if is_max:
        closest = max(filter(lambda x: x <= number, reference_list))
    else:
        closest = min(filter(lambda x: x >= number, reference_list))
    return closest


def round_list(numbers, decimals=2):
    """
    Arrondit tous les nombres dans la liste 'numbers' à 'decimals' décimales.
    """
    return [round(number, decimals) for number in numbers]


def read_excel_yield(filename, starting_row, end_row) -> Iterator[pd.DataFrame]:
    yield pd.read_excel(filename, skiprows=starting_row , nrows=end_row+1)


if __name__ == "__main__":
  FILENAME = "data/DataProjet2024.xlsx"
  STARTING_ROW = 2
  ROW_COUNT = 100

  i = 0
  with open(FILENAME, 'rb') as f:
    rows = read_excel_yield(f, STARTING_ROW, ROW_COUNT)
    df_file = next(rows)
  
  # print(df_file.columns)
  sumTime = 0
  sumDifferences = 0
  nbImprovements = 0
  sumTime = 0

  plot_algo_dynamique_time = []
  plot_algo_dynamique_puissance_total = []
  plot_algo_dynamique_puissance_1 = []
  plot_algo_dynamique_puissance_2 = []
  plot_algo_dynamique_puissance_3 = []
  plot_algo_dynamique_puissance_4 = []
  plot_algo_dynamique_puissance_5 = []
  color = []
  for excel_line_index in range(len(df_file)) : 
    debit_total_original = df_file.loc[excel_line_index, "Qtot (m3/s)"]
    debit_total_computed = round(debit_total_original, 2)
    DEBIT_TOTAL = debit_total_computed
    niveau_amont = df_file.loc[excel_line_index, "Niv Amont (m)"]
  
    ref = np.arange(DEBIT_TOTAL,MIN_DEBIT - PAS_DEBIT, -PAS_DEBIT)
    REF = [round(number,2) for number in ref if number >= 0]
    # print(REF)
    
    df_result : pd.DataFrame = initialize_result_df(debit_total_original, 
                                                    debit_total_computed, 
                                                    df_file.iloc[excel_line_index])
    excel_line_actives_turbines : List[bool] = get_active_turbines(df_file, excel_line_index)
    actives_turbines = [index for index, value in enumerate(excel_line_actives_turbines, start=1) if value]
    color.append(len(actives_turbines))

    start = time()

    result = dynamicProgrammingAlgorithm(excel_line_actives_turbines)
    ttl_time = time() - start
    plot_algo_dynamique_time.append(ttl_time)

    sumTime += ttl_time

    extractResults(df_result, actives_turbines, result)
    print("----".center(200))
    print(df_result)

    plot_algo_dynamique_puissance_total.append(df_result.loc["Computed", "Puissance totale"] - df_result.loc["Original", "Puissance totale"])
    if df_result.loc["Original", "Débit T1"]:
      plot_algo_dynamique_puissance_1.append(df_result.loc["Computed", "Débit T1"] - df_result.loc["Original", "Débit T1"] )

    if df_result.loc["Original", "Débit T2"]:
      plot_algo_dynamique_puissance_2.append(df_result.loc["Computed", "Débit T2"] - df_result.loc["Original", "Débit T2"] )

    if df_result.loc["Original", "Débit T3"]:
      plot_algo_dynamique_puissance_3.append(df_result.loc["Computed", "Débit T3"] - df_result.loc["Original", "Débit T3"] )

    if df_result.loc["Original", "Débit T4"]:
      plot_algo_dynamique_puissance_4.append(df_result.loc["Computed", "Débit T4"] - df_result.loc["Original", "Débit T4"] )

    if df_result.loc["Original", "Débit T5"]:
      plot_algo_dynamique_puissance_5.append(df_result.loc["Computed", "Débit T5"] - df_result.loc["Original", "Débit T5"] )

    currentDifference = df_result.loc["Computed", "Puissance totale"] - df_result.loc["Original", "Puissance totale"]
    if currentDifference > 0:
      nbImprovements +=1
    sumDifferences += currentDifference
  print(sumDifferences)
  print(nbImprovements)
  print(f"Average time: {sumTime/ROW_COUNT}")
  plot_differences(plot_algo_dynamique_puissance_total, label="Total Power")
  plot_differences(plot_algo_dynamique_puissance_1, label="Turbine 1 Power")
  plot_differences(plot_algo_dynamique_puissance_2, label="Turbine 2 Power")
  plot_differences(plot_algo_dynamique_puissance_3, label="Turbine 3 Power")
  plot_differences(plot_algo_dynamique_puissance_4, label="Turbine 4 Power")
  plot_differences(plot_algo_dynamique_puissance_5, label="Turbine 5 Power")

  plot_time(plot_algo_dynamique_time, color)








