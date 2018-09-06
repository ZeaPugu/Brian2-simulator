=======================================
This is a quick manual on how to use Brian Simulator to observe behaviors of Spiking Neural Networks (SNNs).
This tutorial consists of a step-by-step procedure for a beginner to explore Brian Simulator. I strongly believe that this is time-saving for beginners.
Last but not least, the reader is referred to the Brian 2 documentation from https://brian2.readthedocs.io/en/stable/# for any further details.
Latest update: September 6th, 2018
Editor: Le-Ha Hoang
=======================================
### Step 1:Import all libaries from Brian 2.

### Step 2: Defining parameters of SNNs
	- Neuron models: Threshold voltage, number of neurons per layer,...
	- Input stimuli: Poisson Input or explicit input,...
	- Duration of simulation

### Step 3: Defining neuron groups by using command(s):
	- group1 = NeuronGroup(...)

### Step 4: Defining synapse models by using command(s):
	- connection1 = Synapses(....)

### Step 5: Runing the simultion by this command run(time of simulation-milisecond or second)

### Step 6: Keeping track of any changes with time from membrane potentials, firing rate, or firing moment (raster plot) by using the command(s):
- Input_mon 		= StateMonitor (G_1, ['v', 'I'], record=True) # track changes of membrane potentials or currents
- Hid_out_weights   = StateMonitor (S_2,'w',record=True) # track changes of weights
- Input_spk			= SpikeMonitor (G_1, 'i', record=True) # track changes of neuron firing moments
- LFP_1 			= PopulationRateMonitor(G_1) # track changes of firing rate

### Step 7: Visualizing the memebrane potentials, raster plots, firing rate, synapses connection and more by using this command(s):
- plot
- subplot
- ....

### Step 8: Remmeber to include this command to show the simulation results: show()
