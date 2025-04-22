clc
clear
close all

% Load .tir file in MATLAB
tireFilePath = 'C:\Users\Rohan Shinde\Box\BFR\MK10\Mk. 10 Vehicle Dynamics\Tires and Sim\Tires\Tire Fitting Tools\.tir Files\magicformula_R20.tir';

tireData = simscape.multibody.tirread(tireFilePath);

% Create a bus object based on `tireData`
busInfo = Simulink.Bus.createObject(tireData);
tireDataBus = eval(busInfo.busName); % Create a bus object named after the struct

% Assign `tireData` to the bus object type
tireDataParam = Simulink.Parameter;
tireDataParam.Value = tireData;
tireDataParam.DataType = 'Bus: tireDataBus';