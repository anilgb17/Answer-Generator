"""Setup utilities for creating necessary directories."""
import os
from pathlib import Path
from config.settings import settings


def create_directories():
    """Create all necessary directories for the application."""
    directories = [
        settings.upload_dir,
        settings.output_dir,
        Path(settings.log_file).parent,
        settings.vector_db_path,
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")


if __name__ == "__main__":
    create_directories()
