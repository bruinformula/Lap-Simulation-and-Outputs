%% Section 1: Getting Longitudinal and Lateral Accelerations around Track
endurance_coords = "../Endurance_Coordinates_1.xlsx";
addpath('Lap-Simulation');
[A_long_g, A_lat_g] = Lap_Sim(endurance_coords);

%% Section 2

addpath('Tire-Load-Transfer');

% Determine number of samples
N = numel(A_lat_g);                                  % number of data points based on vector length

% Preallocate arrays for each corner's loads
loads_FL = zeros(N,1);
loads_FR = zeros(N,1);
loads_RL = zeros(N,1);
loads_RR = zeros(N,1);

% Loop over each sample and compute loads using the transfer model
for i = 1:N                                          
    [~,~,~,~, lf, fr, rl, rr] = loadTransferModel(A_lat_g(i), A_long_g(i));
    loads_FL(i) = lf;                                % store front-left load for sample i
    loads_FR(i) = fr;                                % store front-right load for sample i
    loads_RL(i) = rl;                                % store rear-left load for sample i
    loads_RR(i) = rr;                                % store rear-right load for sample i
end                                                  % end loop

% Create figure window for plotting
figure('Name','Corner Loads','NumberTitle','off');     % new figure with custom title

% Plot Front-Left loads
subplot(2,2,1);                                     % top-left position in 2x2 grid
plot(loads_FL,'LineWidth',1.5);                     % plot values vs. sample index
title('Front Left','FontWeight','bold');            % add bold title
xlabel('Sample #');                                  % label x-axis
ylabel('Load (lbs)');                                % label y-axis

% Plot Front-Right loads
subplot(2,2,2);                                     % top-right position in grid
plot(loads_FR,'LineWidth',1.5);                     % plot values vs. sample index
title('Front Right','FontWeight','bold');           % add bold title
xlabel('Sample #');                                  % label x-axis
ylabel('Load (lbs)');                                % label y-axis

% Plot Rear-Left loads
subplot(2,2,3);                                     % bottom-left position in grid
plot(loads_RL,'LineWidth',1.5);                     % plot values vs. sample index
title('Rear Left','FontWeight','bold');             % add bold title
xlabel('Sample #');                                  % label x-axis
ylabel('Load (lbs)');                                % label y-axis

% Plot Rear-Right loads
subplot(2,2,4);                                     % bottom-right position in grid
plot(loads_RR,'LineWidth',1.5);                    % plot values vs. sample index
title('Rear Right','FontWeight','bold');            % add bold title
xlabel('Sample #');                                  % label x-axis
ylabel('Load (lbs)');                                % label y-axis
