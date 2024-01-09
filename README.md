# Supplementary data for the PTSP anf the IPODS-MP
Supplementary data for research on the PTSP and its extension, the IPODS-MP.

## Benchmark

### Benchmark for the PTSP

Folder [```instances/geismar```](./instances/geismar/) contains the *customer-instances* of Geismar et al. (2008).
File ```instance_i<instance>``` refers to the ```i```th customer-instance ```(1,2,3,4,5,6)```.

Each customer-instance is given in a JSON format as a list of locations with their coordinates (```'x'``` and ```'y'```) and demand (```'demand'```).
The first location refers to the plant, the others refer to the customers.
For example:
```
[
  { "demand":    0, "x":    0, "y":    0 },
  { "demand":  271, "x":   83, "y":   80 },
  { "demand":  169, "x":   86, "y":  -33 },
  ...
  { "demand":  186, "x":   33, "y":  -57 },
  { "demand":  167, "x":   83, "y":   41 },
  { "demand":  279, "x":   73, "y":  -49 }
]
```

Each of the 6 customer-instances is considered with capacity from $\{300,600\}$, lifespan from $\{300,600\}$, and production rate from $\{1,2,3\}$.
These $6\times 2\times 2\times 3 = 72$ *instances* constitute the benchmark dataset.

### Benchmark for the IPODS-MP

Folder [```instances/canatasagun```](./instances/canatasagun/) contains the *customer-instances* of Can Atasagun, G., & Karaoğlan, İ. (2024).
File ```instance_dem<demand distribution>_loc<space distribution>_n<customers>_p<plants>_i<instance>.json``` refers to the ```i```th customer-instance ```(1,2,3)``` with the given demand distribution ```(1,2)```, space distribution ```(1,2,3)```, number of customers ```(10,20,30,40,50,100)```, and number of plants ```(2,3,4,5)```.

Each customer-instance is given in JSON format as for the PTSP, where the first locations (with zero demand) refer to the plants, the others refer to the customers.

## Solutions

### Solutions for the PTSP

Folder [```solutions/geismar```](./solutions/geismar/) contains solutions for the benchmark dataset of Geismar et al. (2008).
- [```lacomme_et_al```](./solutions/geismar/lacomme_et_al/): solutions of Lacomme et al. (2018) obtained from [the webpage of the authors](https://perso.isima.fr/~lacomme/marina/Research/PTSP_Results.html).
- [```horvath_vns```](./solutions/geismar/horvath_vns/): solutions of the variable neighborhood search of Horváth (2024).
- [```best_known```](./solutions/geismar/best_known/): best known solutions.

File ```sol_i<instance>_Q<capacity>_B<lifespan>_r<production rate>.json``` refers to a solution for the corresponding instance ```(1,2,3,4,5,6)``` with the corresponding capacity ```(300,600)```, lifespan ```(300,600)```, and production rate ```(1,2,3)```.

Each solution is given in a JSON format as a list of batches, where each batch is a list of customer indices.
For example:
```
[
  [28, 4],  [9, 22, 13],  [40, 10, 35],  [15, 19, 1],  [3, 18, 21],  [14, 23, 16],  [7, 17, 25],  [20, 6, 8],  [26, 29],  [31, 32, 33, 24],  [12, 30, 2],  [34, 37],  [36, 38, 11],  [27, 5, 39]
]
```

### Solutions for the IPODS-MP

Folder [```solutions/canatasagun```](./solutions/canatasagun/) contains solutions for the benchmark dataset of Can Atasagun, G., & Karaoğlan, İ. (2024).
- [```horvath_vns```](./solutions/canatasagun/horvath_vns/): solutions of the variable neighborhood search of Horváth (2024).

File ```sol_dem<demand distribution>_loc<space distribution>_n<number of customers>_p<number of plants>_i<instance>_Q<capacity>_B<lifespan>_r<production rate>.json``` refers to a solution for instance ```instance_dem<demand distribution>_loc<space distribution>_n<number of customers>_p<number of plants>_i<instance>``` with the corresponding capacity ```(300,600)```, lifespan ```(300,600)```, and production rate ```(1,2,3)```.

Each solution is given in JSON format as a list of routes, where each route is a list of batches, and each batch is a list of customer indices.
For example:
```
[
  [ [2], [3], [5], [10] ],
  [ [6, 7], [11, 8], [4], [9] ]
]

```

## Evaluator

Functions in file [```evaluator.py```](./evaluator.py) can be used to evaluate solutions given in the form described above.

## References
Geismar, H. N., Laporte, G., Lei, L., & Sriskandarajah, C. (2008). *The integrated production and transportation scheduling problem for a product with a short lifespan*. INFORMS Journal on Computing, 20(1), 21-33.

Lacomme, P., Moukrim, A., Quilliot, A., & Vinot, M. (2018). *Supply chain optimisation with both production and transportation integration: multiple vehicles for a single perishable product*. International Journal of Production Research, 56(12), 4313-4336.

Can Atasagun, G., & Karaoğlan, İ. (2024). *Solution approaches for the integrated production and outbound distribution scheduling problem with multiple plants and perishable items*. Expert Systems with Applications, 237, 121318.

Horváth, M. (2024). *New computational results for integrated production and transportation problems for a product with a short lifespan*. Submitted article.
