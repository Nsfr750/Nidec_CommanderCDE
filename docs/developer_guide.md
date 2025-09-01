# Developer Guide

## Table of Contents
1. [Project Structure](#project-structure)
2. [Development Setup](#development-setup)
3. [Code Style](#code-style)
4. [Architecture Overview](#architecture-overview)
5. [Adding New Features](#adding-new-features)
6. [Testing](#testing)
7. [Debugging](#debugging)
8. [Building and Distribution](#building-and-distribution)
9. [Version Control](#version-control)
10. [Contributing Guidelines](#contributing-guidelines)

## Project Structure
```
Nidec_CommanderCDE/
├── app_struct/         # Application structure and models
├── docs/               # Documentation files
├── images/             # Application images and icons
├── lang/               # Language files and translations
├── script/             # Utility scripts
├── tests/              # Test files
├── main.py            # Main application entry point
├── menu.py            # Menu and UI setup
├── nidec_models.py    # Nidec drive models and parameters
├── requirements.txt   # Python dependencies
└── CHANGELOG.md      # Version history
```

## Development Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/Nsfr750/Nidec_CommanderCDE.git
   cd Nidec_CommanderCDE
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

## Code Style
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines
- Use type hints for all function signatures
- Document all public classes and methods with docstrings
- Keep lines under 100 characters
- Use `black` for code formatting:
  ```bash
  black .
  ```
- Use `isort` for import sorting:
  ```bash
  isort .
  ```

## Architecture Overview

### Main Components
- **Main Application (`main.py`)**
  - Entry point and main window
  - UI initialization and event handling
  - High-level application logic

- **Drive Communication**
  - Handles low-level communication with Nidec drives
  - Implements communication protocols
  - Manages connection state

- **UI Components**
  - Built with PyQt6
  - Follows MVVM pattern
  - Supports theming and styling

### Data Flow
1. User interacts with UI components
2. UI events trigger controller methods
3. Controller updates model and view
4. Drive communication happens asynchronously
5. Status updates are pushed to the UI

## Adding New Features
1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Implement your changes following the existing code style

3. Add or update tests for your changes

4. Update documentation as needed

5. Run tests and ensure they pass:
   ```bash
   pytest
   ```

6. Submit a pull request

## Testing
### Running Tests
```bash
# Run all tests
pytest

# Run a specific test file
pytest tests/test_module.py

# Run tests with coverage report
pytest --cov=.
```

### Writing Tests
- Place test files in the `tests/` directory
- Name test files with `test_` prefix
- Use descriptive test function names
- Test both success and error cases
- Mock external dependencies

## Debugging
### Common Issues
1. **Connection Problems**
   - Check COM port permissions
   - Verify baud rate settings
   - Test with a terminal program

2. **UI Freezing**
   - Move long-running tasks to separate threads
   - Use `QApplication.processEvents()` when needed

3. **Memory Leaks**
   - Use `tracemalloc` to track memory usage
   - Ensure proper cleanup of resources

### Debugging Tools
- Python debugger (`pdb`)
- Qt Creator for UI debugging
- Wireshark for protocol analysis

## Building and Distribution
### Creating a Standalone Executable
1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Build the application:
   ```bash
   pyinstaller --onefile --windowed main.py
   ```

3. The executable will be in the `dist/` directory

## Version Control
### Branching Strategy
- `main` - Stable production code
- `develop` - Integration branch for features
- `feature/*` - New features and enhancements
- `bugfix/*` - Bug fixes
- `release/*` - Release preparation

### Commit Messages
Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:
- `feat:` A new feature
- `fix:` A bug fix
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code changes that neither fix bugs nor add features
- `perf:` Performance improvements
- `test:` Adding or updating tests
- `chore:` Changes to the build process or auxiliary tools

## Contributing Guidelines
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

### Code Review Process
1. Automated checks (tests, linting)
2. Manual code review
3. Address review comments
4. Merge when approved

### Reporting Issues
When reporting issues, please include:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details
- Relevant logs or screenshots

---
*Last updated: 2025-09-01*
