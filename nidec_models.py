"""
Nidec Commander CDE Series Models Configuration
"""

from lang.translations import t

# Model specifications and register mappings
MODEL_CONFIG = {
    "CDE400": {
        "max_frequency": 400.0,  # Hz
        "max_current": 8.0,      # A
        "power_rating": 0.4,     # kW
        "voltage_rating": 230.0, # V
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
        "max_frequency": 550.0,
        "max_current": 10.0,
        "power_rating": 0.55,
        "voltage_rating": 230.0,
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
        "max_frequency": 750.0,
        "max_current": 15.0,
        "power_rating": 0.75,
        "voltage_rating": 400.0,
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
        "max_frequency": 1100.0,
        "max_current": 22.0,
        "power_rating": 1.1,
        "voltage_rating": 400.0,
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

# Fault code descriptions
FAULT_CODES = {
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

def get_fault_description(fault_code, language='en'):
    """Get the translated description for a fault code.
    
    Args:
        fault_code: The fault code value
        language: Language code (default: 'en')
        
    Returns:
        str: The translated fault description
    """
    if fault_code in FAULT_CODES:
        return t(FAULT_CODES[fault_code], language)
    return t('unknown_fault', language, default='Unknown Fault')

def get_model_list(language='en'):
    """Return list of available drive models with translated names
    
    Args:
        language: Language code (default: 'en')
        
    Returns:
        list: List of model names
    """
    return [
        'CDE400', 'CDE550', 'CDE750', 'CDE1100S'
    ]
    
def get_model_display_name(model, language='en'):
    """Get the display name for a model
    
    Args:
        model: Model identifier (e.g., 'CDE400')
        language: Language code (default: 'en')
        
    Returns:
        str: Translated model name
    """
    return model  # Models don't need translation as they are product codes

def get_model_config(model, language='en'):
    """Get configuration for a specific model
    
    Args:
        model: Model identifier (e.g., 'CDE400')
        language: Language code (default: 'en')
        
    Returns:
        dict: Model configuration with translated strings
    """
    config = MODEL_CONFIG.get(model, MODEL_CONFIG["CDE400"]).copy()
    
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
