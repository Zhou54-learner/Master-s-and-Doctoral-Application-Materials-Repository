%导入声音文件
filename = ['E:\2023\traindata\R7.5mm_r5.5mm\20cm\R7.5mmr5.5mm_20cm_01_1.m4a']; % 声音文件名
[y, Fs] = audioread(filename); % 读取声音文件
y = y(:,1); % 只保留单声道

% 计算声音长度和时间间隔
N = length(y); % 声音的样本数
duration = N / Fs; % 声音的时长
t = linspace(0, duration, N); % 时间间隔

% 对声音信号进行傅里叶变换
Y = fft(y); % 进行傅里叶变换
P2 = abs(Y / N); % 计算双边频谱
P1 = P2(1:N/2+1); % 留下单边频谱
P1(2:end-1) = 2*P1(2:end-1); % 乘以2以保持幅度正确

% 创建频率向量
f = Fs*(0:(N/2))/N;

% 绘制声音波形和频谱图
figure;
subplot(2,1,1);
plot(t, y);
xlabel('时间 (秒)');
ylabel('振幅');
title('声音波形');
subplot(2,1,2);
plot(f, P1);
xlabel('频率 (Hz)');
ylabel('幅度');
title('声音频谱');

% 播放音频
%sound(y, Fs);
