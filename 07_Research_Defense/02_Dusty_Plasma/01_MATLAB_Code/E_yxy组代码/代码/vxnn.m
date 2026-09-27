function [output] = vxnn(a00,a1,a2,a3,a4,a5,a6,b00,b1,b2,b3,b4,b5,b6,k,R0,R1,R2,R3,R4,R5,R6,M0)
%UNTITLED6 下一时刻的vx
output=fxfl(a1,a00,b1,b00,k,R1,R0,M0)+fxfl(a2,a00,b2,b00,k,R2,R0,M0)+fxfl(a3,a00,b3,b00,k,R3,R0,M0)+fxfl(a4,a00,b4,b00,k,R4,R0,M0)+fxfl(a5,a00,b5,b00,k,R5,R0,M0)+fxfl(a6,a00,b6,b00,k,R6,R0, M0);
end