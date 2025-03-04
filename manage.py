import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kennel_admin.settings')  # Убедись, что тут правильное имя проекта

import django
django.setup()  # 👈 Добавь эту строку перед импортами Django моделей

from django.core.management import execute_from_command_line

def main():
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
