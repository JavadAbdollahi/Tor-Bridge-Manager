# main.py
# Entry point for the Tor Bridge Manager (single connection)

import sys
from app import App

if __name__ == "__main__":
    try:
        App().run()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit()