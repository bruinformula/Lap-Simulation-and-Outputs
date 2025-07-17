"""
Tire Model Module
=================

Implementation of the Magic Formula 5.2 tire model for lateral force calculation.
"""

import numpy as np
from typing import Dict, Any, Union, Optional


# Global variables for tire model (converted from MATLAB globals)
TIRE_GLOBALS = {
    'FZ0': None,
    'LFZO': None, 
    'LCY': None,
    'LMUY': None,
    'LEY': None,
    'LKY': None,
    'LHY': None,
    'LVY': None,
    'LGAY': None,
    'KY': None
}


def set_tire_globals(tire_data: Dict[str, Any]) -> None:
    """
    Set global tire parameters from loaded data.
    
    Parameters:
    -----------
    tire_data : Dict[str, Any]
        Dictionary containing tire model parameters
    """
    global TIRE_GLOBALS
    
    # Extract parameters from tire data
    # These would typically be loaded from the .mat files
    TIRE_GLOBALS.update({
        'FZ0': tire_data.get('FZ0', 220.0),  # Reference normal force
        'LFZO': tire_data.get('LFZO', 1.0),  # Load scaling factor
        'LCY': tire_data.get('LCY', 1.0),    # Cornering stiffness scaling
        'LMUY': tire_data.get('LMUY', 1.0),  # Friction scaling
        'LEY': tire_data.get('LEY', 1.0),    # Curvature factor scaling
        'LKY': tire_data.get('LKY', 1.0),    # Cornering stiffness scaling
        'LHY': tire_data.get('LHY', 1.0),    # Horizontal shift scaling
        'LVY': tire_data.get('LVY', 1.0),    # Vertical shift scaling
        'LGAY': tire_data.get('LGAY', 1.0),  # Camber scaling
        'KY': tire_data.get('KY', 1.0)       # Cornering stiffness
    })


def MF52_Fy_fcn(A: np.ndarray, X: np.ndarray) -> np.ndarray:
    """
    Magic Formula 5.2 lateral force calculation.
    
    This function implements the MF5.2 fitting of tire data provided by the
    Tire Testing Consortium.
    
    Parameters:
    -----------
    A : np.ndarray
        Array of Magic Formula coefficients [18 elements]
        A[0]: PCy1, A[1]: PDy1, A[2]: PDy2, A[3]: PDy3,
        A[4]: PEy1, A[5]: PEy2, A[6]: PEy3, A[7]: PEy4,
        A[8]: PKy1, A[9]: PKy2, A[10]: PKy3,
        A[11]: PHy1, A[12]: PHy2, A[13]: PHy3,
        A[14]: PVy1, A[15]: PVy2, A[16]: PVy3, A[17]: PVy4
        
    X : np.ndarray
        Input array with shape (n, 3) where:
        X[:, 0]: Slip angle [degrees]
        X[:, 1]: Normal force [N] (negative values)
        X[:, 2]: Camber angle [degrees]
        
    Returns:
    --------
    np.ndarray
        Lateral force Fy [N]
    """
    global TIRE_GLOBALS
    
    # Convert inputs
    ALPHA = X[:, 0] * np.pi / 180  # Slip angle in radians
    Fz = np.abs(X[:, 1])           # Normal force (positive)
    GAMMA = X[:, 2] * np.pi / 180  # Camber angle in radians
    
    # Get global parameters with defaults
    FZ0 = TIRE_GLOBALS.get('FZ0', 220.0)
    LFZO = TIRE_GLOBALS.get('LFZO', 1.0)
    LCY = TIRE_GLOBALS.get('LCY', 1.0)
    LMUY = TIRE_GLOBALS.get('LMUY', 1.0)
    LEY = TIRE_GLOBALS.get('LEY', 1.0)
    LKY = TIRE_GLOBALS.get('LKY', 1.0)
    LHY = TIRE_GLOBALS.get('LHY', 1.0)
    LVY = TIRE_GLOBALS.get('LVY', 1.0)
    LGAY = TIRE_GLOBALS.get('LGAY', 1.0)
    
    # Calculate derived parameters
    GAMMAy = GAMMA * LGAY
    Fz0PR = FZ0 * LFZO
    DFz = (Fz - Fz0PR) / Fz0PR
    
    # Extract Magic Formula coefficients
    PCy1 = A[0]
    PDy1 = A[1]
    PDy2 = A[2]
    PDy3 = A[3]
    PEy1 = A[4]
    PEy2 = A[5]
    PEy3 = A[6]
    PEy4 = A[7]
    PKy1 = A[8]
    PKy2 = A[9]
    PKy3 = A[10]
    PHy1 = A[11]
    PHy2 = A[12]
    PHy3 = A[13]
    PVy1 = A[14]
    PVy2 = A[15]
    PVy3 = A[16]
    PVy4 = A[17]
    
    # Calculate Magic Formula parameters
    SHy = (PHy1 + PHy2 * DFz) * LHY + PHy3 * GAMMAy
    ALPHAy = ALPHA + SHy
    Cy = PCy1 * LCY
    MUy = (PDy1 + PDy2 * DFz) * (1.0 - PDy3 * GAMMAy**2) * LMUY
    Dy = MUy * Fz
    KY = (PKy1 * FZ0 * np.sin(2.0 * np.arctan(Fz / (PKy2 * FZ0 * LFZO))) * 
          (1.0 - PKy3 * np.abs(GAMMAy)) * LFZO * LKY)
    By = KY / (Cy * Dy)
    Ey = ((PEy1 + PEy2 * DFz) * 
          (1.0 - (PEy3 + PEy4 * GAMMAy) * np.sign(ALPHAy)) * LEY)
    SVy = (Fz * ((PVy1 + PVy2 * DFz) * LVY + 
                 (PVy3 + PVy4 * DFz) * GAMMAy) * LMUY)
    
    # Calculate lateral force
    Fy0 = (Dy * np.sin(Cy * np.arctan(By * ALPHAy - 
                                      Ey * (By * ALPHAy - np.arctan(By * ALPHAy)))) + SVy)
    Fy = Fy0
    
    return Fy


