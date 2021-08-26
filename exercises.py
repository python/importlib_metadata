from pytest_perf.deco import extras


@extras('perf')  # type: ignore[misc]
def discovery_perf() -> None:
    "discovery"
    import importlib_metadata  # end warmup

    importlib_metadata.distribution('ipython')


def entry_points_perf() -> None:
    "entry_points()"
    import importlib_metadata  # end warmup

    importlib_metadata.entry_points()


@extras('perf')  # type: ignore[misc]
def cached_distribution_perf() -> None:
    "cached distribution"
    import importlib_metadata

    importlib_metadata.distribution('ipython')  # end warmup
    importlib_metadata.distribution('ipython')


@extras('perf')  # type: ignore[misc]
def uncached_distribution_perf() -> None:
    "uncached distribution"
    import importlib
    import importlib_metadata

    # end warmup
    importlib.invalidate_caches()
    importlib_metadata.distribution('ipython')
