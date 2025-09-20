from pathlib import Path


import wf4bwdf as bwdf

def load_solutions():
    data_path = Path(__file__).parent.parent / "submissions" / "BWDFCompetitorsSolutions.xlsx"
    print(data_path)
    solutions = bwdf.bwdf_competitors_solutions(data_path)

    for team, solution in solutions.items():
        print("-----")
        print(f"Team: {team}")
        print()
        print(bwdf.evaluate(solution))
              
    return

def hello() -> str:
    print("Complete dataset:")
    print(bwdf.load_complete_dataset())
    print("Filtered iter 1:")
    print(bwdf.load_iteration_dataset(1, use_letters_for_names=True))
    return "Hello from WF 4 BWDF!"

if __name__ == '__main__':
    load_solutions()
    hello()