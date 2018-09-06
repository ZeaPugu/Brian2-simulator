## This Python code is written based on the example from Brian2 documentation :https://brian2.readthedocs.io/en/stable/index.html
# This network consists of three layers with configurable number of neurons. 
# - The neuron model is LIF. 
# - Network protocol is MLP.
# - Noisy neurons are customized up to your decision
# - All synapses are excitatory ones. 
# - The reserval potential is not manually set.
# - Spiking-Timing-Dependent-Plasticity is applied to update synapses' weights.
# - Firing rate is calculated and showed with fixed time window.
## Latest update: September 4th, 2018
## Editor: Le-Ha Hoang

from brian2 import *
import visualization as vis
start_scope()

### Parameters defined ###
duration	= .1*second
numIn		= 3		# Number of neurons in input layer
numHid		= 5			# Number of neurons in hidden layer
numOut		= 2			# Number of neurons in output layer
vThres		= -50*mvolt	# Threshold voltage of pre-synaptic neurons

pos			= 1				# Forming fully-connected-layer network
sigma		= 5*mvolt		# Adding neural noises
vRest		= -70*mvolt
C_mem		= 0.0005*ufarad

wmax		= 10*mvolt  	# Maximum weight value
taupre 		= taupost = 20*ms
Apre 		= 10*mvolt 
Apost 		= -Apre*taupre/taupost*1.05

ampt		= .01*mamp # A sine wave with fixed amplitude and frequency is applied as an input stimuli
rate		= 100*Hz

##=======================================================
### Setting up one variant of LIF model ### 
# Initializing the neurons
eqs = '''
dv/dt = (vRest-v)/tau + sigma*xi*tau**-0.5: volt
tau : second
'''

# Input layer with explicit input stimuli via a current
G_1 = NeuronGroup(numIn,'''
dv/dt = (vRest-v)/tau + I/C_mem: volt
I = ampt*sin(2*pi*rate*t) : amp
tau : second	
''',
					threshold='v>vThres',
					reset='v = vRest',
					refractory=2*ms,
 method='euler')
G_1.tau= '20*ms'
G_1.v  = 'vRest'

# Hidden layer
G_2 	= NeuronGroup(numHid,
					  eqs,
					  threshold='v>vThres',
					  reset='v = vRest',
					  refractory=2*ms,
					  method='euler')
G_2.tau	= '20*ms'
G_2.v  = 'vRest'

# Output layer
G_3 	= NeuronGroup(numOut,
					  eqs,
					  threshold='v>vThres',
					  reset='v = vRest',
					  refractory=2*ms,
					  method='euler')
G_3.tau	= '20*ms'
G_3.v  = 'vRest'

##=======================================================
# Synaptic's weights are updated by Spike-Timing-Dependent-Plasticity learning rule

eqs_stdp ='''
	w : volt
	dapre/dt = -apre/taupre : volt (event-driven)
	dapost/dt = -apost/taupost : volt (event-driven)
'''

eqs_on_pre ='''
	v_post += w
	apre += Apre
	w = clip(w+apost, 0, wmax)
'''

eqs_on_post  ='''
	apost += Apost
	w = clip(w+apre, 0, wmax)
'''

## Synapses defined between layers =================

S_1	= Synapses(G_1, G_2, 
				model = eqs_stdp,
				on_pre = eqs_on_pre,
				on_post = eqs_on_post,
				method='linear')
S_1.connect(p=pos)
S_1.w='rand()*wmax'

S_2	= Synapses(G_2, G_3, 
				model = eqs_stdp,
				on_pre = eqs_on_pre,
				on_post = eqs_on_post,
				method='linear')
S_2.connect(p=pos)
S_2.w='rand()*wmax'

##=======================================================

## Monitoring =====================================

Input_mon 		= StateMonitor (G_1, ['v', 'I'], record=True)
Hidden_mon		= StateMonitor (G_2, 'v', record=True)
Output_mon 		= StateMonitor (G_3, 'v', record=True)

