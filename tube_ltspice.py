import numpy as np
import scipy.optimize
import matplotlib.pyplot as plt
import click

## Koren's model for tubes
# global defaults
RGI=2000 
CCG='22P'
CGP='1.8P' 
CCP='11P'
VCT = 0.0
Vs = []
Vsi = Vs
KP = 800
EX = 1.35
KVB = 7
kvbb = KVB

KG1 = 1000
KGX = np.power(KG1, (1.0 / EX))

# model parameters
tube_name = None
tube_source = None
Vp = None
Vg = None
Idata = None
MU = None
VGP = None
axset = None
Vpmax = None

# https://numpy.org/doc/stable/user/numpy-for-matlab-users.html
def tube_current(x0, Vp = Vp, Vg = Vg):
    _mu = MU * x0[0]
    _exx = EX * x0[1]
    _kg1 = KGX * x0[2]
    _kp = KP * x0[3]


    if (len(x0) >= 5 and (max(Vg) + VCT) > np.spacing(1)):  
        _kvbb = KVB * np.power(x0[4], 2)
    else:
        _kvbb = KVB

    
    EL_Voltage = Vp / (KP * x0[3])      # (Ep / kp)
    EL_Exp = np.exp(
        _kp * 
        (
            (1 / _mu) + 
            (Vg + VCT) / np.sqrt(
                _kvbb + np.power(Vp, 2)
            )
        )
    )
    
    EL_Log = np.log(1 + EL_Exp)
    
    E1 =  EL_Voltage * EL_Log
    y = np.power(E1 / _kg1, _exx) * (1 + np.sign(E1));
    
    return y

def read_tube_data(tube):
    with open(f'{tube}.m', 'r') as f:
        tube_txt = f.read()

    tube_data = {}

    tube_txt = tube_txt.split('\n')
    tube_data['tube_name'] = tube_txt[0].split('=')[-1].replace('\'', '').replace(';', '').strip()
    tube_data['tube_source'] = tube_txt[1].split('=')[-1].replace('\'', '').replace(';', '').strip()

    for tube_txt_el in tube_txt[2:]:
        for el in tube_txt_el.split(';'):
            vars = el.strip().split('=')
            
            if len(vars) == 2:
                var_name = vars[0].strip()
                var_value = vars[1].strip()
                
                if ':' in var_value:
                    rng = var_value.split(':')
                    var_value = np.arange(float(rng[0]),float(rng[2]) + float(rng[1]),float(rng[1]))
                elif '[' in var_value:
                    arr = [float(e) for e in var_value[1:-1].split(' ') if e != '']
                    var_value = arr
                else:
                    try:
                        var_value = float(var_value)
                    except ValueError:
                        var_value = var_value
                
                tube_data[var_name] = var_value           

    # post processing
    tube_data['Vp'] = np.array(tube_data['Vp'])
    tube_data['Vg'] = np.array(tube_data['Vg'])
    tube_data['Idata'] = np.array(tube_data['Idata'])

    return tube_data

def unpack_tube_data(tube_data):
    global tube_name, VCT
    global tube_source
    global Vp
    global Vg
    global Idata
    global MU
    global VGP
    global axset
    global Vpmax

    if 'tube_name' in tube_data:
        tube_name = tube_data['tube_name']
    
    if 'tube_source' in tube_data:
        tube_source = tube_data['tube_source']

    if 'Vp' in tube_data:
        Vp = tube_data['Vp']

    if 'Vg' in tube_data:
        Vg = tube_data['Vg']
    
    if 'Idata' in tube_data:
        Idata = tube_data['Idata']
    
    if 'MU' in tube_data:
        MU = tube_data['MU']

    if 'VGP' in tube_data:
        VGP = tube_data['VGP']

    if 'axset' in tube_data:
        axset = tube_data['axset']
    
    if 'Vpmax' in tube_data:
        Vpmax = tube_data['Vpmax']

    if 'VCT' in tube_data:
        VCT = tube_data['VCT']

    

def optimize_model():
    opt = lambda x: np.linalg.norm((tube_current(x, Vp, Vg) - Idata) * np.log(Idata) / Idata) # L2-Norm
    xopt = scipy.optimize.fmin(func=opt, x0=np.ones(5), maxiter=5000, ftol=1e-9, full_output=True, disp=True)

    return xopt

def generate_plot(xopt):
    Vp_plot = []
    Vg_plot = []
    Vi_plot = []

    for Vg_ind in VGP:
        Vpp = np.arange(0, Vpmax + 10, 10)
        Vgg = np.array([Vg_ind] * len(Vpp))
        Vii = np.array(tube_current(xopt[0], Vpp, Vgg))

        Vp_plot.append(Vpp)
        Vg_plot.append(Vg_ind)
        Vi_plot.append(Vii)

    param_names = ['MU', 'EX', 'KG1', 'KP', 'KVB']
    param_vals = list(xopt[0] * np.array([MU, EX, KG1, KP, KVB]))
    param_txt = []

    for p_nm, p_val in zip(param_names, param_vals):
        param_txt.append(f'{p_nm}={p_val:.3f}')
    param_plot = '\n'.join(param_txt)

    fig = plt.figure(figsize=(12,9))

    for i, vgp in enumerate(Vg_plot):
        plt.plot(Vp_plot[i], Vi_plot[i], label=f'{vgp}V')

    plt.plot(Vp, Idata, 'ro')
    plt.title(f'{tube_name}\n{tube_source}')
    plt.legend(loc='lower right')
    lims = plt.axis()
    plt.text(0, lims[-1] * .75 , param_plot)
    plt.savefig(f'{tube_name}_fit_plot.png', dpi=300)

    return param_txt

def output_model(param_txt):
    model = f'''.subckt {tube_name} A G K
* {tube_source}
XV1 A G K Triode
+params: {' '.join(param_txt)} VCT={VCT} RGI={RGI} CCG={CCG}  CGP={CGP} CCP={CCP}
.ends
    '''

    with open(f'{tube_name}.model', 'w') as f:
        f.write(model)

@click.command()
@click.option('--tube_filename', default='12AX7ASYL', help="Specify the name of the tube")
def produce_model(tube_filename):
    tube_data = read_tube_data(tube_filename)
    unpack_tube_data(tube_data)

    xopt = optimize_model()
    param_txt = generate_plot(xopt)
    output_model(param_txt)

if __name__ == '__main__':
    produce_model()
