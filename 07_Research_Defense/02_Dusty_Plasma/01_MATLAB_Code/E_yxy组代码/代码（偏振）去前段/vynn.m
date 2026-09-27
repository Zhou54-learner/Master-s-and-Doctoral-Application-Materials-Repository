function [output] = vynn(x00,x1,x2,x3,x4,x5,x6,y00,y1,y2,y3,y4,y5,y6,vy00,dt,k,q00,q1,q2,q3,q4,q5,q6,m,b)
%UNTITLED6 下一时刻的vy
%   此处显示详细说明
    function[out2]=gy(a00,a1,a2,a3,a4,a5,a6,k1,b00,b1,b2,b3,b4,b5,b6,c00,c1,c2,c3,c4,c5,c6)
        out2=fyfl(a1,a00,b1,b00,k1,c1,c00)+fyfl(a2,a00,b2,b00,k1,c2,c00)+fyfl(a3,a00,b3,b00,k1,c3,c00)+fyfl(a4,a00,b4,b00,k1,c4,c00)+fyfl(a5,a00,b5,b00,k1,c5,c00)+fyfl(a6,a00,b6,b00,k1,c6,c00);
    end
l1=gy(x00,x1,x2,x3,x4,x5,x6,k,y00,y1,y2,y3,y4,y5,y6,q00,q1,q2,q3,q4,q5,q6);
output=vy00+dt*(l1./m-b.*vy00);
end