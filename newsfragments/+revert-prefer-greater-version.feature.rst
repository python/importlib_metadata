Reverted the preference for the greater metadata directory added in v9.1.0.
The ordering was lexicographic on the directory name and not on the parsed
version, so it only approximated a preference for the newer version. Where a
path supplies more than one metadata directory for a distribution, discovery
once again reports them in the order the path supplies
(python/cpython#100666).
