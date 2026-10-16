import pytest

from engine import recalc as rc


def test_missing_soffice_raises(monkeypatch, tmp_path):
    monkeypatch.setenv("SOFFICE_BIN", "")
    monkeypatch.setattr(rc.shutil, "which", lambda name: None)
    p = tmp_path / "x.xlsx"
    p.write_bytes(b"not really")
    with pytest.raises(rc.RecalcError, match="soffice not found"):
        rc.recalc(p)


def test_cli_usage():
    assert rc.main([]) == 2


def test_scan_counts_formulas_without_libreoffice(cafe_xlsx):
    res = rc.scan_errors(cafe_xlsx)
    assert res.total_formulas > 1000
    assert res.total_errors == 0
    assert res.ok
