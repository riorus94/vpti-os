"""Web Search Strategy routing (#8). Pure. The compliance guardrail is the
critical behavior: compliance/regulation/internal-process never reach the web."""

from vaos.domain.intent import Intent
from vaos.modules.web_search import SearchMode, mode_for


def test_compliance_never_uses_web() -> None:
    assert mode_for(Intent.COMPLIANCE) is SearchMode.INTERNAL


def test_strategy_uses_hybrid() -> None:
    assert mode_for(Intent.STRATEGY) is SearchMode.HYBRID


def test_opportunity_uses_hybrid() -> None:
    assert mode_for(Intent.OPPORTUNITY) is SearchMode.HYBRID


def test_risk_uses_internal() -> None:
    # risk is the INTERNAL default — this guards that default, no web for risk.
    assert mode_for(Intent.RISK) is SearchMode.INTERNAL


def test_web_source_domain_list_parses_and_trims() -> None:
    from vaos.config import Settings

    s = Settings(web_source_domains=" anindya.biz , *.anindya.biz ,, scisi.co.id ")
    assert s.web_source_domain_list() == ["anindya.biz", "*.anindya.biz", "scisi.co.id"]


def test_empty_web_source_domains_means_unscoped() -> None:
    from vaos.config import Settings

    assert Settings(web_source_domains="").web_source_domain_list() == []


def test_configured_domains_reach_the_tavily_adapter() -> None:
    from vaos.app import _build_web
    from vaos.config import Settings

    web = _build_web(Settings(tavily_api_key="tvly-key", web_source_domains="anindya.biz"))

    assert web is not None
    assert web._include_domains == ["anindya.biz"]  # composition root passes the watched list
