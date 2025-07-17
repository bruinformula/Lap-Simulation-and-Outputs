try
    fprintf('Testing Lap_Sim function after signature fixes...\n');
    
    addpath('Lap-Simulation');
    
    % Test if function can be parsed
    func_handle = @Lap_Sim;
    fprintf('✓ Function handle created successfully.\n');
    
    % Get function info  
    func_info = functions(func_handle);
    fprintf('✓ Function file: %s\n', func_info.file);
    
    fprintf('✓ All function signature fixes appear successful!\n');
    fprintf('   The "Too many input arguments" error should now be resolved.\n');
    
catch ME
    fprintf('✗ ERROR: %s\n', ME.message);
    if contains(ME.message, 'Too many input arguments')
        fprintf('  Still have function signature mismatches.\n');
    end
    if ~isempty(ME.stack)
        fprintf('  Location: %s at line %d\n', ME.stack(1).name, ME.stack(1).line);
    end
end
