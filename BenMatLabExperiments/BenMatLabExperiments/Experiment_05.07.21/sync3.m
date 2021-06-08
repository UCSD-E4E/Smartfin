df = readtable("05.07.21-decoded.csv");
df = df(1:2137,:); %get first session
df = sortrows(df,"time"); %start time is 6:36
df.Ax = df.Ax.*9.81;
df.Ay = df.Ay.*9.81;
df.Az = df.Az.*9.81;
df.Ay = detrend(df.Ay);
df.Ay = df.Ay - mean(df.Ay);
df
dp = readtable("05.07.21-Pierwaves.csv");
dp.Data = detrend(dp.Data);
dp.Data = dp.Data - mean(dp.Data);
dp.Displacement = dp.Data;
dp.Velocity = zeros(length(dp.Data),1);
dp.Velocity(1:end-1) = diff(dp.Displacement)./diff(dp.UnixTimestamp);
dp.Acceleration = zeros(length(dp.Data),1);
dp.Acceleration(1:end-2) = diff(dp.Velocity(1:end-1))./diff(dp.UnixTimestamp(1:end-1));
dp.time = datetime(dp.UnixTimestamp, 'convertfrom','posixtime');
dp
%%
figure(1)
clf
yyaxis right
plot(df.time(180:1000),df.Ay(180:1000))
ylim([-.2 .2])
hold on
x = 1:1:(1281-695);
yyaxis left
plot(x,dp.Acceleration(696:1281))
ylim([-25 25])

% now loop through 586 s of fin vs. pier and find when they are best
% correlated
%dp.time(361) is 6:36 pst
%dp.time(696:1281) is 6:41:35 : 6:51:20 pst +/- 2 seconds. Figure out the
%timestamp for displacement
%%
%if I iterate through df.Ay(start:end) changing by one each time then maybe
%I can find the best correlation window
a = zeros(1,length(df.Ay));
pier = dp.Acceleration(696:1281); %This is the data chunk I want to compare the smartfin data to
n = (length(df.Ay)-586);
for i = 1:n
    fin = df.Ay(i:i+585);
    b = corrcoef(fin,pier);
    a(i) = b(1,2);
end
a
[maximum,idx] = max(a)
%%
figure(3)
clf
x = 1:1:(1281-695);
[peakspier, idx] = findpeaks(lowpass(pier,1/25))
[peaksfin, idy] = findpeaks(lowpass(-df.Ay(300:885),1/5))
plot(x,lowpass(pier,1/25))
hold on
scatter(idx,peakspier)
yyaxis right
plot(x,lowpass(-df.Ay(300:885),1/5))
scatter(idy,peaksfin)
legend('pier','smartfin')
%%
figure(4)
clf
x = 1:1:(1281-695);
plot(x,lowpass(pier,1/50))
hold on
yyaxis right
plot(x,lowpass(-df.Ay(290:875),1/5))
legend('pier','smartfin')
%%
% a = zeros(1,length(df.Ay));
% for i = 1:length(df.Ay)-585
%     fin = (df.Ay(i:i+584));
%     b = corrcoef(fin,dp.Acceleration);
%     a(i) = b(1,2);
% end
% [maximum idx] = max(a)
% %fin_exp = df2.Ay(idx:idx+108)
%%
df.Ay(1:586)
%%
%temp data to sync maybe
%%
dtemp = readtable("05.07.21-Piertemp.csv")
figure(6)
clf
pier_temp = dtemp.WaterTemp__C_(256:262)
temp_time = linspace(1,length(df.temp),7)
plot(temp_time,pier_temp) %6:30 : 7:06
hold on
plot(df.time,df.temp)
legend('pier','Smartfin')
xlabel('time [s]')
ylabel('Temp [^oC]')
title('Temp vs. Time')
%%
plot(df.time)