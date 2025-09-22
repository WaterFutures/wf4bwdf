# Water-Futures for the Battle of Water Demand Forecasting (wf4bwdf)

This repository contains the **Water-Futures Team implementation** of the Battle of the Water Demand Forecasting (BWDF) competition.

The Battle of the Water Demand Forecasting (BWDF) was a competition organized in the context of the 3rd Water Distribution Systems Analysis and Computing and Control in the Water Industry (WDSA-CCWI) joint conference held in Ferrara, Italy in 2024 [(Alvisi et al., 2025)](https://ascelibrary.org/doi/full/10.1061/JWRMD5.WRENG-6887).

> This repository is our open-source implementation created to fulfill the Water-Futures mission of making water research tools freely available.

This repository provides an easy-to-use Python package that allows researchers to:

- **Quickly load** the competition data
- **Evaluate models** using the original competition workflow  

---
## Installation

You can install the package using pip:

```bash
pip install wf4bwdf
```

All required dependencies are installed automatically with pip. See `pyproject.toml` for details.
The project has a minimal dependency, from Python 3.9 and pandas above 2.1 it should work.

A **lightweight implementation** of this package is also available through the [WaterBenchmarkHub](https://waterfutures.github.io/WaterBenchmarkHub/), which includes only the core functions to load data in memory and evaluate forecasts.

## Usage Examples

### 1. Load complete dataset
The function `load_complete_dataset`  provides access to **DMA inflows and weather data** from the supplementary information of Alvisi et al., (2025) and **also calendar information and other problem metadata** readily available in machine-readable format.

```python
import wf4bwdf as bwdf

dataset = bwdf.load_complete_dataset()

# Print DMA description
print(dataset['dma-properties']['Description'])

# Plot DMA 3(C) inflow
dma_c_inflow = dataset['dma-inflows']['DMA 3']
# plot the series
```

### 2. Evaluate forecasts following the competition requirements
Evaluate the forecast following the competition requirements means that the `evaluate` function works only if the forecast is a complete prediction of one the original evaluation weeks and of at least 1 DMA.
```python
import wf4bwdf as bwdf
import pandas as pd

for iteration in range(1,5):
    # Load the data for that iteration (no leak of future information) using letters instead of the numbers (e.g., 'DMA C')
    dataset = bwdf.load_iteration_dataset(iteration, use_letters_for_names=True)

    # Compute your forecast: previous week
    forecast = dataset['dma-inflows'].iloc[-168:]
    forecast.index = forecast.index + pd.Timedelta(weeks=1)

    # Evaluate the forecast
    results = bwdf.evaluate(forecast)

    # Should have returned a series with the combination 'Evaluation week', DMA, and BWDF performance indicators')
    print(results)
```

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

The data used in this project have been downloaded from the open access work of Alvisi et al. (2025).
Those data are available under the terms of Creative Commons Attribution 4.0 International license, https://creativecommons.org/licenses/by/4.0/.

## How to Cite?

If you use this implementation of the BWDF in your research, please cite the original paper that you can find here: [Battle of the Water Demand Forecasting paper](https://ascelibrary.org/doi/full/10.1061/JWRMD5.WRENG-6887).

Use the "Cite this repository" button in the About section (right sidebar) to copy the citation in your preferred format.

---

*This repository is mantained on initiative of the Water-Futures team.
WOULD BE NICE TO SAY THAT WE RECEIVED THE ENDORSEMNET OF THE COMPETITION ORGANISER AND LET LINK TO UNI FERRARA
Explore more of our projects on [GitHub](https://github.com/WaterFutures) and learn about our team and work on our [website](https://waterfutures.eu/).*

*Water-Futures has received funding from the European Research Council (ERC) under the European Union’s Horizon 2020 research and innovation program (Grant Agreement No. 951424).*
