"""
Feature Engineering Module for Nuclear Power Plant AI Models
Transforms reactor parameters into the 288 features expected by the trained models.

This module handles:
- Mapping reactor parameters to base features
- Rolling mean calculations (window=3)
- Difference calculations (current - previous)
- Feature validation and preprocessing
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ReactorState:
    """
    Represents the current state of reactor parameters.
    Based on the feature names from the training data.
    Note: TIME is not included as it's not used in the model training (96 base features only).
    """
    # Temperature parameters
    TAVG: float = 300.0  # Average RCS temperature
    THA: float = 320.0   # Hot leg temperature A
    THB: float = 320.0   # Hot leg temperature B
    TCA: float = 280.0   # Cold leg temperature A
    TCB: float = 280.0   # Cold leg temperature B
    TSAT: float = 350.0  # Pressurizer saturation temperature
    TRB: float = 25.0    # Reactor building temperature
    TFPK: float = 400.0  # Peak fuel temperature
    TFSB: float = 380.0  # Submerged fuel temperature
    TF: float = 390.0    # Average fuel temperature
    TPCT: float = 350.0  # Peak cladding temperature
    
    # Pressure parameters
    P: float = 155.0     # RCS pressure (bar)
    PSGA: float = 70.0   # Steam generator A pressure
    PSGB: float = 70.0   # Steam generator B pressure
    LVPZ: float = 50.0   # Pressurizer level
    PRB: float = 1.0     # Reactor building pressure
    PRBA: float = 0.8    # Reactor building air partial pressure
    
    # Flow parameters
    WRCA: float = 1000.0  # RCS flow A
    WRCB: float = 1000.0  # RCS flow B
    WFWA: float = 500.0   # Feedwater flow A
    WFWB: float = 500.0   # Feedwater flow B
    WSTA: float = 500.0   # Steam flow A
    WSTB: float = 500.0   # Steam flow B
    WLR: float = 0.0      # RCS leakage
    WUP: float = 0.0      # Pressurizer makeup
    WHPI: float = 0.0     # High pressure injection
    WECS: float = 0.0     # Emergency core cooling
    WTRA: float = 0.0     # Tube rupture A
    WTRB: float = 0.0     # Tube rupture B
    WCFT: float = 0.0     # Core flood tank
    WLPI: float = 0.0     # Low pressure injection
    WCHG: float = 50.0    # Charging flow
    WRLA: float = 0.0     # Relief valve A
    WRLB: float = 0.0     # Relief valve B
    WLD: float = 0.0      # Letdown flow
    WSPY: float = 0.0     # Pressurizer spray
    WCSP: float = 0.0     # Containment spray
    WBK: float = 0.0      # Break flow
    WFLB: float = 0.0     # Feedwater line break
    
    # Level parameters
    LVCR: float = 100.0   # Core water level
    LSGA: float = 50.0    # Steam generator A level (wide range)
    LSGB: float = 50.0    # Steam generator B level (wide range)
    NSGA: float = 50.0    # Steam generator A level (narrow range)
    NSGB: float = 50.0    # Steam generator B level (narrow range)
    LWRB: float = 0.0     # Reactor building water level
    
    # Volume parameters
    VOL: float = 300.0    # RCS liquid volume
    VOID: float = 10.0    # RCS void volume
    TKLV: float = 1000.0  # RWST volume
    
    # Power parameters
    QMWT: float = 100.0   # Reactor thermal power (%)
    QMGA: float = 50.0    # Steam generator A heat removal
    QMGB: float = 50.0    # Steam generator B heat removal
    QRHR: float = 0.0     # Residual heat removal
    QFCL: float = 0.0     # Fan cooler power
    PWR: float = 100.0    # Core thermal power
    PWNT: float = 100.0   # Neutron power
    
    # Reactivity parameters
    RHBR: float = 0.0     # Boron reactivity
    RHMT: float = 0.0     # Moderator temperature reactivity
    RHFL: float = 0.0     # Fuel temperature reactivity
    RHRD: float = 0.0     # Rod reactivity
    RH: float = 0.0       # Total reactivity
    
    # Radiation parameters
    RM1: float = 1.0      # Radiation monitor 1
    RM2: float = 1.0      # Radiation monitor 2
    RM3: float = 1.0      # Radiation monitor 3
    RM4: float = 1.0      # Radiation monitor 4
    RC87: float = 1.0     # RCS activity
    RC131: float = 1.0    # I-131 concentration
    CNH2: float = 0.1     # Hydrogen concentration
    
    # Other parameters
    TBLD: float = 100.0   # Turbine load
    HUP: float = 1000.0   # Pressurizer enthalpy
    HLW: float = 1000.0   # Leakage enthalpy
    HTR: float = 0.0      # Pressurizer heater power
    SCMA: float = 100.0   # Subcooling margin A
    SCMB: float = 100.0   # Subcooling margin B
    FRCL: float = 0.0     # Cladding failure fraction
    DNBR: float = 2.0     # DNB ratio
    MH2: float = 0.0      # Hydrogen mass
    MBK: float = 0.0      # Integrated break flow
    EBK: float = 0.0      # Integrated break energy
    FRZR: float = 0.0     # Zr oxidation fraction
    MDBR: float = 0.0     # Debris mass
    MCRT: float = 0.0     # Molten concrete mass
    MGAS: float = 0.0     # CCI gas mass
    TDBR: float = 0.0     # Debris temperature
    TSLP: float = 0.0     # Lower plenum temperature
    TCRT: float = 0.0     # Molten concrete temperature
    PPM: float = 1000.0   # Boron concentration
    RRCA: float = 1.0     # Flow ratio A
    RRCB: float = 1.0     # Flow ratio B
    RRCO: float = 1.0     # Core flow ratio
    STRB: float = 0.0     # RB release rate
    STSG: float = 0.0     # SG release rate
    STTB: float = 0.0     # Turbine release rate
    RBLK: float = 0.0     # RB leak mass
    SGLK: float = 0.0     # SG leak mass
    DTHY: float = 0.0     # Thyroid dose
    DWB: float = 0.0      # Whole body dose


class FeatureEngineer:
    """
    Handles feature engineering for nuclear power plant AI models.
    Transforms reactor parameters into the 288 features expected by the models.
    """
    
    def __init__(self, rolling_window: int = 3):
        """
        Initialize the feature engineer.
        
        Args:
            rolling_window: Window size for rolling mean calculations
        """
        self.rolling_window = rolling_window
        self.history: List[ReactorState] = []
        
        # Define the base feature names in the order expected by the model (96 features)
        self.base_features = [
            "TAVG", "THA", "THB", "TCA", "TCB", "WRCA", "WRCB", "PSGA", "PSGB",
            "WFWA", "WFWB", "WSTA", "WSTB", "VOL", "LVPZ", "VOID", "WLR", "WUP", "HUP",
            "HLW", "WHPI", "WECS", "QMWT", "LSGA", "LSGB", "QMGA", "QMGB", "NSGA", "NSGB",
            "TBLD", "WTRA", "WTRB", "TSAT", "QRHR", "LVCR", "SCMA", "SCMB", "FRCL", "PRB",
            "PRBA", "TRB", "LWRB", "DNBR", "QFCL", "WBK", "WSPY", "WCSP", "HTR", "MH2",
            "CNH2", "RHBR", "RHMT", "RHFL", "RHRD", "RH", "PWNT", "PWR", "TFSB", "TFPK",
            "TF", "TPCT", "WCFT", "WLPI", "WCHG", "RM1", "RM2", "RM3", "RM4", "RC87",
            "RC131", "STRB", "STSG", "STTB", "RBLK", "SGLK", "DTHY", "DWB", "P", "WRLA",
            "WRLB", "WLD", "MBK", "EBK", "TKLV", "FRZR", "MDBR", "MCRT", "MGAS", "TDBR",
            "TSLP", "TCRT", "PPM", "RRCA", "RRCB", "RRCO", "WFLB"
        ]
        
        logger.info(f"FeatureEngineer initialized with {len(self.base_features)} base features")
    
    def add_state(self, state: ReactorState) -> None:
        """
        Add a new reactor state to the history.
        
        Args:
            state: Current reactor state
        """
        self.history.append(state)
        
        # Keep only the last few states for rolling calculations
        max_history = max(10, self.rolling_window * 2)
        if len(self.history) > max_history:
            self.history = self.history[-max_history:]
    
    def create_features(self, state: ReactorState) -> List[float]:
        """
        Create the 288 features expected by the AI models.
        
        Args:
            state: Current reactor state
            
        Returns:
            List of 288 features (96 base + 96 rolling mean + 96 diff)
        """
        # Add current state to history
        self.add_state(state)
        
        # Extract base features
        base_values = []
        for feature_name in self.base_features:
            value = getattr(state, feature_name, 0.0)
            base_values.append(float(value))
        
        # Create DataFrame for easier manipulation
        df = pd.DataFrame([base_values], columns=self.base_features)
        
        # Add rolling mean features
        rolling_features = []
        for feature_name in self.base_features:
            # Calculate rolling mean using history
            if len(self.history) >= self.rolling_window:
                recent_values = [getattr(s, feature_name, 0.0) for s in self.history[-self.rolling_window:]]
                rolling_mean = np.mean(recent_values)
            else:
                # Not enough history, use current value
                rolling_mean = getattr(state, feature_name, 0.0)
            rolling_features.append(float(rolling_mean))
        
        # Add difference features
        diff_features = []
        for feature_name in self.base_features:
            if len(self.history) >= 2:
                # Calculate difference from previous state
                current_val = getattr(self.history[-1], feature_name, 0.0)
                previous_val = getattr(self.history[-2], feature_name, 0.0)
                diff = current_val - previous_val
            else:
                # No previous state, difference is 0
                diff = 0.0
            diff_features.append(float(diff))
        
        # Combine all features: base + rolling_mean + diff = 96 + 96 + 96 = 288
        all_features = base_values + rolling_features + diff_features
        
        logger.debug(f"Created {len(all_features)} features from reactor state")
        return all_features
    
    def validate_features(self, features: List[float]) -> bool:
        """
        Validate that features are within reasonable bounds.
        
        Args:
            features: List of feature values
            
        Returns:
            True if features are valid, False otherwise
        """
        if len(features) != 288:
            logger.error(f"Expected 288 features, got {len(features)}")
            return False
        
        for i, value in enumerate(features):
            if not isinstance(value, (int, float)):
                logger.error(f"Feature {i} is not numeric: {value}")
                return False
            
            if not np.isfinite(value):
                logger.error(f"Feature {i} is not finite: {value}")
                return False
            
            # Check for reasonable bounds
            if abs(value) > 1e10:
                logger.warning(f"Feature {i} has extreme value: {value}")
        
        return True
    
    def from_dict(self, params: Dict[str, Any]) -> ReactorState:
        """
        Create a ReactorState from a dictionary of parameters.
        Maps common parameter names to the expected feature names.
        
        Args:
            params: Dictionary of reactor parameters
            
        Returns:
            ReactorState object
        """
        # Create default state
        state = ReactorState()
        
        # Parameter mapping for common names
        param_mapping = {
            # Time
            'time': 'TIME',
            'timeSeconds': 'TIME',
            
            # Temperature mappings
            'averageRcsTemperature': 'TAVG',
            'hotLegTemperatureA': 'THA',
            'hotLegTemperatureB': 'THB',
            'coldLegTemperatureA': 'TCA',
            'coldLegTemperatureB': 'TCB',
            'pressurizerTemperature': 'TSAT',
            'reactorBuildingTemperature': 'TRB',
            'peakFuelTemperature': 'TFPK',
            'averageFuelTemperature': 'TF',
            'peakCladdingTemperature': 'TPCT',
            
            # Pressure mappings
            'rcsPressure': 'P',
            'steamGeneratorAPressure': 'PSGA',
            'steamGeneratorBPressure': 'PSGB',
            'pressurizerLevel': 'LVPZ',
            'reactorBuildingPressure': 'PRB',
            
            # Flow mappings
            'rcsFlowA': 'WRCA',
            'rcsFlowB': 'WRCB',
            'feedwaterFlowA': 'WFWA',
            'feedwaterFlowB': 'WFWB',
            'steamFlowA': 'WSTA',
            'steamFlowB': 'WSTB',
            'rcsLeakage': 'WLR',
            'chargingFlow': 'WCHG',
            
            # Level mappings
            'coreWaterLevel': 'LVCR',
            'steamGeneratorALevel': 'LSGA',
            'steamGeneratorBLevel': 'LSGB',
            
            # Power mappings
            'reactorThermalPower': 'QMWT',
            'neutronPower': 'PWNT',
            'coreThermalPower': 'PWR',
            'turbineLoad': 'TBLD',
            
            # Radiation mappings
            'radiationMonitor1': 'RM1',
            'radiationMonitor2': 'RM2',
            'radiationMonitor3': 'RM3',
            'radiationMonitor4': 'RM4',
            'rcsActivity': 'RC87',
            'hydrogenConcentration': 'CNH2',
            
            # Other mappings
            'boronConcentration': 'PPM',
            'dnbRatio': 'DNBR',
            'totalReactivity': 'RH'
        }
        
        # Apply parameter mappings
        for param_name, value in params.items():
            # Direct mapping
            if param_name in param_mapping:
                feature_name = param_mapping[param_name]
                if hasattr(state, feature_name):
                    setattr(state, feature_name, float(value))
            # Direct feature name
            elif hasattr(state, param_name):
                setattr(state, param_name, float(value))
        
        return state
    
    def reset_history(self) -> None:
        """Reset the feature history."""
        self.history = []
        logger.info("Feature history reset")
    
    def get_feature_names(self) -> List[str]:
        """
        Get the complete list of 288 feature names.
        
        Returns:
            List of feature names in order
        """
        feature_names = []
        
        # Base features
        feature_names.extend(self.base_features)
        
        # Rolling mean features
        for feature in self.base_features:
            feature_names.append(f"{feature}_rm{self.rolling_window}")
        
        # Difference features
        for feature in self.base_features:
            feature_names.append(f"{feature}_d1")
        
        return feature_names