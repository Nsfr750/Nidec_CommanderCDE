# Project Structure

This document outlines the structure of the Nidec CommanderCDE project.

## Directory Structure

```text
Nidec_CommanderCDE/
├── .github/                    # GitHub configuration and workflows
│   ├── FUNDING.yml             # Funding information
│   └── CODEOWNERS              # Code ownership definitions
├── docs/                       # Documentation files
│   ├── CODE_OF_CONDUCT.md      # Code of conduct
│   ├── CONTRIBUTING.md         # Contribution guidelines
│   ├── developer_guide.md      # Developer documentation
│   ├── README.md 
│   ├── SECURITY.md             # Security policy
│   ├── STRUCTURE.md            # This file
│   ├── troubleshooting.md      # Troubleshooting guide
│   └── user_guide.md           # User documentation          
├── script/                     # Utility scripts
│   ├── assets/                 # Application assets (images, icons, etc.)
|   │   ├── __init__.py         # Assets initialization
|   │   ├── about.png           # About Img
|   │   ├── icon.ico            # Application icon
|   │   ├── logo.png            # Application logo
|   │   ├── screenshot.png      # Application screenshot
|   │   └── version_info.txt    # Version information
│   ├── core/                   # Core scripts
|   │   ├── __init__.py         # Core initialization
|   │   └── nidec_models.py     # Nidec drive models and parameters
│   ├── lang/                   # Language files and translations
|   │   ├── __init__.py         # Language initialization
│   │   ├── lang_en.py          # English translations
│   │   ├── lang_it.py          # Italian translations
│   │   └── lang_manager.py     # Language management
│   ├── UI/                     # UI scripts
|   │   ├── __init__.py         # UI initialization
|   │   ├── aboput.py           # About dialog
|   │   ├── help.py             # Help system
|   │   ├── menu.py             # Menu and UI setup
|   │   ├── serial_dialog.py    # Serial port configuration dialog
|   │   ├── simulator.py        # Simulator dialog
|   │   └── sponsor.py          # Sponsor information
│   ├── utils/                  # Utility scripts 
|   │   ├── __init__.py         # Utils initialization
|   │   ├── inverter_sim.py     # Inverter simulator
|   │   ├── serial_handler.py   # Serial port handler
|   │   ├── updates.py          # Update system
|   │   └── version.py          # Version information
|   └── __init__.py             # Script initialization
├── .gitattributes              # Git attributes
├── .gitignore                  # Git ignore rules
├── CHANGELOG.md                # Version history
├── LICENSE                     # Project license
├── main.py                     # Main application entry point
├── README.md                   # Project README
└── requirements.txt            # Python dependencies
```

## Key Files

- `main.py`: The main entry point of the application
- `menu.py`: Handles the main menu and UI setup
- `nidec_models.py`: Contains the Nidec drive models and parameter definitions
- `lang/`: Contains all language-related files and translations
- `script/`: Contains various utility scripts and dialogs
- `docs/`: Contains all project documentation

## Dependencies

All Python dependencies are listed in `requirements.txt`. To install them:

```bash
pip install -r requirements.txt
```

## Building and Distribution

To create a standalone executable:

```bash
pyinstaller --onefile --windowed main.py
```

## Version Information

Current version: 0.0.5

## License

This project is licensed under the GPLv3 License - see the [LICENSE](../LICENSE) file for details.
