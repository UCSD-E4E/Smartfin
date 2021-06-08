df = readtable("2021.04.27.06.51.14.txt")
df.xAcc = df.xAcc .* 9.81; %Accelerometer multiply by 0.019141 to get m/s^2 or divide by 512 to
%get answer in Gs
df.yAcc = df.yAcc .* 9.81;
df.zAcc = df.zAcc .* 9.81;
%%
figure(1)
%accelerometer plots
subplot(331)
plot(df.time,df.xAcc)
title('x-axis')
ylabel('m/s^2')
xlabel('time [s]')
subplot(332)
plot(df.time,df.yAcc)
title('y-axis')
ylabel('m/s^2')
xlabel('time [s]')
subplot(333)
plot(df.time,df.zAcc)
title('z-axis')
ylabel('m/s^2')
xlabel('time [s]')

%angle plots
subplot(334)
plot(df.time,df.xAng)
title('x-gyro')
ylabel('degrees/second')
xlabel('time [s]')
subplot(335)
plot(df.time,df.yAng)
title('y-gyro')
ylabel('degrees/second')
xlabel('time [s]')
subplot(336)
plot(df.time,df.zAng)
title('z-gyro')
ylabel('degrees/second')
xlabel('time [s]')

%mag plots
subplot(337)
plot(df.time,df.xMag)
title('x-mag')
ylabel('micro-Teslas')
xlabel('time [s]')
subplot(338)
plot(df.time,df.yMag)
title('y-mag')
ylabel('micro-Teslas')
xlabel('time [s]')
subplot(339)
plot(df.time,df.zMag)
title('z-mag')
ylabel('micro-Teslas')
xlabel('time [s]')
%%
figure(2)
clf
plot(df.time,df.temp)
title('temperature vs. time')
xlabel('time [s]')
ylabel('temperature [^oC]')
%%
figure(5)
idx = find(df.water > 0)
plot(df.time,df.water,"LineWidth",20)
title('in water?')
%%
names = df.Properties.VariableNames(2:10);
data = df(:,2:10);
data_to_calc = table2array(data);
stds = zeros(1,9);
var = zeros(1,9);
for i=1:9    
    stds(i) = nanstd(data_to_calc(:,i));
    var(i) = (nanstd(data_to_calc(:,i)))^2;
end
results = [stds ; var];
results = array2table(results,"RowNames",{'std. dev.','variance'});
results.Properties.VariableNames(:) = names;
results
%%
figure(6)
clf
x1 = linspace(-1,2.5,50);
x2 = linspace(7.5,12.5,50);
x3 = linspace(-3,3,50);

subplot(311)
histogram(df.Ax,"Normalization","pdf")
x_gaus = normpdf(x1,nanmean(df.Ax),nanstd(df.Ax));
hold on
plot(x1,x_gaus,"LineWidth",2)
subplot(312)
histogram(df.Ay,"Normalization","pdf")
y_gaus = normpdf(x2,nanmean(df.Ay),nanstd(df.Ay));
hold on
plot(x2,y_gaus,"LineWidth",2)
subplot(313)
histogram(df.Az,"Normalization","pdf")
z_gaus = normpdf(x3,nanmean(df.Az),nanstd(df.Az));
hold on
plot(x3,z_gaus,"LineWidth",2)

% histogram(Ss_anom,binsize,'Normalization','pdf')
% Ss_gaus = normpdf(x2,nanmean(Ss_anom),nanstd(Ss_anom));
% hold on
% plot(x2,Ss_gaus,'LineWidth',2)