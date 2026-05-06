import json

import report
import pytest


@pytest.fixture(scope="session")
def report_json():
    print("\n[ Fixture ]: requested...")
    report.generate_report()

    with open("report.json") as file:
        print("\n[ Fixture ]: return report data")
        return json.load(file)


def test_report_json(report_json):
    print("\n[ Test ]: recieved -", report_json)
    assert type(report_json) == dict  # noqa: E721


def test_report_fields(report_json):
    print("\n[ Test ]: recieved -", report_json)
    assert "timestamp" in report_json
    assert "status" in report_json
