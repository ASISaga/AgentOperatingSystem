"""Tests for AOS Client SDK observability module."""

import pytest
from aos_client.observability import (
    ObservabilityConfig,
    CorrelationContext,
    StructuredLogger,
    MetricsCollector,
    HealthCheck,
    get_correlation_context,
    set_correlation_context,
    correlation_scope,
    get_metrics_collector,
    get_health_check,
    create_structured_logger,
)


class TestObservabilityConfig:
    def test_defaults(self):
        config = ObservabilityConfig()
        assert config.structured_logging is True
        assert config.correlation_tracking is True
        assert config.metrics_endpoint is None

    def test_custom(self):
        config = ObservabilityConfig(
            structured_logging=False,
            metrics_endpoint="/metrics",
            health_checks=["aos", "service-bus"],
        )
        assert len(config.health_checks) == 2


class TestCorrelationContext:
    def test_auto_id(self):
        ctx = CorrelationContext()
        assert ctx.correlation_id is not None
        assert len(ctx.correlation_id) > 0

    def test_custom_id(self):
        ctx = CorrelationContext(correlation_id="my-id")
        assert ctx.correlation_id == "my-id"

    def test_to_dict(self):
        ctx = CorrelationContext(correlation_id="test", operation_name="op")
        d = ctx.to_dict()
        assert d["correlation_id"] == "test"
        assert d["operation_name"] == "op"
        assert "duration_ms" in d


class TestCorrelationScope:
    def test_sets_context(self):
        with correlation_scope(operation_name="test-op") as ctx:
            current = get_correlation_context()
            assert current is ctx
            assert ctx.operation_name == "test-op"

    def test_restores_context(self):
        set_correlation_context(None)
        with correlation_scope():
            pass
        assert get_correlation_context() is None


class TestStructuredLogger:
    def test_create(self):
        log = create_structured_logger("test")
        assert isinstance(log, StructuredLogger)
        assert log.name == "test"


class TestMetricsCollector:
    def test_increment(self):
        mc = MetricsCollector()
        mc.increment("requests")
        mc.increment("requests")
        assert mc.counters["requests"] == 2

    def test_gauge(self):
        mc = MetricsCollector()
        mc.set_gauge("cpu", 0.75)
        assert mc.gauges["cpu"] == 0.75

    def test_histogram(self):
        mc = MetricsCollector()
        mc.record("latency", 100.0)
        mc.record("latency", 200.0)
        snap = mc.snapshot()
        assert snap["histograms"]["latency"]["count"] == 2
        assert snap["histograms"]["latency"]["avg"] == 150.0

    def test_reset(self):
        mc = MetricsCollector()
        mc.increment("x")
        mc.reset()
        assert len(mc.counters) == 0

    def test_global_singleton(self):
        mc = get_metrics_collector()
        assert isinstance(mc, MetricsCollector)


class TestHealthCheck:
    async def test_all_healthy(self):
        hc = HealthCheck()
        async def check_ok():
            return True
        hc.register("test", check_ok)
        result = await hc.check()
        assert result["healthy"] is True

    async def test_unhealthy(self):
        hc = HealthCheck()
        async def check_fail():
            raise RuntimeError("down")
        hc.register("test", check_fail)
        result = await hc.check()
        assert result["healthy"] is False

    def test_global_singleton(self):
        hc = get_health_check()
        assert isinstance(hc, HealthCheck)
