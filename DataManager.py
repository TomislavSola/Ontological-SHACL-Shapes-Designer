from rdflib import Graph
import os

class DataManager():
    '''Class that manages the parsing and querying of the RDF graphs'''
    def __init__(self):
        #empty graphs for the merged ontologies and instances
        self.ont_graph = Graph()
        self.inst_graph = Graph()
        self.shapes_graph = Graph()
    def parse_ontologies(self, ont_path):
        self.ont_graph.parse(ont_path)
    def parse_instances(self, inst_path):
        self.inst_graph.parse(inst_path)
    def parse_shapes(self, shapes_path):
        self.shapes_graph.parse(shapes_path)
    def getQueryString(self, queryType,mode):
        bundle_dir = os.path.dirname(os.path.abspath(__file__))
        query_file = open(bundle_dir+"\\"+mode+"_queries\\"+str(queryType)+"_query.rq","r")
        query = query_file.read()
        query_file.close()
        return query
