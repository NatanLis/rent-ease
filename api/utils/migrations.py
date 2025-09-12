import os
import subprocess
import sys


def run_migrations():
    """
    Run Alembic database migrations using Python's module execution.

    This approach is compatible with cloud environments (e.g. Vercel) where direct shell commands may be restricted.
    On success, prints migration output and completion message. On failure, prints error details.
    """
    try:
        # Add current directory to Python path to ensure Alembic can find config
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)

        # Run Alembic migrations using Python interpreter
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True,
        )

        # Print migration output if available
        if result.stdout:
            print("Migration output:", result.stdout)

        print("Migrations completed successfully!")

    except subprocess.CalledProcessError as e:
        print(f"Migration failed. Error: {e}")
        print("Standard output:", e.stdout)
        print("Standard error:", e.stderr)
        raise
    except Exception as e:
        print(f"An error occurred while running migrations: {e}")
        raise
