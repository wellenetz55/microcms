"""One-shot, private Cron verification; never writes the production web root."""
import contextlib
import datetime
import json
import os
from pathlib import Path
import ssl
import sys
import unittest

import pull
import test_pull


def main():
    os.umask(0o077)
    folder = Path(__file__).resolve().parent
    if (folder / 'verification.done').exists():
        return
    with (folder / 'verification.log').open('w') as log, contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
        print('Server verification UTC: ' + datetime.datetime.utcnow().isoformat())
        print('Python: ' + sys.version.split()[0])
        print('TLS: ' + ssl.OPENSSL_VERSION)
        suite = unittest.defaultTestLoader.loadTestsFromModule(test_pull)
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
        if result.wasSuccessful():
            config = json.loads((folder / 'config.json').read_text())
            try:
                pull.run(config, apply=False)
                print('SERVER VERIFICATION PASSED; production files unchanged')
            except Exception as exc:
                print('HTTPS verification failed: ' + type(exc).__name__)
        else:
            print('Server compatibility tests failed; production files unchanged')
    (folder / 'verification.done').write_text('One-shot verification finished. See verification.log.\n')


if __name__ == '__main__':
    main()
