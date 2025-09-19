#!/usr/bin/env python
"""Test the live bot with detailed logging"""
import asyncio
import logging
import sys

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Import and run main
from main import main

if __name__ == "__main__":
    asyncio.run(main(["--youtube"]))