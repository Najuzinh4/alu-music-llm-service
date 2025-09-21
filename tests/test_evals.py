from pathlib import Path
from scripts import run_evals


def test_run_evals_tmp_dataset(tmp_path: Path):
    #cria dataset pequeno
    ds = tmp_path / 'evals.jsonl'
    ds.write_text(
        '\n'.join([
            '{"texto": "Amei o álbum", "categoria": "ELOGIO"}',
            '{"texto": "O clipe está horrível e tenebroso", "categoria": "CRÍTICA"}',
        ]),
        encoding='utf-8'
    )

    out = tmp_path / 'report.json'
    code = run_evals.main(["--data", str(ds), "--out", str(out)])
    assert code == 0
    assert out.exists()

