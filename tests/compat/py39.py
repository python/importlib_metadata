from jaraco.test.cpython import from_test_support, try_import


os_helper = try_import('os_helper') or from_test_support(
    'FS_NONASCII', 'skip_unless_symlink'
)
import_helper = try_import('import_helper') or from_test_support(
    'modules_setup', 'modules_cleanup'
)
