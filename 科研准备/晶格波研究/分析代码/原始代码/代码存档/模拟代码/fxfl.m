function [fx] = fxfl(x2,x1,y2,y1,k,q2,q1)
%UNTITLED2 此处显示有关此函数的摘要
%   x2对x1力的x分量
r=sqrt((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1));
fx=-((x2-x1)*q1*q2*(1+k*r)*exp(-k*r))/(r*r*r);
end