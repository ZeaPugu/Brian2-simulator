## This code is rewritten based on previous work of
## BRUNEL, Nicolas et WANG, Xiao-Jing.
## "Effects of neuromodulation in a cortical network model of object working memory dominated by recurrent inhibition" 
## Journal of computational neuroscience, 2001, vol. 11, no 1, p. 63-85.
## --------------------------------------
## This Python code executes a number of tasks as follows.
# 1. Initializing two neuron groups 
# 2. Injecting Poisson input stimuli to two neuron groups
# 3. Ploting the membrane potentials of all neurons
## Latest update: September 4th, 2018

from brian2 import *
import visualization as vis
# populations
N = 100
N_E = int(N * 0.8)  # pyramidal neurons
N_I = int(N * 0.2)  # interneurons

# voltage
V_L = -70. * mV
V_thr = -50. * mV
V_reset = -60. * mV
V_E = 0. * mV
V_I = -70. * mV

# membrane capacitance
C_m_E = 0.5 * nF
C_m_I = 0.2 * nF

# membrane leak
g_m_E = 25. * nS
g_m_I = 20. * nS

# refractory period
tau_rp_E = 2. * ms
tau_rp_I = 1. * ms

# external stimuli
rate = 3 * Hz
C_ext = 1000

# synapses
C_E = N_E
C_I = N_I

# AMPA (excitatory)
g_AMPA_ext_E = 2.08 * nS
g_AMPA_rec_E = 0.104 * nS * 800. / N_E
g_AMPA_ext_I = 1.62 * nS
g_AMPA_rec_I = 0.081 * nS * 800. / N_E
tau_AMPA = 2. * ms

# NMDA (excitatory)
g_NMDA_E = 0.327 * nS * 800. / N_E
g_NMDA_I = 0.258 * nS * 800. / N_E
tau_NMDA_rise = 2. * ms
tau_NMDA_decay = 100. * ms
alpha = 0.5 / ms
Mg2 = 1.

# GABAergic (inhibitory)
g_GABA_E = 1.25 * nS * 200. / N_I
g_GABA_I = 0.973 * nS * 200. / N_I
tau_GABA = 10. * ms


# modeling
eqs_E = '''
dv / dt = (- g_m_E * (v - V_L) - I_syn) / C_m_E : volt (unless refractory)

I_syn = I_AMPA_ext + I_AMPA_rec + I_NMDA_rec + I_GABA_rec : amp

I_AMPA_ext = g_AMPA_ext_E * (v - V_E) * s_AMPA_ext : amp
I_AMPA_rec = g_AMPA_rec_E * (v - V_E) * 1 * s_AMPA : amp
ds_AMPA_ext / dt = - s_AMPA_ext / tau_AMPA : 1
ds_AMPA / dt = - s_AMPA / tau_AMPA : 1

I_NMDA_rec = g_NMDA_E * (v - V_E) / (1 + Mg2 * exp(-0.062 * v / mV) / 3.57) * s_NMDA_tot : amp
s_NMDA_tot : 1

I_GABA_rec = g_GABA_E * (v - V_I) * s_GABA : amp
ds_GABA / dt = - s_GABA / tau_GABA : 1
'''

eqs_I = '''
dv / dt = (- g_m_I * (v - V_L) - I_syn) / C_m_I : volt (unless refractory)

I_syn = I_AMPA_ext + I_AMPA_rec + I_NMDA_rec + I_GABA_rec : amp

I_AMPA_ext = g_AMPA_ext_I * (v - V_E) * s_AMPA_ext : amp
I_AMPA_rec = g_AMPA_rec_I * (v - V_E) * 1 * s_AMPA : amp
ds_AMPA_ext / dt = - s_AMPA_ext / tau_AMPA : 1
ds_AMPA / dt = - s_AMPA / tau_AMPA : 1

I_NMDA_rec = g_NMDA_I * (v - V_E) / (1 + Mg2 * exp(-0.062 * v / mV) / 3.57) * s_NMDA_tot : amp
s_NMDA_tot : 1

I_GABA_rec = g_GABA_I * (v - V_I) * s_GABA : amp
ds_GABA / dt = - s_GABA / tau_GABA : 1
'''

