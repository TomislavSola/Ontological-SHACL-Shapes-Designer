import timeit
import os
import pickle
from rdflib import Graph
from pyshacl import validate

bundle_dir = os.path.dirname(os.path.abspath(__file__))

#datasets and shapes are varied, the output contains nrOfDatasets x nrOfShapes runtimes
num_datasets = 12
num_shapes = 8

#average runtime is measured over num_runs runs
num_runs = 10

#iteration counter and variables to store interesting information about the performance
ctr = 0
total_execution_time = 0
total_num_violations = 0

#lists to also keep track of the complexity of the datasets/shapes in terms of the number of triples
dataset_sizes = []
shape_sizes = []

#list to store the results as a string
result_messages = []

#list of the relative directories containing the different datasets
dataset_directories = ['ApartmentBuilding_Binary','ApartmentBuilding_Directed1ToN','ApartmentBuilding_DirectedBinary',\
                        'DuplexBuilding_Binary','DuplexBuilding_Directed1ToN','DuplexBuilding_DirectedBinary',\
                        'Garage_Binary','Garage_Directed1ToN','Garage_DirectedBinary',\
                        'OfficeBuilding_Binary','OfficeBuilding_Directed1ToN','OfficeBuilding_DirectedBinary']

plot_dict = dict()

#loop through all datasets
for i in range(num_datasets):
    dataset_directory = bundle_dir+"\\test_datasets\\"+dataset_directories[i]
    inst_graph = Graph()

    for instance_file_path in os.listdir(dataset_directory):
        inst_graph.parse(dataset_directory+"/"+instance_file_path)

    
    #store the size of the dataset for the result table
    dataset_sizes.append(len(inst_graph))

    #loop through all shapes and measure the average execution time over 10 runs
    for j in range(num_shapes):
        
        #increase the counter
        ctr+= 1
  
        shape_file_path = bundle_dir+"\\test_shapes\\"+str(j)+"\\shapes.ttl"

        shapes_graph = Graph().parse(shape_file_path)
        shape_sizes.append(len(shapes_graph))

        _, results_graph, results_text = validate(data_graph= inst_graph,shacl_graph=shapes_graph)

        results_graph.serialize(destination=bundle_dir+"\\test_shapes\\"+str(j) + "\\reports\\report_"+dataset_directories[i]+".ttl",format="turtle")

        try:
            num_violations = results_text.split("\n")[2].split(" (")[1].split(")")[0]
        except(IndexError):
            #this means the dataset conforms to the shapes, such that num_violations must be set to 0
            num_violations = 0

        total_num_violations += int(num_violations)

        duration = timeit.Timer('validate(data_graph= inst_graph,shacl_graph=shapes_graph,)','from pyshacl import validate\nfrom __main__ import inst_graph, shapes_graph').timeit(number = num_runs)

        #the float value of the average runtime is rounded to 3 decimal places
        avg_duration = round(duration/num_runs,3)

        if "_Binary" in dataset_directories[i]:
            plot_dict[int(num_violations)] = avg_duration

        total_execution_time += avg_duration

        print(f'Iteration {ctr} of {num_datasets*num_shapes}')

        result_msg = f'Dataset: {dataset_directories[i]} ({dataset_sizes[i]} statements), shape: {j} ({shape_sizes[j]} statements). Elapsed Time: {avg_duration} seconds. Number of violations:  {num_violations}' 

        #each result message contains the average runtime, the complexities of the dataset and the shape as well as the number of violations
        result_messages.append(result_msg)


#save results as a .txt file, each line contains one result message
with open(bundle_dir+'\\benchmark_results_pyshacl.txt', 'w') as fp:
    fp.write("----------BENCHMARK RESULTS FOR THE PYSHACL PROCESSOR----------\n\n")
    fp.write("----------total average execution time: "+str(round(total_execution_time,3))+" seconds----------\n\n")
    fp.write("----------total number of violations found: "+ str(total_num_violations)+"--------------\n\n")
    fp.write("----------------FOR MORE DETAILS SEE BELOW---------------------\n\n\n")
    fp.write('\n'.join(result_messages))

#save a dictionary {num_violations:avg_duration} for the visualization plot
with open(bundle_dir+"\\plotDictionary.pkl", "wb") as tf:
    pickle.dump(plot_dict,tf)


