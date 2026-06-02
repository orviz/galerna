# Example: File-backed variable parameters and scalar broadcasting

This example shows how to load variable values from a CSV file and how scalars
are broadcast in `one_by_one` mode.

Steps:

- `stations.csv` contains one station id per line.
- `galerna.yaml` uses `station: "file:stations.csv"` to load those values.
- `scalar: 10` is a scalar that will be repeated to match the number of stations.

Run:

```bash
cd examples/directories/06_file_parameters
galerna build
galerna run
galerna status
```
