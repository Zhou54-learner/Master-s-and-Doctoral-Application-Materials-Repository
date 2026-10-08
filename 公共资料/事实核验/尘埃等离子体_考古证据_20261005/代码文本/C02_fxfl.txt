function [ax] = fxfl(x2,x1,y2,y1,k,R2,R1,M) %R，M为改变后电荷和质量与改变前的比值
%   x2对x1力的x分量,R为电荷比值
r=sqrt((x2-x1)^2+(y2-y1)^2);
ax=((1+r)*(x1-x2)*k^2./((1+k)*r^3))*exp(-(r-k))*R1*R2/M;
end