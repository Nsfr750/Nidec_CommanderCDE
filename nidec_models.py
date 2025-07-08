"""
Nidec Commander CDE Series Models Configuration

This module provides configuration and utility functions for different Nidec CDE Series
motor drive models. It includes register mappings, model specifications, and helper
functions for retrieving model information and fault descriptions.

Key Features:
- Centralized model configurations for different drive models
- Register address mappings for Modbus communication
- Fault code descriptions with multi-language support
- Model-specific parameter limits and specifications

Dependencies:
- lang.translations: For internationalization support

Author: [Your Name]
Version: 1.0.0
"""

from typing import Dict, List, Optional, Any
from lang.translations import t

# Model specifications and register mappings
# This dictionary contains the complete configuration for all supported Nidec CDE drive models.
# Each model includes specifications, register addresses, and default parameter values.
MODEL_CONFIG: Dict[str, Dict[str, Any]] = {
    "CDE400": {
        "max_frequency": 400.0,  # Hz
        "max_current": 8.0,      # A
        "power_rating": 0.4,     # kW
        "voltage_rating": 400.0, # V
        "registers": {
            "frequency_reference": 0x1000,
            "run_command": 0x2000,
            "direction_control": 0x2001,
            "output_frequency": 0x2002,
            "output_current": 0x2003,
            "dc_bus_voltage": 0x2004,
            "status_register": 0x2005,
            "fault_register": 0x2006,
            "accel_time": 0x3000,
            "decel_time": 0x3001,
            "motor_rated_current": 0x3002,
            "max_frequency_reg": 0x3003,
            "motor_rated_voltage": 0x3004
        }
    },
    "CDE550": {
        "max_frequency": 50.0, #Hz
        "max_current": 10, #A
        "power_rating": 5.5, #KW
        "voltage_rating": 400.0, #V
        "registers": {
            "frequency_reference": 0x1000,
            "run_command": 0x2000,
            "direction_control": 0x2001,
            "output_frequency": 0x2002,
            "output_current": 0x2003,
            "dc_bus_voltage": 0x2004,
            "status_register": 0x2005,
            "fault_register": 0x2006,
            "accel_time": 0x3000,
            "decel_time": 0x3001,
            "motor_rated_current": 0x3002,
            "max_frequency_reg": 0x3003,
            "motor_rated_voltage": 0x3004
        }
    },
    "CDE750": {
        "max_frequency": 750.0, #Hz
        "max_current": 15.0, #A
        "power_rating": 0.75, #Kw
        "voltage_rating": 400.0, #V
        "registers": {
            "frequency_reference": 0x1000,
            "run_command": 0x2000,
            "direction_control": 0x2001,
            "output_frequency": 0x2002,
            "output_current": 0x2003,
            "dc_bus_voltage": 0x2004,
            "status_register": 0x2005,
            "fault_register": 0x2006,
            "accel_time": 0x3000,
            "decel_time": 0x3001,
            "motor_rated_current": 0x3002,
            "max_frequency_reg": 0x3003,
            "motor_rated_voltage": 0x3004
        }
    },
    "CDE1100S": {
        "max_frequency": 1100.0, #Hz
        "max_current": 22.0, #A
        "power_rating": 1.1, #Kw
        "voltage_rating": 400.0, #V
        "registers": {
            "frequency_reference": 0x1000,
            "run_command": 0x2000,
            "direction_control": 0x2001,
            "output_frequency": 0x2002,
            "output_current": 0x2003,
            "dc_bus_voltage": 0x2004,
            "status_register": 0x2005,
            "fault_register": 0x2006,
            "accel_time": 0x3000,
            "decel_time": 0x3001,
            "motor_rated_current": 0x3002,
            "max_frequency_reg": 0x3003,
            "motor_rated_voltage": 0x3004
        }
    }
}

