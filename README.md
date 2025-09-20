# Water-Futures for the Battle of Water Demand Forecasting (wf4bwdf)

This repository contains the **Water-Futures Team implementation** of the Battle of the Water Demand Forecasting (BWDF) competition.

The Battle of the Water Demand Forecasting (BWDF) was a competition organized in the context of the 3rd Water Distribution Systems Analysis and Computing and Control in the Water Industry (WDSA-CCWI) joint conference held in Ferrara, Italy in 2024 [(Alvisi et al., 2025)](#citation).

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
Evaluate the forecast following the competition requirements means that the function
works only if the forecast is a complete prediction of the original evaluation week in at least 1 DMA.
```python
import wf4bwdf as bwdf
import pandas as pd

for iteration in range(1,5):
    # Load the data for that iteration (no leak of future information) using letters instead of the numbers
    dataset = bwdf.load_iteration_dataset(iteration, use_letters_for_names=True)

    # Compute your forecast: previous week
    forecast = dataset['dma-inflows'].iloc[-168:]

    # Evaluate the forecast
    results = bwdf.evaluate(forecast)

    # Should have returned a series with the combination 'Evaluation week', DMA, and BWDF performance indicators')
    print(results)
```

## Contributing

We welcome contributions to this project! There are several exciting improvements we're looking forward to implementing, with the live leaderboard being particularly interesting, as well as offering benchmark models for comparison.

### Prerequisites

- **Python 3.11** - Required for development
- **uv** - Fast Python package installer and resolver

### Workflow

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/project-name.git
   cd project-name
   ```
3. **Install dependencies** using uv:
   ```bash
   uv sync
   ```
4. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
5. Make your changes and ensure they work properly
6. Run tests (if applicable):
   ```bash
   uv run pytest
   ```
7. Commit clearly and push your fork
   ```bash
   git commit -m "Add: description of your changes"
   git push origin feature/your-feature-name
   ```
8. **Create a Pull Request** from your fork to the main repository

If you have questions about contributing, feel free to open an issue for discussion before starting work on major features.

Thank you for contributing to the project!

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
The data used in this project have been downloaded from the open access work of Alvisi et al. (2025).
Those data are available under the terms of Creative Commons Attribution 4.0 International license, https://creativecommons.org/licenses/by/4.0/.

## Citation

If you use this implementation in your research, please cite the original paper:

```bibtex
@article{alvisi2025bwdf,
title={Battle of Water Demand Forecasting},
volume={151},
rights={This work is made available under the terms of the Creative Commons Attribution 4.0 International license, https://creativecommons.org/licenses/by/4.0/.},
DOI={10.1061/JWRMD5.WRENG-6887},
number={10},
journal={Journal of Water Resources Planning and Management},
publisher={American Society of Civil Engineers},
author={Alvisi, S. and Franchini, M. and Marsili, V. and Mazzoni, F. and Salomons, E. and Housh, M. and Abokifa, A. and Arsova, K. and Ayyash, F. and Bae, H. and Barreira, R. and Basto, L. and Bayer, S. and Berglund, E. Z. and Biondi, D. and Boloukasli Ahmadgourabi, F. and Brentan, B. and Caetano, J. and Campos, F. and Cao, H. and Cardona, S. and Carreño Alvarado, E. P. and Carriço, N. and Chatzistefanou, G.-A. and Coy, Y. and Creaco, E. and Cuomo, S. and de Klerk, A. and Di Nardo, A. and DiCarlo, M. and Dittmer, U. and Dziedzic, R. and Ebrahim Bakhshipour, A. and Eliades, D. and Farmani, R. and Ferreira, B. and Gabriele, A. and Gamboa-Medina, M. M. and Gao, F. and Gao, J. and Gargano, R. and Geranmehr, M. and Giudicianni, C. and Glynis, K. and Gómez, S. and González, L. and Groß, M. and Guo, H. and Habibi, M. N. and Haghighi, A. and Hammer, B. and Hans, L. and Hayslep, M. and He, Y. and Hermes, L. and Herrera, M. and Hinder, F. and Hou, B. and Iglesias-Rey, A. and Iglesias-Rey, P. L. and Jang, I.-S. and Izquierdo, J. and Jahangir, M. S. and Jara-Arriagada, C. and Jenks, B. and Johnen, G. and Kalami Heris, M. and Kalumba, M. and Kang, M.-S. and Khashei Varnamkhasti, M. and Kim, K.-J. and Kley-Holsteg, J. and Ko, T. and Koochali, A. and Kossieris, P. and Koundouri, P. and Kühnert, C. and Kulaczkowski, A. and Lee, J. and Li, K. and Li, Y. and Liu, H. and Liu, Y. and López-Hojas, C. A. and Maier, A. and Makropoulos, C. and Martínez-Solano, F. J. and Marzouny, N. H. and Menapace, A. and Michalopoulos, C. and Moraitis, G. and Mousa, H. and Namdari, H. and Nikolopoulos, D. and Oberascher, M. and Ostfeld, A. and Pagano, M. and Pasha, F. and Perafán, J. and Perelman, G. and Pesantez, J. and Polycarpou, M. and Quarta, M. G. and Que, Q. and Quilty, J. and Quintiliani, C. and Ramachandran, A. and Reynoso Meza, G. and Rodriguez, V. and Romano, Y. and Saldarriaga, J. and Salem, A. K. and Samartzis, P. and Santonastaso, G. F. and Savic, D. and Schiano Di Cola, V. and Schol, D. and Seyoum, A. G. and Shen, R. and Simukonda, K. and Sinske, A. and Sitzenfrei, R. and Sonnenschein, B. and Stoianov, I. and Tabares, A. and Todini, E. and Tsiami, L. and Tsoukalas, I. and Ulusoy, A.-J. and Vamvakeridou-Lyroudia, L. and van Heerden, A. and Vaquet, J. and Vaquet, V. and Wallner, S. and Walraad, M. and Wang, D. and Wu, S. and Wu, W. and Wunsch, A. and Yao, Y. and Yu, J. and Zanfei, A. and Zanutto, D. and Zhang, H. and Ziebarth, M. and Ziel, F. and Zou, J.},
year={2025},
pages={04025049}
} 
```

Follow this link to read the [Battle of the Water Demand Forecasting paper](https://ascelibrary.org/doi/full/10.1061/JWRMD5.WRENG-6887).

---

*This repository is mantained on initiative of the Water-Futures team.
WOULD BE NICE TO SAY THAT WE RECEIVED THE ENDORSEMNET OF THE COMPETITION ORGANISER AND LET LINK TO UNI FERRARA
Explore more of our projects on [GitHub](https://github.com/WaterFutures) and learn about our team and work on our [website](https://waterfutures.eu/).*

*Water-Futures has received funding from the European Research Council (ERC) under the European Union’s Horizon 2020 research and innovation program (Grant Agreement No. 951424).*
