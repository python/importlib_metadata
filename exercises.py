from pytest_perf.deco import extras, deps, control


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


@deps('flake8', 'pytest', 'twine', 'pre-commit')
@control('v1.4.0')
def entry_points_selected_perf():
    import importlib_metadata  # end warmup

    eps = importlib_metadata.entry_points()

    try:
        eps.select(group="flake8.extension")
        eps.select(group="flake8.report")
    except AttributeError:
        eps["flake8.extension"]
        eps["flake8.report"]
