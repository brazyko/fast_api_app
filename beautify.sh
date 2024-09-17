#!/bin/bash

# Beautify project's code

echo "💥 Black formatter is checking.. ⏳ "
black .
echo "Black formatter finished! 💎"

echo "💥 Flake8 in checking.. ⏳ "
flake8 .
echo "Flake8 finished! 💎"

echo "💥 MyPy is checking.. ⏳ "
mypy . --install-types
echo "MyPy finished! 💎"