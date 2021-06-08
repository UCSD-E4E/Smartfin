clear all
%Create data arrays
Temperature = zeros(7200,1);
IMU = zeros(7200,1);
GPS = zeros(7200,1);
TemperatureIMU = zeros(7200,1);
TemperatureGPS = zeros(7200,1);
TemperatureIMUGPS = zeros(7200,1);
Battery = zeros(7200,1);
TemperatureEpoch = zeros(7200,1);
IMUx3 = zeros(7200,1);
TemperatureIMUx3 = zeros(7200,1);
TemperatureIMUx3GPS = zeros(7200,1);
%%
%Fill with frequencies
start = 1;
time = 7200;
f1 = 0;
f2 = 0;
f3 = 0;
f4 = 0;
f5 = 0;
f6 = 0;
f7 = 10;
f8 = 0;
f9 = 0;
f10 = 1;

Battery(start:f7:time) = 1; %this number is the frequency in Hz(10 is 10 Hz)
TemperatureIMUx3(start:f10:time) = 1;

%%
%Multiply each array by its byte size
%sn = size of element n
s7 = 2;
s10 = 20;
Battery = Battery * s7;
TemperatureIMUx3 = TemperatureIMUx3 * s10;
%%
%Create table
df = [Temperature, IMU, GPS, TemperatureIMU, TemperatureGPS, TemperatureIMUGPS, Battery, TemperatureEpoch, IMUx3, TemperatureIMUx3, TemperatureIMUx3GPS];
%%
%Calculate total without padding and where padding is needed.
ca = cumsum(df);
caa = cumsum(ca,2);
sums = caa(:,end);
total = sums(7200);
n = round(total/496);
b = zeros(1,n);
for i = 1:n
    lastIndex = find(sums <= 496*i, 1, 'last');
    b(i) = sums(lastIndex);
    sums(lastIndex + 1 : end);
end
%%
%Size of padding and calculate sum
x = (496:496:(496*n));
padding = x - b;
totalpadding = sum(padding)
totalsize = total + totalpadding %bytes