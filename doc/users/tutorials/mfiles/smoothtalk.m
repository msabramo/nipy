% smoothtalk.m
% Script to generate figures and data for smoothing tutorial
% Matthew Brett 6/8/99

% seed random number generator
seed = 5;
randn('seed', seed);

% make vectors of points for the x axis 
minx = 1; 
maxx = 40;
x = minx:maxx; % for discrete plots
fineness = 1/100; 
finex = minx:fineness:maxx; % for continuous plots

% make and plot random data
y = randn(size(x));
figure
bar(x,y)
curraxis = axis;
axis([minx-0.25 maxx+0.25 curraxis([3 4])]);

% The formula for a normal distribution Gaussian 
% is given by 
%                 1           ( (x-u)^2 )
%    f(r) = ------------ x exp| ------  |
%           sqrt(v*2*pi)      (   2v    )
% Where v is sigma, and u is the mean.

% simple Gaussian kernel sigma 1, mean 0, as for N pdf
kernx = -6:fineness:6;
skerny = 1/sqrt(2*pi) * exp(-kernx.^2/2); 
figure
plot(kernx, skerny);

% parameters for Gaussian kernel
FWHM = 4;
sig = FWHM/sqrt(8*log(2));

% select example datapoint
datap = 14;

% continuous kernel at example data point
kerny = exp(-(finex-datap).^2/(2*sig^2));
% make area under kernel sum to 1
kerny = kerny / sum(kerny) / fineness; 
figure
plot(finex, kerny);

% discrete kernel at example data point
kerny_i = exp(-(x-datap).^2/(2*sig^2));
% make area under kernel sum to 1
kerny_i = kerny_i / sum(kerny_i);
figure
bar(x, kerny_i);
curraxis = axis;
axis([minx-0.25 maxx+0.25 curraxis([3 4])]);

% do the smooth
sy = zeros(size(y));
for xi = x
  kerny_i =  exp(-(x-xi).^2/(2*sig^2));
  kerny_i = kerny_i / sum(kerny_i);
  sy(xi) = sum(y.*kerny_i);
end

% plot of smoothed data
figure
bar(x, sy);
curraxis = axis;
axis([minx-0.25 maxx+0.25 curraxis([3 4])]);

% square wave centred over example point
sqw = zeros(size(finex));
tmp = find(finex > (datap-FWHM) & finex < (datap + FWHM));
mx = 1 / FWHM / 2;
sqw(tmp) = ones(size(tmp)) * mx;
figure
plot(finex, sqw)
axis([minx maxx -mx*0.1 mx*1.1])

% 2d Gaussian kernel - fairly continuous
Dim = [20 20];
fineness = 0.1;
[x2d,y2d] = meshgrid(-(Dim(2)-1)/2:fineness:(Dim(2)-1)/2,...
		 -(Dim(1)-1)/2:fineness:(Dim(1)-1)/2);
gf    = exp(-(x2d.*x2d + y2d.*y2d)/(2*sig*sig));
gf    = gf/sum(sum(gf))/(fineness^2);
figure
colormap hsv
surf(x2d+Dim(1)/2,y2d+Dim(2)/2,gf);

% 2d Gaussian kernel - discrete
[x2d,y2d] = meshgrid(-(Dim(2)-1)/2:(Dim(2)-1)/2,-(Dim(1)-1)/2:(Dim(1)-1)/2);
gf    = exp(-(x2d.*x2d + y2d.*y2d)/(2*sig*sig));
gf    = gf/sum(sum(gf));
figure
bar3(gf,'r');
axis([0 Dim(1) 0 Dim(2) 0 max(gf(:))*1.2])
axis xy

% matched filter theorem stuff

% simulated data - 8 FWHM peak
FWHM = 8;
sig = FWHM/sqrt(8*log(2));
sigd = exp(-(x-datap).^2/(2*sig^2));
sigd = sigd / sum(sigd);

% add random noise
nsigd = sigd + (randn(size(sigd)) * max(sigd/3));

% display signal and noise
mx = max(nsigd) * 1.2;
mn = min(nsigd) * 1.2;
figax = [minx maxx mn mx];
figure
bar(x, sigd)
axis(figax);
figure
bar(x, nsigd)
axis(figax);

% smooth with matched filter
snsigd = zeros(size(nsigd));
for xi = x
  kerny_i =  exp(-(x-xi).^2/(2*sig^2));
  kerny_i = kerny_i / sum(kerny_i);
  snsigd(xi) = sum(nsigd.*kerny_i);
end
figure
bar(x, snsigd)
axis(figax)
