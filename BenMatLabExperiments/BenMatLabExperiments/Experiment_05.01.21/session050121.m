df = readtable("decodeddata2.csv")
pier_data = readtable('autoss_c905_75dd_f5ff.csv')
%decodeddata2.csv is the session from 5-1-21
%% 
% Scripps Pier
% 
% Operated by the Scripps Institution of Oceanography (SIO). The instrument 
% package is mounted at a nominal depth of 5 meters MLLW. Historical data has 
% been collected continuously since April 4, 2005.
% 
% https://sccoos.org/data/autoss/

% %convert raw values into SI units
df.Ax = df.Ax .* 9.81; %Accelerometer multiply by 0.019141 to get m/s^2 or divide by 512 to
%get answer in Gs
df.Ay = df.Ay .* 9.81;
df.Az = df.Az .* 9.81;
% %Mag is already in micro-Teslas
% df.Gx = df.Gx ./8.2; %Gyroscope divide by 8.2 to get degrees/second
% df.Gy = df.Gy ./8.2;
% df.Gz = df.Gz ./8.2;
%%
figure(1)
clf
%accelerometer plots
subplot(331)
plot(df.time,df.Ax)
title('x-axis')
ylabel('m/s^2')
xlabel('time [s]')
subplot(332)
plot(df.time,df.Ay)
title('y-axis')
ylabel('m/s^2')
xlabel('time [s]')
subplot(333)
plot(df.time,df.Az)
title('z-axis')
ylabel('m/s^2')
xlabel('time [s]')
%Mag plots
subplot(334)
plot(df.time,df.Mx)
ylabel('micro-Teslas')
xlabel('time [s]')
title('x-Mag')
subplot(335)
plot(df.time,df.My)
ylabel('micro-Teslas')
xlabel('time [s]')
title('y-Mag')
subplot(336)
plot(df.time,df.Mz)
ylabel('micro-Teslas')
xlabel('time [s]')
title('z-Mag')
%Gyroscope plots
subplot(337)
plot(df.time,df.Gx)
ylabel('degrees/second')
xlabel('time [s]')
title('x-Gyro')
subplot(338)
plot(df.time,df.Gy)
ylabel('degrees/second')
xlabel('time [s]')
title('y-Gyro')
subplot(339)
plot(df.time,df.Gz)
ylabel('degrees/second')
xlabel('time [s]')
title('z-Gyro')
%%
temp = pier_data.temperature_celsius_(2702:2708);
time = linspace(0,length(df.time),length(temp));
% DateString = '2021-04-24T08:10:18Z'
% formatIn = 'yr-mo-dyThr:min:secZ';
% datevec(DateString,formatIn)
%%
figure(2)
clf
subplot(211)
plot(df.time,df.temp)
title('temperature vs. time')
xlabel('time [s]')
ylabel('temperature [^oC]')
subplot(212)
histogram(df.temp)

% ldg = legend('Smartfin','Scripps Pier','Location',"best")
% ldg.FontSize = 20

% subplot(211)
% plot(df.time,df.temp)
% title('temperature vs. time')
% xlabel('time [s]')
% ylabel('temperature [^oC]')
% subplot(212)
% histogram(df.temp)
%%
figure(3)
clf
idx = find(df.wet > 0);
scatter(df.time,df.wet)
title('in water?')
%%
names = df.Properties.VariableNames(6:14);
data = df(:,6:14);
data_to_calc = table2array(data);
stds = zeros(1,9);
var = zeros(1,9);
for i=1:9    
    stds(i) = std(data_to_calc(:,i));
    var(i) = (std(data_to_calc(:,i)))^2;
end
results = [stds ; var];
results = array2table(results,"RowNames",{'std. dev.','variance'});
results.Properties.VariableNames(:) = names;
results