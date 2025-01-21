from .database import create_table, fetch_inventory, insert_part_numbers, search
from .inventory import Inventory, Part, export_to_excel, search_part_numbers, show_all

# Initialize the database and perform initial setup
create_table()
search_part_numbers()

# __init__.py

# This file indicates that the directory is a Python package.
# You can use this file to initialize the package and import necessary modules.

# Example of importing a module within the package

# You can also define package-level variables or functions here
__version__ = "1.0.0"


def get_version():
    return __version__
