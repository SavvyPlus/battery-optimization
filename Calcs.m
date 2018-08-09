% Author: Will
% Email: weiliangzhou93@gmail.com

tic;
%% Calculations
% load('HH_Sim_Spot_300_VIC1_2018-07-24_ForBattery.mat');
spot_price = Spot_Sims(9:210672,1);

day = 0;
dispatch = zeros(96,1);
spot_price_temp = zeros(48,1);
for i = 1:5
    spot_price_temp(:,i) = spot_price(1+48*day:48+48*day);
    if i == 1
        dispatch_temp = lpfunc_FirstDay(spot_price_temp(:,i));
    else
        dispatch_temp = lpfunc_SecondTillEnd(spot_price_temp(:,i));
    end
    
    dispatch(:,i) = dispatch_temp;
    day = day + 1;
end

% x = lpfunc(spot_price);

toc;