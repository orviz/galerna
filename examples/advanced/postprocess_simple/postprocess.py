from pathlib import Path


def process_case(context, galerna=None):
    """Simple postprocess function used by the example.

    Writes a small file into the case directory containing the case_num
    and shows how to access the Galerna instance if needed.
    """
    case_dir = Path(context["case_dir"])
    case_dir.mkdir(parents=True, exist_ok=True)
    out = case_dir / "postprocess.txt"
    info = f"case_num={context.get('case_num')} x={context.get('x')}\n"
    if galerna is not None:
        info += f"output_dir={galerna.output_dir}\n"
    out.write_text(info)
