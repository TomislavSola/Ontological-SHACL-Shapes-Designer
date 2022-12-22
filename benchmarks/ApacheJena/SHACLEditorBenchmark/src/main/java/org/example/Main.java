package org.example;

import java.io.File;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.jena.graph.Graph;
import org.apache.jena.riot.Lang;
import org.apache.jena.riot.RDFDataMgr;
import org.apache.jena.shacl.ShaclValidator;
import org.apache.jena.shacl.Shapes;
import org.apache.jena.shacl.ValidationReport;
import org.apache.log4j.Logger;
import org.apache.log4j.BasicConfigurator;

import com.github.underscore.U;

public class Main {

    static Logger logger = Logger.getLogger(Main.class);

    public static void main(String[] args) throws IOException {

        BasicConfigurator.configure();

        String SHAPES_DIR = System.getProperty("user.dir")+"\\src\\main\\resources\\test_shapes\\";
        String DATA_DIR = System.getProperty("user.dir")+"\\src\\main\\resources\\test_datasets\\";


        int num_shapes = 8;
        int num_runs = 10;

        double total_execution_time = 0;
        int total_num_violations = 0;

        DecimalFormat df = new DecimalFormat("#.###");

        List<String> dataset_directories = List.of("ApartmentBuilding_Binary","ApartmentBuilding_Directed1ToN",
                "ApartmentBuilding_DirectedBinary","DuplexBuilding_Binary","DuplexBuilding_Directed1ToN",
                "DuplexBuilding_DirectedBinary","Garage_Binary","Garage_Directed1ToN","Garage_DirectedBinary",
                "OfficeBuilding_Binary","OfficeBuilding_Directed1ToN","OfficeBuilding_DirectedBinary");

        List<String> result_lines = new ArrayList<String>();

        File output = new File(System.getProperty("user.dir")+"\\src\\main\\resources\\benchmark_results_java.txt");
        FileWriter writer = new FileWriter(output);

        Map plotDict = new HashMap();

        for(String dataset : dataset_directories){

            String filename = "";

            if (dataset.contains("_Binary")) {
                filename = "dataset-binary.ttl";
            }
            if (dataset.contains("_Directed1ToN")) {
                filename = "dataset-directed1ton.ttl";
            }
            if (dataset.contains("_DirectedBinary")) {
                filename = "dataset-directedbinary.ttl";
            }

            Graph dataGraph = RDFDataMgr.loadGraph(DATA_DIR+dataset+"\\"+filename);

            for(int i =0; i<num_shapes; i++) {

                Graph shapesGraph = RDFDataMgr.loadGraph(SHAPES_DIR+i+"\\"+"shapes.ttl");

                Shapes shapes = Shapes.parse(shapesGraph);

                ValidationReport report = ShaclValidator.get().validate(shapes, dataGraph);

                int num_violations = report.getEntries().size();
                Graph results_graph = report.getGraph();

                total_num_violations += num_violations;

                File report_file = new File(SHAPES_DIR+i+"\\reports\\report_"+dataset+".ttl");
                FileOutputStream report_stream = new FileOutputStream(report_file);
                RDFDataMgr.write(report_stream,results_graph,Lang.TURTLE);
                report_stream.close();

                //the average execution time over 10 runs is measured
                long startTime = System.nanoTime();
                for (int j =0; j<num_runs; j++){
                    ValidationReport tmp_report = ShaclValidator.get().validate(shapes, dataGraph);
                }
                long stopTime = System.nanoTime();

                long elapsedTime = (stopTime - startTime)/num_runs;

                if (!plotDict.containsKey(num_violations) && dataset.contains("_Binary"))
                {
                    plotDict.put(num_violations, df.format(elapsedTime/1e9));
                }

                total_execution_time += elapsedTime;

                String result_msg = "Dataset: "+dataset+", shape: "+i+". Elapsed Time: "+df.format(elapsedTime/1e9)+
                        " seconds. Number of violations: "+num_violations+"\n";

                result_lines.add(result_msg);

            }
        }

        writer.write("------------BENCHMARK RESULTS FOR THE APACHE JENA PROCESSOR------------\n\n");
        writer.write("------------total average execution time: "+df.format(total_execution_time/1e9)+" seconds------------\n\n");
        writer.write("------------total number of violations found: "+ total_num_violations+"----------------\n\n");
        writer.write("------------------FOR MORE DETAILS SEE BELOW-----------------------\n\n\n");

        for (String line : result_lines)
        {
            writer.write(line);
        }

        writer.flush();
        writer.close();

        Graph testGraph = RDFDataMgr.loadGraph(DATA_DIR+ "ApartmentBuilding_Binary" + "\\" + "dataset-binary.ttl");

        Graph astrea_graph = RDFDataMgr.loadGraph(SHAPES_DIR + "\\astrea-shapes.ttl");

        Shapes astrea_shapes = Shapes.parse(astrea_graph);

        ValidationReport astreaReport = ShaclValidator.get().validate(astrea_shapes,testGraph);

        Graph astreaReportGraph = astreaReport.getGraph();

        File astrea_report_file = new File(SHAPES_DIR+ "\\astrea-report.ttl");
        FileOutputStream astrea_report_stream = new FileOutputStream(astrea_report_file);
        RDFDataMgr.write(astrea_report_stream,astreaReportGraph,Lang.TURTLE);
        astrea_report_stream.close();

        System.out.println(U.toJson(plotDict));


    }
}