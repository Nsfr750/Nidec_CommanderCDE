# Project Structure

This document outlines the structure of the Nidec CommanderCDE project.

## Directory Structure

```
Nidec_CommanderCDE/
├── .github/                    # GitHub configuration and workflows
│   ├── FUNDING.yml             # Funding information
│   └── CODEOWNERS              # Code ownership definitions
├── docs/                       # Documentation files
│   ├── developer_guide.md      # Developer documentation
│   ├── SECURITY.md             # Security policy
│   ├── STRUCTURE.md            # This file
│   ├── translation_guide.md    # Translation guidelines
│   ├── CODE_OF_CONDUCT.md      # Code of conduct
│   ├── CONTRIBUTING.md         # Contribution guidelines
│   ├── troubleshooting.md      # Troubleshooting guide
│   └── user_guide.md           # User documentation          
├── script/                     # Utility scripts
│   ├── lang/                   # Language files and translations
│   │   ├── lang_en.py          # English translations
│   │   ├── lang_it.py          # Italian translations
│   │   └── lang_manager.py     # Language management
│   ├── assets/                 # Application assets (images, icons, etc.)
|   │   ├── icon.png            # Application icon
|   │   ├── logo.png            # Application logo
|   │   └── screenshot.png      # Application screenshot
│   ├── UI/                     # UI scripts
|   │   ├── aboput.py           # About dialog
|   │   ├── help.py             # Help system
|   │   ├── sponsor.py          # Sponsor information
|   │   └── menu.py             # Menu and UI setup
│   ├── core/                   # Core scripts
|   │   └── nidec_models.py     # Nidec drive models and parameters
│   └── utils/                  # Utility scripts 
|       ├── updates.py          # Update system
|       └── version.pyl         # Version information
├── .gitignore                  # Git ignore rules
├── CHANGELOG.md                # Version history
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
