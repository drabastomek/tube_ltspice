TubeName = '6HV5A';
Source = 'GE Datasheet 6HV5-A Frank Phillips page';
axset = [0 5000 0 .4];  MU = 300;
VGP = 0:-2:-10;  Vpmax = 5000; VCT = 0.5;
RGI = 2000; CCG='22P'; CGP='1.8P'; CCP='11P';
Vp =    [500  1000 2000  1000  2000 3000 2500 3800  4600  4000 5000];
Vg =    [0    0    0     -2    -2   -2   -6   -6    -6    -10  -10 ];
Idata = [0.05 0.12 0.28 0.025 0.16 0.345 0.05 0.245 0.395 0.072 0.2];