def interpolate_tire_force(slip_ratio: np.ndarray, normal_force: Union[float, np.ndarray], 
                          camber_angle: Union[float, np.ndarray], tire_data: Dict[str, Any],
                          scale_factor: float = 1.0) -> np.ndarray:
    """
    Interpolate tire force from lookup table data.
    
    Parameters:
    -----------
    slip_ratio : np.ndarray
        Array of slip ratios
    normal_force : float
        Normal force on tire [N]
    camber_angle : float
        Camber angle [degrees]
    tire_data : Dict[str, Any]
        Tire data dictionary from .mat file
    scale_factor : float
        Scaling factor for tire force
        
    Returns:
    --------
    np.ndarray
        Interpolated tire forces
    """
    # This function would implement interpolation from the tire data tables
    # For now, return a simplified model
    
    # Ensure inputs are arrays for consistent processing
    normal_force = np.atleast_1d(normal_force)
    camber_angle = np.atleast_1d(camber_angle)
    
    # Extract data from tire_data if available
    if 'full_send_x' in tire_data:
        # Use the spline data from MATLAB
        # This would require scipy.interpolate for proper implementation
        from scipy.interpolate import griddata
        
        # Placeholder implementation - would need actual spline interpolation
        # based on the MATLAB fnval function equivalent
        forces = np.zeros_like(slip_ratio)
        
        # Simple model for demonstration
        for i, sr in enumerate(slip_ratio):
            # Create input vector matching MATLAB format
            nf = normal_force[0] if len(normal_force) == 1 else normal_force[i]
            ca = camber_angle[0] if len(camber_angle) == 1 else camber_angle[i]
            input_vec = np.array([sr, -nf, ca])
            # Simplified force calculation (replace with actual interpolation)
            forces[i] = nf * sr * 0.8 * scale_factor
            
        return forces
    else:
        # Fallback to simple model
        nf = normal_force[0] if len(normal_force) == 1 else normal_force
        return nf * slip_ratio * 0.8 * scale_factor


class TireModel:
    """
    Comprehensive tire model class combining lateral and longitudinal models.
    """
    
    def __init__(self, data_dir: str, scale_factors: Optional[Dict[str, float]] = None):
        """
        Initialize tire model.
        
        Parameters:
        -----------
        data_dir : str
            Directory containing tire data files
        scale_factors : Dict[str, float], optional
            Scaling factors for tire forces {'x': sf_x, 'y': sf_y}
        """
        self.data_dir = data_dir
        self.scale_factors = scale_factors or {'x': 0.6, 'y': 0.47}
        
        # Load tire data
        from .data_loader import load_tire_data
        self.lateral_model, self.lateral_coeffs, self.longitudinal_data = load_tire_data(data_dir)
        
        # Set global parameters
        set_tire_globals(self.lateral_coeffs)
        
    def calculate_lateral_force(self, slip_angle: Union[float, np.ndarray],
                               normal_force: Union[float, np.ndarray],
                               camber_angle: Union[float, np.ndarray] = 0.0) -> np.ndarray:
        """
        Calculate lateral tire force using Magic Formula.
        
        Parameters:
        -----------
        slip_angle : float or np.ndarray
            Slip angle [degrees]
        normal_force : float or np.ndarray
            Normal force [N]
        camber_angle : float or np.ndarray
            Camber angle [degrees]
            
        Returns:
        --------
        np.ndarray
            Lateral force [N]
        """
        # Ensure inputs are arrays
        slip_angle = np.atleast_1d(slip_angle)
        normal_force = np.atleast_1d(normal_force)
        camber_angle = np.atleast_1d(camber_angle)
        
        # Create input matrix
        X = np.column_stack([slip_angle, normal_force, camber_angle])
        
        # Get coefficients (would be loaded from .mat file)
        A = self.lateral_coeffs.get('A', np.ones(18))  # Placeholder
        
        # Calculate force
        Fy = MF52_Fy_fcn(A, X) * self.scale_factors['y']
        
        return Fy
    
    def calculate_longitudinal_force(self, slip_ratio: Union[float, np.ndarray],
                                   normal_force: Union[float, np.ndarray],
                                   camber_angle: Union[float, np.ndarray] = 0.0) -> np.ndarray:
        """
        Calculate longitudinal tire force.
        
        Parameters:
        -----------
        slip_ratio : float or np.ndarray
            Slip ratio [-]
        normal_force : float or np.ndarray
            Normal force [N]
        camber_angle : float or np.ndarray
            Camber angle [degrees]
            
        Returns:
        --------
        np.ndarray
            Longitudinal force [N]
        """
        # Ensure inputs are arrays
        slip_ratio = np.atleast_1d(slip_ratio)
        normal_force = np.atleast_1d(normal_force)
        camber_angle = np.atleast_1d(camber_angle)
        
        # Use interpolation from longitudinal data
        Fx = interpolate_tire_force(slip_ratio, normal_force, camber_angle,
                                   self.longitudinal_data, self.scale_factors['x'])
        
        return Fx
