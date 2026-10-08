% 导入声音文件
filenames = {'E:\2023\traindata\R11.6mm_r8.0mm\100cm\R11.6mmr8mm_100cm_03_1.m4a', 'E:\2023\traindata\R11.6mm_r8.0mm\100cm\R11.6mmr8mm_100cm_03_2.m4a', 'E:\2023\traindata\R11.6mm_r8.0mm\100cm\R11.6mmr8mm_100cm_03_3.m4a', 'E:\2023\traindata\R11.6mm_r8.0mm\100cm\R11.6mmr8mm_100cm_03_4.m4a','E:\2023\traindata\R11.6mm_r8.0mm\100cm\R11.6mmr8mm_100cm_03_5.m4a'}; % 声音文件名
main_frequencies = zeros(1, length(filenames)); % 初始化主频数组
for i = 1:length(filenames)
    [y, Fs] = audioread(filenames{i}); % 读取声音文件
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

     % 查找主频
    [~, idx] = max(P1); % 找到频谱中最大幅度对应的索引
    main_frequency = (idx - 1) * Fs / length(y); % 计算主频

    % 存储主频
    main_frequencies(i) = main_frequency;

    % 创建频率向量
    f = Fs*(0:(N/2))/N;

    % 绘制声音波形和频谱图
    figure;
    subplot(2,1,1);
    plot(t, y);
    xlabel('时间 (秒)');
    ylabel('振幅');
    title(sprintf('声音波形 - 文件 %d', i));
    subplot(2,1,2);
    plot(f, P1);
    xlabel('频率 (Hz)');
    ylabel('幅度');
    title(sprintf('声音频谱 - 文件 %d', i));
end
 
 
 % 播放音频(可选)
    %sound(y, Fs);

% 计算主频的平均值
average_main_frequency = mean(main_frequencies);

% 将主频数据和平均值导出到 Excel 文件
data = [main_frequencies, average_main_frequency]; % 构造数据矩阵，注意转置以确保每个文件的主频在单独的列中
header = [ filenames, {'平均主频'}]; % 表头，确保平均主频在列表最右侧
xlswrite('main_frequencies.xlsx', header, 'Sheet1', 'A1'); % 写入表头
xlswrite('main_frequencies.xlsx', data, 'Sheet1', 'A2'); % 写入数据