Where a path supplies more than one metadata directory for a distribution,
as an interrupted or unclean upgrade may leave behind, discovery now prefers
the greater one by reverse lexicographic ordering of the directory names, so
the stale metadata no longer shadows the version in use
(python/cpython#100666).
