function [W_i_FL, W_i_FR, W_i_RL, W_i_RR, loads_FL, loads_FR, loads_RL, loads_RR] = loadTransferModel(A_lat_g, A_long_g)
% Car: Mk.9
% Function: Static Steady State Load Transfer Model (Optimized)
% Purpose: Calculate load transfer matrices based on acceleration inputs.
% Inputs:
%   A_lat_g - Lateral acceleration in Gs
%   A_long_g - Longitudinal acceleration in Gs (use negative for deceleration)
% Outputs:
%   W_i_FL, W_i_FR, W_i_RL, W_i_RR - Initial load matrix elements
%   loads_FL, loads_FR, loads_RL, loads_RR - Final load matrix elements

% Constants and car parameters
wheelbase = 61; % in
trackwidth = 51; % in
W = 671; % total weight, lbs
CG_z = 11.1; % height of CoG in z-axis, in
CG_x = 34.465; % x position of CG from front axle, in
Z_RF = 1.5; % Front Roll Center Height, in
Z_RR = 2; % Rear Roll Center Height, in

% Axle Roll Stiffness
Kphi_F_max = 15610.54; % ft*lbf/rad 
Kphi_R_max = 18784.76; % ft*lbf/rad
Ks = 225; % lbf/in
MR_F = 1.177; % wheel to shock travel
MR_R = 1.168; % wheel to shock travel

% Convert accelerations from Gs to lbf (assuming 1 G = 32.174 ft/s^2)
% A_long = A_long_g * 32.174;
% A_lat = A_lat_g * 32.174;

% Calculate intermediate values
a = CG_x; 
b = wheelbase - a;
H = (CG_z - ((Z_RR - Z_RF) / wheelbase) * a - Z_RF) / 12; % ft distance between CG and Roll Axis 

% Longitudinal and Lateral Load Transfer
delta_Wx = CG_z * W * A_long_g / wheelbase; % lbf 
delta_Wy_F = (A_lat_g * W / (trackwidth / 12)) * ((H * Kphi_F_max) / ...
    (Kphi_F_max + Kphi_R_max) + (b * Z_RF / (12 * wheelbase)));
delta_Wy_R = (A_lat_g * W / (trackwidth / 12)) * ((H * Kphi_R_max) / ...
    (Kphi_F_max + Kphi_R_max) + (a * Z_RR / (12 * wheelbase)));

%% Initial Load Matrix
W_i_FL = W * (b / wheelbase) / 2;
W_i_FR = W * (b / wheelbase) / 2;
W_i_RL = W * (a / wheelbase) / 2;
W_i_RR = W * (a / wheelbase) / 2;

%% Suspension Load Transfer Matrix
loads_FL = W_i_FL - delta_Wx / 2 + delta_Wy_F;
loads_FR = W_i_FR - delta_Wx / 2 - delta_Wy_F;
loads_RL = W_i_RL + delta_Wx / 2 + delta_Wy_R;
loads_RR = W_i_RR + delta_Wx / 2 - delta_Wy_R;

%% Aero Loads
rho = 0.0023769; % air density slug/ft3
v_squared = 35^2; % velocity squared in ft^2/s^2
aero_factor = 0.5 * rho * v_squared;
Cl_Area = aero_factor * 0.782 * 12.3785; % Lift coefficient * frontal area
Cd_Area = aero_factor * 0.418 * 12.3785; % Drag coefficient * frontal area
CoP_x_bias = 1 - 37.4 / wheelbase; % center of pressure front/rear bias              
CoP_z_wb = 27.5 / wheelbase; % normalized height of CoP

downforce_FL_FR = Cl_Area * CoP_x_bias;
downforce_RL_RR = Cl_Area * (1 - CoP_x_bias);

drag_FL_FR = -Cd_Area * CoP_z_wb;
drag_RL_RR = Cd_Area * CoP_z_wb;

%% Final Load Matrix
loads_FL = loads_FL + downforce_FL_FR + drag_FL_FR;
loads_FR = loads_FR + downforce_FL_FR + drag_FL_FR;
loads_RL = loads_RL + downforce_RL_RR + drag_RL_RR;
loads_RR = loads_RR + downforce_RL_RR + drag_RL_RR;
end