# Fault code definitions with translations
# This dictionary maps fault codes to their descriptions in multiple languages.
# Each fault code includes a unique identifier and a translation key.
FAULT_CODES: Dict[int, str] = {
    0x0000: 'no_fault',
    0x0001: 'overcurrent',
    0x0002: 'overvoltage',
    0x0003: 'undervoltage',
    0x0004: 'inverter_overheat',
    0x0005: 'motor_overload',
    0x0006: 'input_phase_loss',
    0x0007: 'output_phase_loss',
    0x0008: 'external_fault',
    0x0009: 'eeprom_error',
    0x000A: 'cpu_error',
    0x000B: 'overload',
    0x000C: 'braking_resistor_overload',
    0x000D: 'motor_stall_prevention',
    0x000E: 'communication_error'
}

def get_fault_description(fault_code: int, language: str = 'en') -> str:
    """Get the translated description for a fault code.
    
    This function looks up the provided fault code in the FAULT_CODES dictionary
    and returns the corresponding translated description. If the fault code is not
    found, it returns a default 'unknown fault' message.
    
    Args:
        fault_code: Integer value representing the fault code
        language: Two-letter language code (e.g., 'en', 'it'). Defaults to 'en'.
        
    Returns:
        str: The translated fault description in the specified language.
        
    Example:
        >>> get_fault_description(1, 'en')
        'Overcurrent'
        >>> get_fault_description(1, 'it')
        'Sovracorrente'
    """
    if fault_code in FAULT_CODES:
        return t(FAULT_CODES[fault_code], language)
    return t('unknown_fault', language, default='Unknown Fault')

def get_model_list(language: str = 'en') -> List[str]:
    """Return list of available drive models with translated names.
    
    This function generates a list of all supported drive models with their
    identifiers and display names in the specified language.
    
    Args:
        language: Two-letter language code (e.g., 'en', 'it'). Defaults to 'en'.
        
    Returns:
        List[str]: A list of model names
    """
    return [
        'CDE400', 'CDE550', 'CDE750', 'CDE1100S'
    ]

def get_model_display_name(model: str, language: str = 'en') -> str:
    """Get the display name for a model
    
    Args:
        model: Model identifier (e.g., 'CDE400')
        language: Language code (default: 'en')
        
    Returns:
        str: Translated model name
    """
    return model  # Models don't need translation as they are product codes

def get_model_config(model: str, language: str = 'en') -> Dict[str, Any]:
    """Get complete configuration for a specific drive model.
    
    This function retrieves the configuration for a specified model and localizes
    all translatable strings to the requested language. The configuration includes
    specifications, register mappings, and parameter definitions.
    
    Args:
        model: The model identifier (e.g., 'CDE400')
        language: Two-letter language code (e.g., 'en', 'it'). Defaults to 'en'.
        
    Returns:
        Dict[str, Any]: A dictionary containing the complete model configuration
            with all strings localized to the specified language.
            
    Raises:
        ValueError: If the specified model is not found in the configuration.
        
    Example:
        >>> config = get_model_config('CDE400', 'en')
        >>> config['name']
        'CDE Series 400W'
        >>> config['max_frequency']
        400.0
    """
    if model not in MODEL_CONFIG:
        raise ValueError(f"Unknown model: {model}")
    
    # Create a deep copy to avoid modifying the original config
    config = MODEL_CONFIG[model].copy()
    
    # Add translated model name and description
    config['name'] = get_model_display_name(model, language)
    config['description'] = t(f'model_{model}_description', language)
    
    # Translate parameter names and descriptions if they exist
    if 'parameters' in config:
        for param in config['parameters'].values():
            if 'name_key' in param:
                param['name'] = t(param['name_key'], language)
            if 'description_key' in param:
                param['description'] = t(param['description_key'], language)
                
    # Translate register names in the config
    if 'registers' in config:
        translated_registers = {}
        for reg_name, reg_addr in config['registers'].items():
            # Convert register name to translation key (snake_case)
            trans_key = reg_name.lower().replace(' ', '_')
            # Get translation or fall back to original name
            translated_name = t(trans_key, language, default=reg_name)
            translated_registers[translated_name] = reg_addr
        config['registers'] = translated_registers
    
    return config
