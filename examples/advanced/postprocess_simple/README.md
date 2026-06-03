# Postprocess example

This example demonstrates the configured in-process postprocessing feature.

Files:

- `galerna.yaml`: config that defines two cases and a `postprocess` script.
- `postprocess.py`: the script with a `process_case(context, galerna)` function.

Run the example:

```bash
cd examples/postprocess_simple
galerna build
galerna run
galerna postprocess
```

After `galerna postprocess` completes, check `runs/<case_id>/postprocess.txt` files.
