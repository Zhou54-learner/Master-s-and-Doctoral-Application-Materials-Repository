% Native MATLAB render only. No historical analysis code, FFT or solver is run.
out=fileparts(fileparts(mfilename('fullpath')));
audit=fullfile(out,'历史资产核查');
sources={...
 'E:/2023/traindata/R11.6mm_r8.0mm/60cm/R11.6mmr8mm_60mm_scale.fig',...
 'E:/2023/traindata/R11.6mm_r8.0mm/80cm/R11.6mmr8mm_80mm_scale.fig'};
labels={'历史FIG_60cm_原标签','历史FIG_80cm_原标签'};
logs=struct([]);
for k=1:numel(sources)
 f=openfig(sources{k},'new','invisible');
 ax=findall(f,'Type','axes');ln=findall(f,'Type','line');
 logs(k).source=sources{k};logs(k).matlab_version=version;
 logs(k).xlabel=get(get(ax(1),'XLabel'),'String');
 logs(k).title=get(get(ax(1),'Title'),'String');
 logs(k).line_count=numel(ln);
 logs(k).xdata_first_last=[ln(1).XData(1),ln(1).XData(end)];
 set(f,'PaperPositionMode','auto');
 print(f,fullfile(audit,[labels{k},'.png']),'-dpng','-r200');
 print(f,fullfile(audit,[labels{k},'.pdf']),'-dpdf','-bestfit','-painters');
 close(f);
end
fid=fopen(fullfile(audit,'MATLAB实际渲染.json'),'w','n','UTF-8');
fprintf(fid,'%s',jsonencode(logs));fclose(fid);
