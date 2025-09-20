from pathlib import Path

import pandas as pd

from wf4bwdf._data_loading import load_complete_dataset, load_iteration_dataset
from wf4bwdf._solution_evaluation import evaluate

from wf4bwdf._data_loading import _preprocess_date_column, DMAS_NUMERICAL_NAMES

def load_solutions():
    data_path = Path(__file__).parent.parent / "submissions" / "BWDFCompetitorsSolutions.xlsx"
    print(data_path)
    solutions = pd.read_excel(data_path, sheet_name=None)

    for team, solution in solutions.items():
        solution = solution.iloc[:, 1:]
        solution = _preprocess_date_column(solution)
        solution.columns = DMAS_NUMERICAL_NAMES
        print("-----")
        print(f"Team: {team}")
        print()
        print(evaluate(solution))
              
    return

def hello() -> str:
    print("Complete dataset:")
    print(load_complete_dataset())
    print("Filtered iter 1:")
    print(load_iteration_dataset(1, use_letters_for_names=True))
    return "Hello from WF 4 BWDF!"

if __name__ == '__main__':
    load_solutions()
    hello()