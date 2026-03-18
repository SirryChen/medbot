import httpx
import pytest

from medbot.agent.tools.drug_interaction import DrugInteractionCheckTool


def _response(status: int = 200, json_data: dict | None = None) -> httpx.Response:
    response = httpx.Response(status, json=json_data)
    response._request = httpx.Request("GET", "https://mock")
    return response


@pytest.mark.asyncio
async def test_drug_interaction_check_success(monkeypatch) -> None:
    async def mock_get(self, url, **kwargs):
        url_text = str(url).lower()
        if "omeprazole" in url_text:
            return _response(
                json_data={
                    "data": [
                        {"name": "Omeprazole", "internalID": "DDInter1340"},
                        {"name": "Omega-3 fatty acids", "internalID": "DDInter1339"},
                    ]
                }
            )
        if "fosphenytoin" in url_text:
            return _response(json_data={"data": [{"name": "Fosphenytoin", "internalID": "DDInter783"}]})
        raise AssertionError(f"Unexpected URL: {url}")

    async def mock_post(self, url, **kwargs):
        assert str(url).endswith("/ddinter/checker/")
        assert kwargs["content"] == "choices=DDInter1340&choices=DDInter783"
        return _response(
            json_data={
                "state": "success",
                "data": [
                    {
                        "drug_a_name": "Omeprazole",
                        "drug_b_name": "Fosphenytoin",
                        "idx__level": "Moderate",
                        "idx__interaction_description": "May increase phenytoin serum concentrations.",
                        "idx__management": "Monitor and consider dosage adjustment.",
                        "id": 981463,
                    }
                ],
                "level": {"0": 0, "1": 0, "2": 1, "3": 0},
            }
        )

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)
    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    tool = DrugInteractionCheckTool()
    result = await tool.execute(drugs=["Omeprazole", "Fosphenytoin"])

    assert "Resolved drugs: Omeprazole [DDInter1340], Fosphenytoin [DDInter783]" in result
    assert "Severity counts: major=0, moderate=1, minor=0, unknown=0" in result
    assert "Omeprazole <-> Fosphenytoin" in result
    assert "Monitor and consider dosage adjustment." in result


@pytest.mark.asyncio
async def test_drug_interaction_check_reports_ambiguity(monkeypatch) -> None:
    async def mock_get(self, url, **kwargs):
        if "ome" in str(url).lower():
            return _response(
                json_data={
                    "data": [
                        {"name": "Omeprazole", "internalID": "DDInter1340"},
                        {"name": "Omega-3 fatty acids", "internalID": "DDInter1339"},
                    ]
                }
            )
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    tool = DrugInteractionCheckTool()
    result = await tool.execute(drugs=["ome", "warfarin"])

    assert "ambiguous drug name 'ome'" in result
    assert "Omeprazole [DDInter1340]" in result


@pytest.mark.asyncio
async def test_drug_interaction_check_requires_two_drugs() -> None:
    tool = DrugInteractionCheckTool()
    result = await tool.execute(drugs=["Omeprazole"])
    assert "at least two drug names" in result
