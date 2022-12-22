using VDS.RDF;
using VDS.RDF.Parsing;
using VDS.RDF.Writing;
using VDS.RDF.Shacl;
using VDS.RDF.Shacl.Validation;
using System.Data;
using Newtonsoft.Json;

namespace SHACLEditorBenchmarking
{
    class Program
    {
        static void Main(string[] args)
        {

            string SHAPES_DIR = System.IO.Directory.GetCurrentDirectory() + "\\test_shapes\\";
            string DATA_DIR = System.IO.Directory.GetCurrentDirectory() + "\\test_datasets\\";

            int num_shapes = 8;
            int num_runs = 10;

            double total_execution_time = 0;
            int total_num_violations = 0;

            List<String> dataset_directories = new List<string>() {"ApartmentBuilding_Binary", "ApartmentBuilding_Directed1ToN",
                "ApartmentBuilding_DirectedBinary", "DuplexBuilding_Binary", "DuplexBuilding_Directed1ToN",
                "DuplexBuilding_DirectedBinary", "Garage_Binary", "Garage_Directed1ToN", "Garage_DirectedBinary",
                "OfficeBuilding_Binary", "OfficeBuilding_Directed1ToN", "OfficeBuilding_DirectedBinary" };

            List<String> result_lines = new List<string>();

            IDictionary<int, double> plotDict = new Dictionary<int, double>();

            foreach (String dataset in dataset_directories)
            {

                String filename = "";

                if (dataset.Contains("_Binary"))
                {
                    filename = "dataset-binary.ttl";
                }
                if (dataset.Contains("_Directed1ToN"))
                {
                    filename = "dataset-directed1ton.ttl";
                }
                if (dataset.Contains("_DirectedBinary"))
                {
                    filename = "dataset-directedbinary.ttl";
                }

                IGraph dataGraph = new Graph();

                FileLoader.Load(dataGraph, DATA_DIR + dataset + "\\" + filename);

                for (int i = 0; i < num_shapes; i++)
                {

                    IGraph shapesGraph = new Graph();

                    FileLoader.Load(shapesGraph, SHAPES_DIR + i + "\\" + "shapes.ttl");

                    ShapesGraph shapes = new ShapesGraph(shapesGraph);

                    Report validationReport = shapes.Validate(dataGraph);

                    CompressingTurtleWriter compressingTurtleWriter = new CompressingTurtleWriter();

                    IGraph reportGraph = validationReport.Normalised;
                    int num_violations = validationReport.Results.Count;

                    total_num_violations += num_violations;

                    compressingTurtleWriter.Save(reportGraph, SHAPES_DIR + i + "\\" + "\\reports\\report_"+dataset+".ttl");

                    var watch = System.Diagnostics.Stopwatch.StartNew();
                    for (int j = 0; j < num_runs; j++)
                    {
                        Report tmp_report = shapes.Validate(dataGraph);
                    }
                    watch.Stop();

                    var elapsedTime = Math.Round((watch.Elapsed.TotalSeconds/num_runs), 3);

                    if (!plotDict.ContainsKey(num_violations) && dataset.Contains("_Binary"))
                    {
                        plotDict.Add(num_violations, elapsedTime);
                    }

                    total_execution_time += elapsedTime;

                    String result_msg = "Dataset: " + dataset + ", shape: " + i + ". Elapsed Time: " + elapsedTime +
                        " seconds. Number of violations: " + num_violations;

                    Console.WriteLine(result_msg);

                    //append the result msg to the result list
                    result_lines.Add(result_msg);

                }
            }

            try
            {
                using (StreamWriter result_file = new StreamWriter(System.IO.Directory.GetCurrentDirectory() + "\\benchmark_result\\benchmark_results_dotnet.txt"))
                {
                    result_file.WriteLine("-----------BENCHMARK RESULTS FOR THE DOTNETRDF PROCESSOR-----------\n");
                    result_file.WriteLine("-----------total average execution time: " + Math.Round(total_execution_time, 3) + " seconds-----------\n");
                    result_file.WriteLine("-----------total number of violations found: " + total_num_violations + "---------------\n");
                    result_file.WriteLine("-----------------FOR MORE DETAILS SEE BELOW----------------------\n\n");

                    foreach (string line in result_lines)
                    {
                        result_file.WriteLine(line);
                    }
                }
                Console.WriteLine("Lines written to file successfully.");
            }
            catch (Exception err)
            {
                Console.WriteLine(err.Message);
            }

            //test for astrea compatibility was positive, report could be generated without preprocessing
            //astrea-shapes.ttl was obtained by uploading the merged ontology file ontology_graph.ttl to:
            // https://astrea.linkeddata.es/

            IGraph testGraph = new Graph();

            FileLoader.Load(testGraph, DATA_DIR + "ApartmentBuilding_Binary" + "\\" + "dataset-binary.ttl");

            IGraph astrea_graph = new Graph();

            FileLoader.Load(astrea_graph, SHAPES_DIR + "\\astrea-shapes.ttl");

            ShapesGraph astrea_shapes = new ShapesGraph(astrea_graph);

            Report astreaReport = astrea_shapes.Validate(testGraph);

            CompressingTurtleWriter writer = new CompressingTurtleWriter();

            IGraph astreaReportGraph = astreaReport.Normalised;

            writer.Save(astreaReportGraph, SHAPES_DIR + "\\astrea-report.ttl");

            string plot_str = JsonConvert.SerializeObject(plotDict);

            Console.WriteLine(plot_str);

        }
    }
}
