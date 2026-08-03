# tests/test_run_pipeline.py
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from pipeline.run_pipeline import run_pipeline
from pipeline.extract import Extractor
from pipeline.transform import Transformer
from pipeline.quality import DataQualityValidator
from pipeline.load import Loader


@patch("pipeline.run_pipeline.Loader", autospec=True)
@patch("pipeline.run_pipeline.DataQualityValidator", autospec=True)
@patch("pipeline.run_pipeline.Transformer", autospec=True)
@patch("pipeline.run_pipeline.Extractor", autospec=True)
@patch("pipeline.run_pipeline.EsiosClient", autospec=True)
def test_run_pipeline_happy_path(
    mock_client_cls, mock_extractor_cls, mock_transformer_cls,
    mock_validator_cls, mock_loader_cls,
):
    # Extract
    mock_extractor_cls.return_value.extract_indicator.return_value = {
        "filepath": Path("fake.json"),
        "metadata": {"name": "Demanda real"},
    }

    # Transform
    df = pd.DataFrame({"value": [1.0, 2.0]})
    mock_transformer_cls.return_value.build_dataframe.return_value = {
        "df": df,
        "metadata": {"name": "Demanda real", "short_name": "Demanda real"},
        "metricas_limpieza": {"filas_finales": 2},
    }

    # Quality
    mock_validator_cls.return_value.validate.return_value = {"estado": "EXITOSO"}

    result = run_pipeline(indicator_id=1293, start_date="2026-01-01", end_date="2026-01-31")

    mock_extractor_cls.return_value.extract_indicator.assert_called_once_with(
        1293, "2026-01-01", "2026-01-31", None, None
    )
    mock_transformer_cls.return_value.build_dataframe.assert_called_once_with(Path("fake.json"))
    mock_validator_cls.return_value.validate.assert_called_once()
    mock_loader_cls.return_value.load_staging.assert_called_once()

    assert result == {
        "indicator_id": 1293,
        "quality_report": {"estado": "EXITOSO"},
        "loaded_rows": 2,
    }