Input_spk		= SpikeMonitor (G_1, 'i', record=True)
Hidden_spk		= SpikeMonitor (G_2, 'i', record=True)
Output_spk		= SpikeMonitor (G_3, 'i', record=True)

In_hid_weights	= StateMonitor (S_1,'w',record=True)
Hid_out_weights = StateMonitor (S_2,'w',record=True)

LFP_1 = PopulationRateMonitor(G_1)
LFP_2 = PopulationRateMonitor(G_2)
LFP_3 = PopulationRateMonitor(G_3)

##=======================================================
run(duration)# Run simulation
##=======================================================

##=======================================================
## Make plot
##=======================================================


figure(1) ## Plotting Membrane potentials of input and hidden layers
subplot(211)
for idx in range(numIn):
	plot(Input_mon.t/ms, Input_mon.v[idx])
xlabel('Time (ms)')
ylabel('Input layer')

subplot(212)
for idx in range(numHid):
	plot(Hidden_mon.t/ms, Hidden_mon.v[idx])
xlabel('Time (ms)')
ylabel('Hidden layer')
suptitle('Spike traces of Input layer and Hidden layer')


figure(2) ## Plotting Membrane potentials of output and hidden layers
subplot(211)
for idx in range(numHid):
	plot(Hidden_mon.t/ms, Hidden_mon.v[idx])
xlabel('Time (ms)')
ylabel('Hidden layer')
subplot(212)
for idx in range(numOut):
	plot(Output_mon.t/ms, Output_mon.v[idx])
xlabel('Time (ms)')
ylabel('Output layer')
suptitle('Output layer')
suptitle('Spike traces of Hidden layer and output layer')


figure(4) ## Plotting the raster plot of layers and firing rate
subplot(211) ## Raster plot of input layer
plot(Input_spk.t/ms, Input_spk.i,'.',c='C1',label='Input layer')
xlabel('Time (ms)')
ylabel('Neuron index')
legend()
subplot(212)
plot(LFP_1.t/ms, LFP_3.smooth_rate(window='flat',width=.002*second)/Hz,label='Input layer')
xlabel('Time (ms)')
ylabel('Firing rate (Hz)')
legend()
suptitle('Input layer')

figure(5)
subplot(211)
plot(Hidden_spk.t/ms, Hidden_spk.i,'.',c='C2',label='Hidden layer')
xlabel('Time (ms)')
ylabel('Neuron index')
legend()
subplot(212)
plot(LFP_2.t/ms, LFP_2.smooth_rate(window='flat',width=.002*second)/Hz,label='Hidden layer')
xlabel('Time (ms)')
ylabel('Firing rate (Hz)')
legend()
suptitle('Hidden layer')

figure(6)
subplot(211)
plot(Output_spk.t/ms, Output_spk.i,'.',c='C1',label='Output layer')
xlabel('Time (ms)')
ylabel('Neuron index')
legend()
subplot(212)
plot(LFP_3.t/ms, LFP_2.smooth_rate(window='flat',width=.002*second)/Hz,label='Hidden layer')
xlabel('Time (ms)')
ylabel('Firing rate (Hz)')
legend()
suptitle('Output layer')


figure(7)
subplot(211)
plot(LFP_2.t/ms, LFP_2.smooth_rate(window='gaussian',width=.01*second)/Hz,label='Hidden layer')
legend()
subplot(212)
plot(LFP_3.t/ms, LFP_3.smooth_rate(window='flat',width=.01*second)/Hz,label='Output layer')
legend()
suptitle('Population rate monitor')


figure(8)### Visualization of weight update at synaptics between input layer and hidden layer
subplot(121)
for idx in range(numIn*numHid):
	plot(In_hid_weights.t/ms,In_hid_weights.w[idx])
xlabel('Time (ms)')
ylabel('Input- Hidden Weights ')
suptitle('Weight update between input layer and hidden layer')

subplot(122)
for idx in range(numHid*numOut):
	plot(Hid_out_weights.t/ms,Hid_out_weights.w[idx])
xlabel('Time (ms)')
ylabel('Hidden- Output Weights ')
suptitle('Weight update between output layer and hidden layer')

show() # End of the show

















