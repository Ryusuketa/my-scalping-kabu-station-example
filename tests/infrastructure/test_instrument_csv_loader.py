from my_scalping_kabu_station_example.infrastructure.persistence.instrument_csv_loader import load_instruments


def test_load_instruments_reads_symbols_and_metadata(tmp_path) -> None:
    csv_path = tmp_path / "instruments.csv"
    csv_path.write_text("symbol,exchange\nTEST,TSE\nFOO,OSE\n", encoding="ascii")

    instruments = load_instruments(str(csv_path))

    assert [inst.symbol for inst in instruments.instruments] == ["TEST", "FOO"]
    assert instruments.instruments[0].metadata == {"exchange": "TSE"}
