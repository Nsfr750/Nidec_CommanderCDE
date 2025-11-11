"""
Nidec Drive Models and Parameters

This module defines the Nidec drive models, parameters, and related functionality.
It provides a standardized way to interact with different Nidec drive models.
"""

from typing import Dict, List, Optional, Any, Union
import json
from pathlib import Path

# Import language manager for translations
from script.lang.lang_manager import SimpleLanguageManager

# Initialize language manager
language_manager = SimpleLanguageManager()

def t(key: str, language: str = 'en', default: Optional[str] = None) -> str:
    """Translation helper function for backward compatibility.
    
    Args:
        key: Translation key
        language: Language code (default: 'en')
        default: Default value if key is not found
        
    Returns:
        str: Translated string or default value
    """
    return language_manager.tr(key, default=default or key, lang_code=language)

# Supported Nidec drive models
SUPPORTED_MODELS = [
    'CDE400', 'CDE550', 'CDE750', 'CDE1100S'
]

# Fault codes and their descriptions
FAULT_CODES = {
    '00': 'No fault',
    '01': 'Overcurrent',
    '02': 'DC bus overvoltage',
    '03': 'DC bus undervoltage',
    '04': 'Drive overtemperature',
    '05': 'Motor overload',
    '06': 'Hardware failure',
    # Add more fault codes as needed
}

# Default parameter values for each model
DEFAULT_PARAMETERS = {
    'CDE400': {
        'max_frequency': 400.0,  # Hz
        'max_current': 1.5,      # A
        'max_voltage': 230,      # V
        'default_baudrate': 9600,
        'parameters': {
            'P001': {'name': 'Run Command', 'min': 0, 'max': 1, 'default': 0, 'unit': '', 'readonly': False},
            'P002': {'name': 'Frequency Reference', 'min': 0, 'max': 400, 'default': 0, 'unit': 'Hz', 'readonly': False},
            # Add more parameters as needed
        }
    },
    # Add other models with their respective parameters
}

def get_model_list() -> List[Dict[str, str]]:
    """Get a list of supported drive models with their display names.
    
    Returns:
        List[Dict[str, str]]: List of dictionaries with 'code' and 'name' keys
    """
    return [
        {'code': model, 'name': f"Nidec {model}"} 
        for model in SUPPORTED_MODELS
    ]

def get_model_config(model: str, language: str = 'en') -> Dict[str, Any]:
    """Get configuration for a specific drive model.
    
    Args:
        model: Model code (e.g., 'CDE400')
        language: Language code for translations
        
    Returns:
        Dict: Model configuration including parameters
    """
    if model not in SUPPORTED_MODELS:
        raise ValueError(f"Unsupported model: {model}")
    
    # Get the base configuration
    config = DEFAULT_PARAMETERS.get(model, {})
    
    # Translate parameter names and units if translations are available
    if 'parameters' in config:
        for param_id, param in config['parameters'].items():
            # Translate parameter name
            param_key = f'param_{param_id}_name'
            param['name'] = t(param_key, language, default=param['name'])
            
            # Translate unit if it exists
            if 'unit' in param and param['unit']:
                unit_key = f'unit_{param["unit"].lower()}'
                param['unit'] = t(unit_key, language, default=param['unit'])
    
    return config

def get_fault_description(fault_code: Union[int, str], language: str = 'en') -> str:
    """Get a human-readable description of a fault code.
    
    Args:
        fault_code: The fault code to look up
        language: Language code for the description
        
    Returns:
        str: Human-readable fault description
    """
    fault_code = str(fault_code).zfill(2)  # Ensure 2-digit format
    
    # Use the FAULT_CODES dictionary but translate the descriptions
    fault_descriptions = {
        code: t(f'fault_{code}', language, description)
        for code, description in FAULT_CODES.items()
    }
    
    return fault_descriptions.get(fault_code, t('fault_unknown', language, f'Unknown fault ({fault_code})'))

class NidecDrive:
    """Class representing a Nidec drive."""
    
    def __init__(self, model: str = 'CDE400', address: int = 1):
        """Initialize a new Nidec drive instance.
        
        Args:
            model: Drive model (e.g., 'CDE400')
            address: Modbus address (1-247)
        """
        if model not in SUPPORTED_MODELS:
            raise ValueError(f"Unsupported model: {model}")
        
        self.model = model
        self.address = address
        self.connected = False
        self.config = get_model_config(model)
        self.parameters = {}
        
        # Initialize parameters with default values
        self.reset_parameters()
    
    def reset_parameters(self):
        """Reset all parameters to their default values."""
        self.parameters = {}
        if 'parameters' in self.config:
            for param_id, param in self.config['parameters'].items():
                self.parameters[param_id] = param.get('default', 0)
    
    def get_parameter(self, param_id: str) -> Optional[float]:
        """Get the current value of a parameter.
        
        Args:
            param_id: Parameter ID (e.g., 'P001')
            
        Returns:
            Optional[float]: Parameter value, or None if not found
        """
        return self.parameters.get(param_id)
    
    def set_parameter(self, param_id: str, value: float) -> bool:
        """Set the value of a parameter.
        
        Args:
            param_id: Parameter ID (e.g., 'P001')
            value: New parameter value
            
        Returns:
            bool: True if successful, False otherwise
        """
        if param_id not in self.parameters:
            return False
            
        # Validate value against min/max if defined
        param_config = self.config.get('parameters', {}).get(param_id, {})
        if 'min' in param_config and value < param_config['min']:
            return False
        if 'max' in param_config and value > param_config['max']:
            return False
        
        self.parameters[param_id] = value
        return True
    
    def connect(self) -> bool:
        """Connect to the drive.
        
        Returns:
            bool: True if connected successfully, False otherwise
        """
        # Implementation would go here
        self.connected = True
        return True
    
    def disconnect(self):
        """Disconnect from the drive."""
        self.connected = False
    
    def read_parameters(self) -> bool:
        """Read all parameters from the drive.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connected:
            return False
        
        # Implementation would go here
        # For now, just return the current values
        return True
    
    def write_parameters(self) -> bool:
        """Write all parameters to the drive.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connected:
            return False
        
        # Implementation would go here
        return True
