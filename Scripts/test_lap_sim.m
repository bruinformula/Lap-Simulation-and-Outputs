% Test script to check if the function signature error is fixed
try
    fprintf('Testing Lap_Sim syntax...\n');
    
    % Test basic function parsing
    addpath('Lap-Simulation');
    
    % Try to create a function handle - this will parse the file
    func_handle = @Lap_Sim;
    fprintf('Function handle created successfully.\n');
    
    % Check if the function can be inspected
    func_info = functions(func_handle);
    fprintf('Function info retrieved: %s\n', func_info.function);
    
    % Try to get help text (this will further validate the function)
    help_text = help('Lap_Sim');
    if ~isempty(help_text)
        fprintf('Help text found.\n');
    end
    
    fprintf('Basic syntax test PASSED.\n');
    
catch ME
    fprintf('SYNTAX ERROR: %s\n', ME.message);
    fprintf('Identifier: %s\n', ME.identifier);
    if ~isempty(ME.stack)
        fprintf('Location: %s at line %d\n', ME.stack(1).name, ME.stack(1).line);
    end
    
    % Try to give more specific error information
    if contains(ME.message, 'Too many input arguments')
        fprintf('\nThis appears to be a function signature mismatch.\n');
        fprintf('Check that all calls to calculateVehicleDynamics use the correct parameters.\n');
    end
end
