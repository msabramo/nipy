% smallvoltalk.m
% Script to generate figures for small volume random fields web page
% The script requires spm96 or 99 on the matlab path 
% and will run in matlab 4 or 5

% Constants for image simulations etc
Dim = [128 128];	% No of pixels in X, Y
VNo = prod(Dim);	% Total pixels
sFWHM = 8;		% Smoothing in number of pixels in x, y
seed = 6;		% Seed for random no generator

% Image of independent random nos
randn('seed', seed);
testimg = randn(Dim);

% smooth random number image
sd    = sFWHM/sqrt(8*log(2));   % sigma for this FWHM
smmat = spm_sptop(sd, Dim(1));  % (sparse) smoothing matrix in 1D
stestimg = smmat * testimg;     % apply in x
stestimg = (smmat * stestimg')';% then in y
stestimg = full(stestimg);      % back to non-sparse

% display smoothed image
figure
colormap('bone');
imagesc(stestimg)
axis xy;
xlabel('Pixel position in X')
ylabel('Pixel position in Y')
title(['Image 1 - smoothed with Gaussian kernel of FWHM ' num2str(sFWHM) ' by ' ...
      num2str(sFWHM) ' pixels'])

% put marks at resel centres
hold on
centres = sFWHM/2:sFWHM:Dim(1)-sFWHM/2;
[cx cy] = meshgrid(centres);
plot(cx, cy, 'rx')

% put square at centre
centre = Dim/2;
sidel = sFWHM*3;
o = sidel/2;
plot([-(o) -(o) o o -(o)]+centre(1),...
     [-(o) o o -(o) -(o)]+centre(2))

% and box, same area as square
xside = sFWHM;
yside  = sidel*sidel/xside;
ox = xside/2;
oy = yside/2; 
plot([-(ox) -(ox) ox ox -(ox)]+centre(1),...
     [-(oy) oy oy -(oy) -(oy)]+centre(2))
