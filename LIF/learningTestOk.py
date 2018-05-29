# Show time!!!

from brian2 import *
start_scope()

### Parameters defined ###
numPre		=3 		# Number of pre-synaptic neurons
numPos		=3 		# Number of post-synaptic neurons
vRestPre	=0.4	# Threshold voltage of pre-synaptic neurons
vRestPos	=0.5	# Threshold voltage of post-synaptic neurons
run_time	=0.1*second
pos			=1		# Forming fully-connected-layer network
sigma		=0.05	# Adding neural noises


wmax=0.5
taupre = taupost = 20*ms
Apre = 0.01
Apost = -Apre*taupre/taupost*1.05
### Setting up one variant of LIF model ### 
eqs = '''
dv/dt = (I-v)/tau + sigma*xi*tau**-0.5: 1
I : 1
tau : second
'''

### Input current and mebrane voltage are randomnized in [0,1]
### Time constant is calculated through random function
### Initializing the architecture of pre-synaptic neurons

G_1 = NeuronGroup(numPre, eqs, threshold='v>vRestPre', reset='v = 0',refractory=0.5*ms, method='euler')
G_1.I  ='rand()'
G_1.tau= '30*rand()*ms'
G_1.v  = 'rand()'

#### Initializing the architecture of post-synaptic neurons
G_2 	= NeuronGroup(numPos, eqs, threshold='v>vRestPos', reset='v = 0',refractory=0.5*ms, method='euler')
G_2.I	='rand()'
G_2.tau	= '50*rand()*ms'
G_2.v	= 'rand()'


### Connecting the pre-synapse neurons to post-synapse neurons
### Synapse's weight is pre-defined by a simple equation
### Spike-Timing-Dependent-Plasticity has not been applied yet in this scenario
'''
S 		= Synapses(G_1, G_2, 'w:1',on_pre='v_post += w') 
S.connect(p=pos)
S.w		='j*0.1+0.05' # j is the index of the post-synaptic neuron starting from 0
'''
### Spike-Timing-Dependent-Plasticity has been applied in this scenario
S 		= Synapses(G_1, G_2,
'''
w : 1
dapre/dt = -apre/taupre : 1 (event-driven)
dapost/dt = -apost/taupost : 1 (event-driven)
''',
on_pre='''
v_post += w
apre += Apre
w = clip(w+apost, 0, wmax)
''',
on_post='''
apost += Apost
w = clip(w+apre, 0, wmax)
''', method='linear')
S.connect(p=pos)
S.w='rand()*wmax'


### Start simulating behavior of neurons
M_1 		= StateMonitor (G_1, 'v', record=True)
M_2 		= StateMonitor (G_2, 'v', record=True)
spikes_1 	= SpikeMonitor (G_1,'i',record= True)
spikes_2 	= SpikeMonitor (G_2,'i',record= True)
weight		= StateMonitor (S,'w',record=True)
run(run_time)

### Visualizing the membrane traces (membrane potential) of each neuron
### Top figure shows traces of Pre-synaptic neurons
### Bottom figure shows traces of Post-synaptic neurons

figure(1)
subplot(211)
for idx in range(numPre):
	plot(M_1.t/ms, M_1.v[idx], label='Neuron '+str(idx))
axhline(vRestPre, ls='-',c='C1', lw=0.5, label='Threshold')
xlabel('Time (ms)')
ylabel('Pre-synaptic traces')
legend()
subplot(212)
for idx in range(numPos):
	plot(M_2.t/ms, M_2.v[idx], label='Neuron '+str(idx))
axhline(vRestPos, ls='-',c='C2', lw=0.5,label='Threshold')
xlabel('Time (ms)')
ylabel('Post-synaptic traces')
legend()
suptitle('Spike traces')


### Visualizing the connection by using def keyword ###

def visualise_connectivity(S):
	Ns = len(S.source)
	Nt = len(S.target)
	figure(2)
	#subplot(121)
	plot(zeros(Ns), arange(Ns), 'ok', ms=10)
	plot(ones(Nt), arange(Nt), 'ok', ms=10)
	for i, j in zip(S.i, S.j):
		plot([0, 1], [i, j], '-k')
	xticks([0, 1], ['Source', 'Target'])
	ylabel('Neuron index')
	xlim(-0.1, 1.1)
	ylim(-1, max(Ns, Nt))
'''	
	subplot(122)
	plot(S.i, S.j, 'ok')
	xlim(-1, Ns)
	ylim(-1, Nt)
	xlabel('Source neuron index')
	ylabel('Target neuron index')
'''
visualise_connectivity(S)
suptitle('Feed-forward Spiking Neural Networks')


### Visualization of output spikes ###
figure(3)
subplot(211)
plot(spikes_1.t/ms, spikes_1.i,'x',label='Pre-synaptic neurons')
xlabel('Time (ms)')
ylabel('Neuron index')
legend()
subplot(212)
plot(spikes_2.t/ms, spikes_2.i,'o',label='Post-synaptic neurons')
xlabel('Time (ms)')
ylabel('Neuron index')
legend()
suptitle('Output spikes over the time course')


figure(4)
for idx in range(numPre*numPos):
	plot(weight.t/ms,weight.w[idx],label='weight '+str(idx))
xlabel('Time (ms)')
ylabel('weights change')
legend()

show() # End of the show


# Connecting the post synapses with pre synapses
# Synapse's weight is defined by a simple equation















