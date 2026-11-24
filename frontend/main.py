from pathlib import Path
import sys

# Allow frontend/main.py to import backend/database.py from the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.app import App

if __name__ == "__main__":
    app = App()
    app.mainloop()
