"""Unit tests for dataset provenance and namespace enforcement."""

import pytest
from mcdl.research.provenance import Namespace, compute_bytes_sha256, create_dataset_provenance


def test_bytes_sha256():
    data = b"Mastercard AI Defense Lab"
    h = compute_bytes_sha256(data)
    assert len(h) == 64
    assert h == compute_bytes_sha256(data)


def test_create_dataset_provenance_valid():
    prov = create_dataset_provenance(
        dataset_name="Sparkov Benchmark",
        source_url="https://kaggle.com/datasets/kartik2112/fraud-detection",
        license_type="CC0",
        namespace=Namespace.REAL_WORLD,
        sample_count=1000,
        positive_count=5,
        split_method="temporal",
    )
    assert prov["namespace"] == "REAL_WORLD"
    assert prov["fraud_rate"] == 0.005
    assert prov["dataset_name"] == "Sparkov Benchmark"


def test_invalid_namespace():
    with pytest.raises(ValueError, match="Invalid namespace"):
        create_dataset_provenance(
            dataset_name="Fake",
            source_url="",
            license_type="",
            namespace="UNAUTHORIZED_NAMESPACE",
            sample_count=10,
            positive_count=1,
            split_method="",
        )
