"""Focused tests for `examples/directories/01_local_with_templates/galerna.yaml`.

These validate that `mode: all_combinations` produces the Cartesian
product of the provided `variable_parameters` values.
"""

import yaml
from pathlib import Path

from galerna import Galerna


def _params_for_example(path: Path, tmp_path: Path) -> dict:
    config = yaml.safe_load(path.read_text()) or {}
    params = config.copy()
    for key in ("wrapper", "wrapper_code", "wrapper_class"):
        params.pop(key, None)
    # Use an isolated output dir and avoid requiring templates on disk
    params["output_dir"] = str(tmp_path / "runs")
    params["templates_dir"] = None
    return params


def test_all_combinations_station_compiler(tmp_path):
    """`all_combinations` should produce the Cartesian product of lists.

    The example defines:
      station: [1, 2]
      compiler: ["gcc", "intel"]

    Expect 4 contexts with all (station, compiler) pairs.
    """
    example_path = Path("examples/directories/01_local_with_templates/galerna.yaml")
    params = _params_for_example(example_path, tmp_path)

    wrapper = Galerna(**params)

    assert wrapper.mode == "all_combinations"
    assert len(wrapper.cases_context) == 4

    pairs = {(c["station"], c["compiler"]) for c in wrapper.cases_context}
    expected = {(1, "gcc"), (1, "intel"), (2, "gcc"), (2, "intel")}
    assert pairs == expected

    # Command is defined as a static string in the example
    assert all(c["command_cmd"] == "python run_case.py" for c in wrapper.cases_context)


def test_one_by_one_station_compiler(tmp_path):
    """`one_by_one` should pair values by position, not Cartesian product.

    Using the same example inputs:
        station: [1, 2]
        compiler: ["gcc", "intel"]

    Expect 2 contexts: (1,gcc) and (2,intel).
    """
    example_path = Path("examples/directories/01_local_with_templates/galerna.yaml")
    params = _params_for_example(example_path, tmp_path)
    # override mode to one_by_one for this test
    params["mode"] = "one_by_one"

    wrapper = Galerna(**params)

    assert wrapper.mode == "one_by_one"
    assert len(wrapper.cases_context) == 2

    pairs = [(c["station"], c["compiler"]) for c in wrapper.cases_context]
    assert pairs == [(1, "gcc"), (2, "intel")]
    assert all(c["command_cmd"] == "python run_case.py" for c in wrapper.cases_context)


def test_one_by_one_scalar_broadcast(tmp_path):
    """Scalars should be broadcast to match vector lengths in one_by_one mode."""
    example_path = Path("examples/directories/01_local_with_templates/galerna.yaml")
    params = _params_for_example(example_path, tmp_path)

    # Override variable_parameters with a vector + scalar
    params["variable_parameters"] = {"l": [1, 2, 3], "scalar": 10}
    params["mode"] = "one_by_one"
    params["command"] = "echo {{l}} {{scalar}}"

    wrapper = Galerna(**params)

    assert wrapper.mode == "one_by_one"
    assert len(wrapper.cases_context) == 3

    ls = [c["l"] for c in wrapper.cases_context]
    esc = [c["scalar"] for c in wrapper.cases_context]
    assert ls == [1, 2, 3]
    assert esc == [10, 10, 10]

    assert [c["command_cmd"] for c in wrapper.cases_context] == [
        "echo 1 10",
        "echo 2 10",
        "echo 3 10",
    ]


def test_all_combinations_with_scalar(tmp_path):
    """Scalars in all_combinations should be treated as single-element lists."""
    example_path = Path("examples/directories/01_local_with_templates/galerna.yaml")
    params = _params_for_example(example_path, tmp_path)

    # station is a list, scalar should be treated as [10]
    params["variable_parameters"] = {"station": [1, 2], "scalar": 10}
    params["mode"] = "all_combinations"
    params["command"] = "echo {{station}} {{scalar}}"

    wrapper = Galerna(**params)

    assert wrapper.mode == "all_combinations"
    assert len(wrapper.cases_context) == 2

    pairs = {(c["station"], c["scalar"]) for c in wrapper.cases_context}
    assert pairs == {(1, 10), (2, 10)}
    assert [c["command_cmd"] for c in wrapper.cases_context] == ["echo 1 10", "echo 2 10"]


def test_variable_parameters_from_csv_file_string_syntax(tmp_path):
    """Support loading a simple CSV via the 'file:' shorthand string."""
    csv_path = tmp_path / "stations.csv"
    csv_path.write_text("1\n2\n3\n")

    params = {
        "templates_dir": None,
        "output_dir": str(tmp_path / "runs"),
        "variable_parameters": {"station": f"file:{csv_path}"},
        "mode": "one_by_one",
        "command": "echo {{station}}",
    }

    g = Galerna(**params)
    assert len(g.cases_context) == 3
    assert [c["station"] for c in g.cases_context] == ["1", "2", "3"]


def test_variable_parameters_from_tsv_file_dict_syntax(tmp_path):
    """Support loading a TSV with a header via dict syntax and column selection."""
    tsv_path = tmp_path / "stations.tsv"
    tsv_path.write_text("id\tname\n10\tA\n20\tB\n")

    params = {
        "templates_dir": None,
        "output_dir": str(tmp_path / "runs"),
        "variable_parameters": {
            "station": {"file": str(tsv_path), "format": "tsv", "column": "id"}
        },
        "mode": "one_by_one",
        "command": "echo {{station}}",
    }

    g = Galerna(**params)
    assert len(g.cases_context) == 2
    assert [c["station"] for c in g.cases_context] == ["10", "20"]


def test_example_dict_file_syntax(tmp_path):
    """Exercise the example `galerna_tsv.yaml` using dict file syntax.

    Copy the example directory to a temporary location and point the
    `file` path to the copied TSV so resolution is unambiguous.
    """
    import shutil

    src = Path("examples/directories/06_file_parameters")
    dst = tmp_path / "example"
    shutil.copytree(src, dst)

    example_path = dst / "galerna_tsv.yaml"
    params = _params_for_example(example_path, tmp_path)

    # Ensure file path is absolute so Galerna can find it regardless of cwd
    params["variable_parameters"]["station"]["file"] = str(dst / "stations.tsv")

    g = Galerna(**params)
    assert [c["station"] for c in g.cases_context] == ["10", "20"]