function [output] = vxnn(x00,x1,x2,x3,x4,x5,x6,y00,y1,y2,y3,y4,y5,y6,vx00,vx1,vx2,vx3,vx4,vx5,vx6,vy00,vy1,vy2,vy3,vy4,vy5,vy6,dt,k,q00,q1,q2,q3,q4,q5,q6,m)
%UNTITLED6 下一时刻的vx
%   此处显示详细说明
    function[out2]=gx(a00,a1,a2,a3,a4,a5,a6,k1,b00,b1,b2,b3,b4,b5,b6,c00,c1,c2,c3,c4,c5,c6)
        out2=fxfl(a1,a00,b1,b00,k1,c1,c00)+fxfl(a2,a00,b2,b00,k1,c2,c00)+fxfl(a3,a00,b3,b00,k1,c3,c00)+fxfl(a4,a00,b4,b00,k1,c4,c00)+fxfl(a5,a00,b5,b00,k1,c5,c00)+fxfl(a6,a00,b6,b00,k1,c6,c00);
    end


[~,kx001,kx002,kx003,~] = xlg(x00,vx00,dt);
[~,kx11,kx12,kx13,~]=xlg(x1,vx1,dt);
[~,kx21,kx22,kx23,~]=xlg(x2,vx2,dt);
[~,kx31,kx32,kx33,~]=xlg(x3,vx3,dt);
[~,kx41,kx42,kx43,~]=xlg(x4,vx4,dt);
[~,kx51,kx52,kx53,~]=xlg(x5,vx5,dt);
[~,kx61,kx62,kx63,~]=xlg(x6,vx6,dt);
[~,ky001,ky002,ky003,~] = xlg(y00,vy00,dt);
[~,ky11,ky12,ky13,~]=xlg(y1,vy1,dt);
[~,ky21,ky22,ky23,~]=xlg(y2,vy2,dt);
[~,ky31,ky32,ky33,~]=xlg(y3,vy3,dt);
[~,ky41,ky42,ky43,~]=xlg(y4,vy4,dt);
[~,ky51,ky52,ky53,~]=xlg(y5,vy5,dt);
[~,ky61,ky62,ky63,~]=xlg(y6,vy6,dt);
l1=gx(x00,x1,x2,x3,x4,x5,x6,k,y00,y1,y2,y3,y4,y5,y6,q00,q1,q2,q3,q4,q5,q6);
l2=gx(x00+(dt*kx001/2),x1+(dt*kx11/2),x2+(dt*kx21/2),x3+(dt*kx31/2),x4+(dt*kx41/2),x5+(dt*kx51/2),x6+(dt*kx61/2),k,y00+(dt*ky001/2),y1+(dt*ky11/2),y2+(dt*ky21/2),y3+(dt*ky31/2),y4+(dt*ky41/2),y5+(dt*ky51/2),y6+(dt*ky61/2),q00,q1,q2,q3,q4,q5,q6);
l3=gx(x00+(dt*kx002/2),x1+(dt*kx12/2),x2+(dt*kx22/2),x3+(dt*kx32/2),x4+(dt*kx42/2),x5+(dt*kx52/2),x6+(dt*kx62/2),k,y00+(dt*ky002/2),y1+(dt*ky12/2),y2+(dt*ky22/2),y3+(dt*ky32/2),y4+(dt*ky42/2),y5+(dt*ky52/2),y6+(dt*ky62/2),q00,q1,q2,q3,q4,q5,q6);
l4=gx(x00+dt*kx003,x1+dt*kx13,x2+dt*kx23,x3+dt*kx33,x4+dt*kx43,x5+dt*kx53,x6+dt*kx63,k,y00+dt*ky003,y1+dt*ky13,y2+dt*ky23,y3+dt*ky33,y4+dt*ky43,y5+dt*ky53,y6+dt*ky63,q00,q1,q2,q3,q4,q5,q6);
output=vx00+dt*(l1+2*l2+2*l3+l4)/(6*m);

end