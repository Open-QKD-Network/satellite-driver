import csv

class DataCollector:
	# -------- CSV FORMAT --------
	# [time_stamp, delay, key_length]

	def get_bristol_sim_release_data(self):
		sim_data = []
		with open('./Sim_Data/BristolPassKey.csv') as sim_data_file:
			reader = csv.reader(sim_data_file);
			for row in reader:
				sim_data.append(row)
		return sim_data;

	def get_ottawa_sim_release_data(self):
		sim_data = []
		with open('./Sim_Data/OttawaPassKey.csv') as sim_data_file:
			reader = csv.reader(sim_data_file);
			for row in reader:
				sim_data.append(row)
		return sim_data;

	def get_named_sim_release_data(self, name):
		sim_data = []
		with open(name) as sim_data_file:
			reader = csv.reader(sim_data_file);
			for row in reader:
				sim_data.append(row)
		return sim_data;