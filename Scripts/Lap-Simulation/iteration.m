%% Section 1: Getting Longitudinal and Lateral Accelerations around Track

% Define the path to the autocross coordinate file
ax_coords = "Autocross_Coordinates_1.xlsx";

% Add the necessary folders to the MATLAB path
addpath('Lap-Simulation');

% Initialize an empty table to store the results
results = table('Size', [0, 4], ...
    'VariableTypes', {'double', 'double', 'double', 'double'}, ...
    'VariableNames', {'Roll_Degree', 'RideRate_Front', 'RideRate_Rear', 'Time_Lap'});

% Loop through the roll degrees from 0.9 to 1.4
%for i = 0.9:0.1:1.4
    % Loop through the ride rates from 100 to 200
    for j = 100:10:200
        for k = 100:10:200
            laptime_ax = laptime(ax_coords, 1.4, j, k);

            % If laptime_ax is a vector, take only the last value
            if numel(laptime_ax) > 1
                laptime_ax = laptime_ax(end);
            end

            % Append the results as a new row
            results = [results; {1.4, j, k, laptime_ax}];
        end
    end
    fprintf('Completed simulation for roll degree: %.1f\n', i);

output_filename = '/Users/Hiro/Downloads/RollGradient_Simulation_Results_1.4.csv';

% Delete the file if it already exists
if exist(output_filename, 'file')
    delete(output_filename);
end

writetable(results, output_filename);

fprintf('Data successfully saved to %s\n', output_filename);
