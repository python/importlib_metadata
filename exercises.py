from pytest_perf.deco import extras


@extras('perf')
def discovery_perf():
    "discovery"
    import importlib_metadata  # end warmup

    importlib_metadata.distribution('ipython')


def entry_points_perf():
    "entry_points()"
    import importlib_metadata  # end warmup

    importlib_metadata.entry_points()


@extras('perf')
def cached_distribution_perf():
    "cached distribution"
    import importlib_metadata

    importlib_metadata.distribution('ipython')  # end warmup
    importlib_metadata.distribution('ipython')


@extras('perf')
def uncached_distribution_perf():
    "uncached distribution"
    import importlib

    import importlib_metadata

    # end warmup
    importlib.invalidate_caches()
    importlib_metadata.distribution('ipython')


def entrypoint_regexp_perf():
    import re

    import importlib_metadata

    input = '0' + ' ' * 2**10 + '0'  # end warmup

    re.match(importlib_metadata.EntryPoint.pattern, input)


def normalize_perf():
    # python/cpython#143658
    import importlib_metadata  # end warmup

    # operation completes in < 1ms, so repeat it to get visibility
    # https://github.com/jaraco/pytest-perf/issues/12
    for _ in range(1000):
        importlib_metadata.Prepared.normalize('sample')
