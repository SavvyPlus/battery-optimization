% Auther: Will
% Email: weiliangzhou93@gmail.com

%% Function to solve the battery optimization problem
function y = lpfunc_FirstDay(spot_price)
% Minimize the objective function
sp1 = zeros(96,1);
sp1(1:48) = spot_price;
sp2 = zeros(96,1);
sp2(49:96) = spot_price;

ff = -(sp1/2/1.2-sp2/2);
f = transpose(ff);
% A*x<=b
A = zeros(96,96);
% Discharge limit. No more than capacity
for i = 1:48
    A(i,1:0+i) = 1;
end
for i = 2:48
    A(i,49:48+0+i-1) = -1;
end
for i = 2:48
    A(48+i,1:0+i-1) = -1;
end
for i = 2:48
    A(48+i,48+1:48+0+i-1) = 1;
end
% b
b = zeros(96,1);
b(49:96) = 120;

% Aeq*x=beq
Aeq = zeros(49,96);
Aeq(1,1) = 1;
Aeq(48,48) = 1;
Aeq(49,1:47) = -1;
Aeq(49,49:95) = 1;
beq = zeros(49,1);
beq(49,1) = 120;
% set the trigger price $300
% for i = 1:48
%     if spot_price < 300
%         Aeq(i,i) = 1;
%     end
% end
% lb, ub
lb = zeros(96,1);
ub = zeros(96,1);
ub(:) = 120;
% ub(1:48) = 100;
% ub(49:96) = 120;

y = linprog(f,A,b,Aeq,beq,lb,ub);