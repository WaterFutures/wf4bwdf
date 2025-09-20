import pytest
from pathlib import Path

import wf4bwdf as bwdf
"""
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
"""

def test_example1():
    dataset = bwdf.load_complete_dataset()
    # Print DMA description
    print(dataset['dma-properties']['Description'])

    # Plot DMA 3(C) inflow
    dma_c_inflow = dataset['dma-inflows']['DMA 3']
    # plot the series
    print(dma_c_inflow)

def test_example2():
    for iteration in range(1,5):
        # Load the data for that iteration (no leak of future information) using letters instead of the numbers
        dataset = bwdf.load_iteration_dataset(iteration, use_letters_for_names=True)

        # Compute your forecast: previous week
        forecast = dataset['dma-inflows'].iloc[-2*168:-168]
        forecast.index = dataset['dma-inflows'].iloc[-168:].index

        # Evaluate the forecast
        results = bwdf.evaluate(forecast)

        # Should have returned a series with the combination 'Evaluation week', DMA, and BWDF performance indicators')
        print(results)

if __name__ == '__main__':
    test_example1()
    test_example2()