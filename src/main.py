from TestMultipleBlackBox import TestMultipleBlackBox

if __name__ == "__main__":
    FILENAME = "data/DataProjet2024.xlsx"
    STARTING_ROW = 2
    ROW_COUNT = 100
    i = 0
    multiple_bb = TestMultipleBlackBox(FILENAME, STARTING_ROW, ROW_COUNT)
    multiple_bb.runSimulations()
    multiple_bb.getResults()