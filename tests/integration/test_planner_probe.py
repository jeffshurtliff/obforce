# -*- coding: utf-8 -*-
"""
:Module:            tests.integration.test_planner_probe
:Synopsis:          Exercises the shared installed planner acceptance probe offline
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     20 Oct 2026
"""

import runpy
import sys
from pathlib import Path


def test_planner_acceptance_probe_uses_no_cwd_artifacts(tmp_path, monkeypatch):
    """Keep synthetic setup separate from cwd and enforce the installed probe guard."""
    probe = Path(__file__).resolve().parents[2] / 'dev/probe_planner.py'
    monkeypatch.chdir(tmp_path)
    active = [True]

    def guarded(event, args):
        if active[0] and (event.startswith('socket.') or event in {'subprocess.Popen', 'os.system', 'os.posix_spawn'}):
            raise RuntimeError('Runtime network/process forbidden')

    sys.addaudithook(guarded)
    try:
        runpy.run_path(str(probe), run_name='__main__')
        assert list(tmp_path.iterdir()) == []
    finally:
        active[0] = False
