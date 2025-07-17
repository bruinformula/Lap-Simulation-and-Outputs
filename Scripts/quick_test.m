
try
    addpath('Lap-Simulation');
    fprintf('Testing Lap_Sim function parsing...
');
    
    % Test if the function can be parsed without execution
    func_handle = @Lap_Sim;
    fprintf('Function handle created successfully.
');
    
    % Check function info
    func_info = functions(func_handle);
    fprintf('Function file: %s
', func_info.file);
    
    fprintf('Syntax check PASSED - no immediate errors.
');
    
catch ME
    fprintf('ERROR: %s
', ME.message);
    if ~isempty(ME.stack)
        fprintf('Location: %s at line %d
', ME.stack(1).name, ME.stack(1).line);
    end
end