P_E = NeuronGroup(N_E, eqs_E, threshold='v > V_thr', reset='v = V_reset', refractory=tau_rp_E, method='euler')
P_E.v = V_L

P_I = NeuronGroup(N_I, eqs_I, threshold='v > V_thr', reset='v = V_reset', refractory=tau_rp_I, method='euler')
P_I.v = V_L

eqs_glut = '''
s_NMDA_tot_post = w * s_NMDA : 1 (summed)
ds_NMDA / dt = - s_NMDA / tau_NMDA_decay + alpha * x * (1 - s_NMDA) : 1 (clock-driven)
dx / dt = - x / tau_NMDA_rise : 1 (clock-driven)
w : 1
'''

eqs_pre_glut = '''
s_AMPA += w
x += 1
'''

eqs_pre_gaba = '''
s_GABA += 1
'''

eqs_pre_ext = '''
s_AMPA_ext += 1
'''

duration = .1*second
## Initialization of neuron connection

# E to E
C_E_E = Synapses(P_E, P_E, model=eqs_glut, on_pre=eqs_pre_glut, method='euler')
C_E_E.connect('i!=j')
C_E_E.w[:] = 1

# E to I 
C_E_I = Synapses(P_E, P_I, model=eqs_glut, on_pre=eqs_pre_glut, method='euler')
C_E_I.connect()
C_E_I.w[:] = 1

# I to E_1
C_I_E = Synapses(P_I, P_E, on_pre=eqs_pre_gaba, method='euler')
C_I_E.connect(p=0.2)

# I to I
C_I_I = Synapses(P_I, P_I, on_pre=eqs_pre_gaba, method='euler')
C_I_I.connect('i != j')

# external noise
C_P_E = PoissonInput(P_E, 's_AMPA_ext', C_ext, rate, '1')
C_P_I = PoissonInput(P_I, 's_AMPA_ext', C_ext, rate, '1')

## Monitoring
E_mon 		= SpikeMonitor(P_E)
I_mon	 	= SpikeMonitor(P_I)

E_sta 		= StateMonitor(P_E,'v',record=True)
I_sta		= StateMonitor(P_I,'v',record=True)

LFP_E = PopulationRateMonitor(P_E)
LFP_I = PopulationRateMonitor(P_I)

# ##############################################################################
# # Simulation run
# ##############################################################################

run(duration)


################################################################################
# Analysis and plotting
################################################################################
figure(1)
subplot(211)
plot(E_mon.t/ms, E_mon.i,'.',c='C1',label='Excitatory synapses group')
xlabel('Time (ms)')
ylabel('Neuron index')
legend()
subplot(212)
plot(I_mon.t/ms, I_mon.i,'.',c='C2',label='Inhibitory synapses group')
xlabel('Time (ms)')
ylabel('Neuron index')
legend()
suptitle('Raster plot neurons')


figure(2)
subplot(211)
for idx in range(N_E):
	plot(E_sta.t/ms, E_sta.v[idx])
xlabel('Time (ms)')
ylabel('Membrane potential (mV)')
subplot(212)
for idx in range(N_I):
	plot(I_sta.t/ms, I_sta.v[idx])
xlabel('Time (ms)')
ylabel('Membrane potential (mV)')
suptitle('Spike traces of excitatory synapses group and inhibitory synapses group')

figure(3)
subplot(211)
plot(LFP_E.t/ms, LFP_E.smooth_rate(window='flat',width=.002*second)/Hz,label='Excitatory synapses group')
xlabel('Time (ms)')
ylabel('Firing rate (Hz)')
legend()
subplot(212)
plot(LFP_I.t/ms, LFP_I.smooth_rate(window='flat',width=.002*second)/Hz,label='Inhibitory synapses neuron')
xlabel('Time (ms)')
ylabel('Firing rate (Hz)')
legend()
show()