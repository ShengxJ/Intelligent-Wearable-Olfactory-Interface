function conc = GaussDispersion_ppm(x,y,z,U,H,Q,mol)
%GaussianDispersion  Function:
%       conc is the average concentration of diffusion substance at a
%       position (x, y, z) for OG at height H, x and U represent 
%       the downwind direction and the average wind/airflow speed, and y 
%       stands for the crosswind axis, Q is the source strength, mole
%       represents molecular weight in g/m3. The rate of emission in 
%       crosswind direction is determined according to Pasquill class A 
%       and B for low surface wind.
% Author:
%       JIA Shengxin 2023
if U>0.2
    sigmay=(0.16*x.*(1+0.0001*x).^(-0.5));
    sigmaz=0.12*x;  
else
    sigmay=(0.22*x.*(1+0.0001*x).^(-0.5));
    sigmaz=0.20*x;
end
conc=(Q./(2*pi*U*sigmay.*sigmaz)).*(exp((-(y.^2))./(2*sigmay.^2))).*((exp(-((z-H).^2)./(2*sigmaz.^2)))+(exp(-((z+H).^2)./(2*sigmaz.^2))));
conc=conc*24.45*mol/17.03*10^3;%convert g/m3 conc to ppm
end