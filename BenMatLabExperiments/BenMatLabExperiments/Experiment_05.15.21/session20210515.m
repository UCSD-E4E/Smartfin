%clear all; close all;
%%
df = readtable("20210515_decoded.csv"); % this is 2 sessions
%df = sortrows(df,"time")
%%
figure(1)
clf
scatter(df.Var1,df.time)
hold on
scatter(1,152,'o',"filled")
scatter(176,857,'o',"filled")
xlabel('Ensemble Index')
ylabel('Time (s)')
text(10,152,'Session 1')
text(185,857,'Session 2')
grid on
%%
df2 = df(176:end,:); %start of session 2 at the end of pier
%%
df2 = sortrows(df2,"time"); %sort data by time.
%now we have a good time series to work with
figure(2)
plot(df2.time)
xlabel('Index')
ylabel('Time (s)')
%%
figure(3) %this is all the gps data from session 2
clf
geoplot(df2.lat,df2.lon,'-*','Color','red')
geobasemap satellite
geolimits([32.86578 32.86887],[-117.25878 -117.25412])
title('Location of Surfer')
%We can get a nice gps location if the board is flipped over to start a new
%surf session
%%
df3 = readtable("Experiment3WaterTemperature.csv"); %GMT - 7 = PST 
%Nima flipped the board (to get the fin out of the water) at 2:02:22
%Nima flipped the board (to put the fin back into the water) at 2:02:44
%Start temperature data at 2:00 pm (21:00 GMT)
Pier_Temp = df3.WaterTemp__C_(4:9);
Pier_Time = linspace(1,1800,6);
%%
figure(4)
clf
avgtemp = nanmean(Pier_Temp);
avgtemp = ones(length(df2.temp),1) * avgtemp;
plot(avgtemp)
hold on
plot(df2.time,df2.temp) %How long is the response time from air to water

maximum = max(df2.temp)
minimum = min(df2.temp)
change = maximum - minimum
tau1 = change * 0.67
tau = maximum - tau1
[tofind, idx] = min(abs(df2.temp - tau))
%time to reach 67% of total change is 75 seconds
line([0 75],[0 df2.temp(idx)],'linestyle','--','color','g')
line([0 75], [df2.temp(idx) df2.temp(idx)],'linestyle','--','color','g')
scatter(75,df2.temp(idx),'green')
ylim([18 19.5])
%Pier is from 1:48 PM PST to 2:30 PM PST
%Do not know when Smartfin in from
%plot(df2.time, movmean(df2.temp,75))
legend('30 Minute Average Scripps Pier Temperature','Smartfin Temperature', 'Tau: 75 s (time to reach 67% of Final Temperature Change)')
xlabel('time (s)')
ylabel('Temperature (^oC)')
title('Temperature Vs. Time')
yticks('auto')
yticks(18:.1:19.5)
%What is the response time of the thermistor
%%
figure(5)
clf
find(df2.temp > 19 & df2.lat > 0) %find air temperature and gps lock to maybe see response time. Possibly do this with wet/dry sensor instead
df4 = df(15:175,:);
df4 = sortrows(df4,"time");
plot(df4.time,df4.temp)
title('Temperature vs. Time')
ylabel('Temp (^oC)')
xlabel('time (s)')
%write up the issues in this graph
%There is missing data (there is no explaination for the gap in time series,temp spikes, weird mini session at the beginning, partial session between
%session 1 & 2
%Session data is not correct for df4. I'm not sure how to separate the two
%sessions here it seems like they overlap
%%
figure(6)
clf
geoplot(df4.lat,df4.lon,'-*',"Color",'red')
hold on
geobasemap satellite
geolimits([32.86578 32.86887],[-117.25878 -117.25412])
title('Location of Surfer')
%%
df5 = readtable("Experiment3PierWaves.csv");
df5.DateTime = datetime(df5.UnixTimestamp, 'convertfrom', 'posixtime', 'Format', 'MM/dd/yy HH:mm:ss.SSS'); %add a column showing the datetime very clearly
df5.Data = detrend(df5.Data);
df5.Data = df5.Data - mean(df5.Data);
%Lets assume that the fin started recording at 2:02:44 ~+ 10 seconds
%% 
% Now we have five dataframes
% 
% df1: all decoded data, unsorted 
% 
% df2: s_ession 2,_ sorted
% 
% df3: Temp data from the pier 1:30 - 3:00 PM PST
% 
% df4: _Session 1_, sorted
% 
% df5: Wave height from Scripps Pier pressure sensor: 1:30 - 3:00 PM PST

Pierwaves = df5(1965:2223,:); %2:02:44 - 2:07:02
%Pierwaves = df5(1961:2219,:); %2:02:40 - 2:06:58
Displacement = Pierwaves.Data;
Velocity = diff(Displacement);
Acceleration = diff(Velocity);
figure(7)
clf
plot(Displacement)
hold on
plot(Velocity)
plot(Acceleration)
xlabel('time (s)')
title('displacement, velocity, acceleration')
legend('displacement','velocity','acceleration')
%%
%detrend fin data
%pier accelerations
FinAcceleration = df2.Ay(1:258)*9.81;
lpAcceleration = lowpass(Acceleration,1/25,1);
lpFinAcceleration = lowpass(FinAcceleration,1/25,1);
figure(8)
clf
yyaxis left
plot(lpFinAcceleration)
ylabel('Acceleration (m/s^2)')
%ylim([5 12])
hold on
yyaxis right
plot(lpAcceleration)
legend('fin','pier')
xlabel('time (s)')
title('Smartfin and Pier Wave Accelerations')
%ylim([-3 1.5])

correleation = corrcoef(lpFinAcceleration(1:end-1),lpAcceleration)
%%
% fin = lpFinAcceleration(1:180);
% lpAcceleration2 = diff(df5.Data(1800:2400));
% lpAcceleration2 = diff(lpAcceleration2);
% lpAcceleration2 = lowpass(lpAcceleration2,1/25,1);
%%
% a = zeros(1,length(lpAcceleration2));
% for i = 1:length(lpAcceleration2)-180
%     Pier = lpAcceleration2(i:i+179);
%     b = corrcoef(fin,Pier);
%     a(i) = b(1,2);
% end
% [maximum idx] = max(a)
% %fin_exp = df2.Ay(idx:idx+108)
% figure(9)
% clf
% plot(a)
%%