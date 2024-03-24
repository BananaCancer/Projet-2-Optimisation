import pickle
from TestMultipleSimulations import TestMultipleSimulations
def saveResults(data: object, filename: str):
    file = open(filename, 'wb')
    pickle.dump(data, file)
    file.close()

if __name__ == "__main__":
    FILENAME = "data/DataProjet2024.xlsx"
    STARTING_ROW = 2
    ROW_COUNT = 100
    i = 0
    multi_sim = TestMultipleSimulations(FILENAME, STARTING_ROW, ROW_COUNT, ["BB", "ProgDyn"])
    multi_sim.runSimulations(1000)
    multi_sim.getResults()
    saveResults(multi_sim, 'data/outputbb')