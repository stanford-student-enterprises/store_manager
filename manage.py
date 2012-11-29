#!/usr/bin/env python
import os, sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "store_manager.settings")
    sys.path.append(os.path.join(os.path.dirname(__file__), "store_manager"))
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
