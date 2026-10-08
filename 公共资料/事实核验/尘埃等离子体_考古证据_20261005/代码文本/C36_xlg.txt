function [xynn,k1,k2,k3,k4] = xlg(xyn,vij,dt)
%UNTITLED5 下一时刻的x或y
%   此处显示详细说明
    
k1=vij;
k2=vij+dt*k1/2;
k3=vij+dt*k2/2;
k4=vij+dt*k3; 
xynn=xyn+dt*(k1+2*k2+2*k3+k4)/6;

end