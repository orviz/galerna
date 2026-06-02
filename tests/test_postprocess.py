from pathlib import Path
import textwrap

from galerna import Galerna


def test_inprocess_postprocess_script(tmp_path):
    # create a small script that writes a file into the case_dir
    script = tmp_path / "postproc.py"
    script.write_text(
        textwrap.dedent(
            """
def process_case(context, galerna):
    from pathlib import Path
    p = Path(context['case_dir'])
    p.mkdir(parents=True, exist_ok=True)
    (p / 'post.txt').write_text(str(context['case_num']))
"""
        )
    )

    params = {
        "templates_dir": None,
        "output_dir": str(tmp_path / "runs"),
        "variable_parameters": {"x": [1, 2]},
        "mode": "one_by_one",
        "command": "echo {{x}}",
        "postprocess": {"script": str(script), "function": "process_case", "mode": "inprocess"},
    }

    g = Galerna(**params)

    # ensure case dirs exist
    for ctx in g.cases_context:
        Path(ctx['case_dir']).mkdir(parents=True, exist_ok=True)

    n = g.postprocess_cases()
    assert n == 2
    for ctx in g.cases_context:
        assert (Path(ctx['case_dir']) / 'post.txt').exists()
