% 读取音频文件
[audio, fs] = audioread('E:\2023\traindata\pitchtest3.m4a'); % 你的音频文件路径

% 设置音高检测参数
frameSize = 1024;
hopSize = 512;
minFreq = 80;
maxFreq = 10000;

% 计算音高
[pitchValues, timeInstants] = pitch(audio, fs, ...
    'Method', 'NCF', ...
    'Range', [minFreq, maxFreq]);

% 绘制音高随时间的变化
figure;
plot(timeInstants, pitchValues, '.-');
xlabel('Time (s)');
ylabel('Pitch (Hz)');
title('Pitch Variation Over Time');

% 播放音频(可选)
 %sound(audio, fs);