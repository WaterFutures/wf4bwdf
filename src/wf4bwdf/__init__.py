from ._data_loading import load_complete_dataset, load_iteration_dataset

def hello() -> str:
    print("Complete dataset:")
    print(load_complete_dataset())
    print("Filtered iter 1:")
    print(load_iteration_dataset(1, use_letters_for_names=True))
    return "Hello from WF 4 BWDF!"