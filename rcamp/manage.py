#!/usr/bin/env python3
import os
import sys
import django

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rcamp.settings")

    from django.core.management import execute_from_command_line
    
    print("Django version:", django.get_version()) 

    execute_from_command_line(sys.argv)
