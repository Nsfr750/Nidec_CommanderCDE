"""
Nidec Commander CDE Series Models Configuration
"""

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
    0x0000: "No Fault",
    0x0001: "Overcurrent",
    0x0002: "Overvoltage",
    0x0003: "Undervoltage",
    0x0004: "Inverter Overheat",
    0x0005: "Motor Overload",
    0x0006: "Input Phase Loss",
    0x0007: "Output Phase Loss",
    0x0008: "External Fault",
    0x0009: "EEPROM Error",
    0x000A: "CPU Error",
    0x000B: "Overload",
    0x000C: "Braking Resistor Overload",
    0x000D: "Motor Stall Prevention",
    0x000E: "Communication Error"
}

def get_model_list():
    """Return list of available drive models"""
    return list(MODEL_CONFIG.keys())

def get_model_config(model):
    """Get configuration for a specific model"""
    return MODEL_CONFIG.get(model, MODEL_CONFIG["CDE400"])
