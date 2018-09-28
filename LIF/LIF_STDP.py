## This Python code is written based on the example from Brian2 documentation :https://brian2.readthedocs.io/en/stable/index.html
# This network consists of three layers with configurable number of neurons. 
# - The neuron model is LIF. 
# - Network protocol is Fully-connected fashion.
# - Noisy neurons are customized up to your decision
# - All synapses are excitatory ones. 
# - The reserval potential is not manually set.
# - Spiking-Timing-Dependent-Plasticity is applied to update synapses' weights.
# - Firing rate is calculated and showed with fixed time window.
## Latest update: September 28th, 2018
## Editor: Le-Ha Hoang

from brian2 import *
import visualization as vis
start_scope()
##==================================================================================================
###================== Network parameters configuration =============================================
##==================================================================================================
numIn		= 1					# Number of neurons in input layer
numHid		= 2					# Number of neurons in hidden layer
numOut		= 3					# Number of neurons in output layer
vThres		= -50*mvolt			# Threshold voltage of the neuron 
vRest		= -70*mvolt			# Resting potential of the neuron
C_mem		= 0.0005*ufarad 	# Membrane capacitance of the neuron

wmax		= 10*mvolt  		# Maximum weight value. This unit 'mvolt' aims to compile with the unit of 
								# variable 'v' in the equation that defines neuron model
taupre 		= taupost = 20*ms 	# Time constant of synapses
Apre 		= 10*mvolt 		  	#
Apost 		= -Apre*taupre/taupost*1.05 #

###============== Other declarations===================================================
#======================================================================================
pos			= 1					# Possible number of links between neurons, pos falls in [0,1]
duration	= .1*second			# Simulation time

###============== Let's make some noise==========================================
#=================================================================================
sigma		= 5*mvolt			# Inserting neural noises

###============== Input stimuli===================================================
#=================================================================================
# Sine wave input stimuli
ampt		= .01*mamp 			# A sine wave with fixed amplitude and frequency is applied as an input stimuli
rate		= 100*Hz			# The frequency of sine wave

# Poisson input spikes



##==============================================================================
# Creating groups of Leaky Integrate-and-Fire neurons===========================
##==============================================================================
eqs = '''
dv/dt = (vRest-v)/tau + sigma*xi*tau**-0.5: volt
tau : second
'''
## A model is defined by systems of differential equations.
eqs_sineWave ='''
dv/dt = (vRest-v)/tau + I/C_mem: volt
I = ampt*sin(2*pi*rate*t) : amp
tau : second
'''
# Input layer with explicit input stimuli via a current
G_1 	= NeuronGroup(numIn,
					eqs_sineWave,	
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
G_2.v  	= 'vRest'

# Output layer
G_3 	= NeuronGroup(numOut,
					  eqs,
					  threshold='v>vThres',
					  reset='v = vRest',
					  refractory=2*ms,
					  method='euler')
G_3.tau	= '20*ms'
G_3.v  	= 'vRest'

##====================================================================================
# Synaptic's weights are updated by Spike-Timing-Dependent-Plasticity learning rule===
##====================================================================================
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

##===================================================================================
##======= Creating synapses between neurons of different layers =====================
## ==================================================================================
S_1	= Synapses(G_1, G_2, 
				model = eqs_stdp,
				on_pre = eqs_on_pre,
				on_post = eqs_on_post,
				method='linear')
S_1.connect(p=pos)	# Assign the number of links; The links is proportional to 'pos' which is in the range of [0,1]
S_1.w='rand()*wmax' # Assign the weights of synapses

S_2	= Synapses(G_2, G_3, 
				model = eqs_stdp,
				on_pre = eqs_on_pre,
				on_post = eqs_on_post,
				method='linear')
S_2.connect(p=pos)
S_2.w='rand()*wmax'

##=====================================================================================
##============= Monitoring ============================================================
##=====================================================================================


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

##=====================Run simulation================================================
run(duration)
##===================================================================================

##===================================================================================
##===== Visualization and monitoring of the simulation outcome=======================
##===================================================================================

## Plotting Membrane potentials over the time course of input and hidden layers
figure(1) 
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

## Plotting Membrane potentials over the time course of output and hidden layers
figure(2) 
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

## Plotting the raster plot of layers and firing rate 
## Firing rate is configured with two different 
figure(4) 
subplot(211) ## Raster plot of input layer
plot(Input_spk.t/ms, Input_spk.i,'.',c='C1',label='Input layer')
xlabel('Time (ms)')
ylabel('Neuron index')
legend()
subplot(212)
plot(LFP_1.t/ms, LFP_3.smooth_rate(window='flat',width=.002*second)/Hz,label='Input layer') ## Visualizing the firing rate
xlabel('Time (ms)')
ylabel('Firing rate (Hz)')
legend()
suptitle('Input layer')

figure(5)## The hidden layer
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

##==================================================================================================
##==================================================================================================
##==================================================================================================
# And now, the end is near
# And so I face the final curtain
# My friend, I'll say it clear
# I'll state my case, of which I'm certain ["My way" performed by Frank Sinatra]












