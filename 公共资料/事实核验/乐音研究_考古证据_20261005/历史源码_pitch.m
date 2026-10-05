% 选取69音高的频率440Hz，这是个整数，方便计算
standardFrequency = 440.0;

% 用于存放0 ~ 127音高对应的音高频率
noteFrequency = zeros(1, 128);

for i = 0:127
    noteFrequency(i + 1) = (standardFrequency / 32.0) * 2^((i - 9.0) / 12.0);
    fprintf('音高%d对应的频率为%.2f Hz\n', i, noteFrequency(i + 1));
end
