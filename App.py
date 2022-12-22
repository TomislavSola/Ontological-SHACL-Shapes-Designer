import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter.messagebox import askyesno
import re
import os
import json
from ttkwidgets.autocomplete import AutocompleteCombobox
from tkinter.filedialog import asksaveasfile
from tkinter.filedialog import askdirectory
from rdflib import Graph
from pyshacl import validate
import webbrowser
from rdflib.exceptions import ParserError
from json.decoder import JSONDecodeError
from rdflib import URIRef, RDFS, RDF, Literal
from DataManager import DataManager
from FunctionManager import FunctionManager
from textwrap import dedent


class App(tk.Tk):
    def __init__(self):
        
        super().__init__()

        #initialize class attributes
        self.name = "Root"
        self.master = None 
        self.dm = DataManager()
        self.fm = FunctionManager()
        self.nested_ctr = 0
        self.indentation="\t\t"
        self.shapes_graph_str = ""
        self.finished_shapes_graph = ""
        self.possible_properties = []
        self.possible_classes = []
        self.finishedNodeShapes = []
        self.ridx = 1
        self.isNodeConstraint = False
        self.targetMode = "class"
        self.hasNumericalDtype = False
        self.hasStringDtype = False

        #configure the root window
        self.title("SHACL Editor - Rule Creation")

        self.resizable(0,0)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.inp_dict = {"bot":"https://w3id.org/bot#",
        "cto":"https://w3id.org/cto#",
        "ls":"https://standards.iso.org/iso/21597/-1/ed-1/en/Linkset#",
        "ct":"https://standards.iso.org/iso/21597/-1/ed-1/en/Container#",
        "sh":"http://www.w3.org/ns/shacl#"
        }

        self.help_dict = {
            "Targets" : "https://www.w3.org/TR/shacl/#targets",
            "Property Shapes" : "https://www.w3.org/TR/shacl/#property-shapes",
            "Value Type CCs" : "https://www.w3.org/TR/shacl/#core-components-value-type",
            "Cardinality CCs": "https://www.w3.org/TR/shacl/#core-components-count",
            "Value Range CCS": "https://www.w3.org/TR/shacl/#core-components-range",
            "String-based CCs": "https://www.w3.org/TR/shacl/#core-components-string",
            "Property Pair CCS": "https://www.w3.org/TR/shacl/#core-components-property-pairs",
            "Logical CCs": "https://www.w3.org/TR/shacl/#core-components-logical",
            "Shape-based CCs": "https://www.w3.org/TR/shacl/#core-components-shape",
            "Other CCs": "https://www.w3.org/TR/shacl/#core-components-others",
            "sh:class":"https://www.w3.org/TR/shacl/#ClassConstraintComponent",
            "sh:datatype":"https://www.w3.org/TR/shacl/#DatatypeConstraintComponent",
            "sh:nodeKind":"https://www.w3.org/TR/shacl/#NodeKindConstraintComponent",
            "sh:minCount": "https://www.w3.org/TR/shacl/#MinCountConstraintComponent",
            "sh:maxCount": "https://www.w3.org/TR/shacl/#MaxCountConstraintComponent",
            "sh:minExclusive": "https://www.w3.org/TR/shacl/#MinExclusiveConstraintComponent",
            "sh:minInclusive": "https://www.w3.org/TR/shacl/#MinInclusiveConstraintComponent",
            "sh:maxExclusive": "https://www.w3.org/TR/shacl/#MaxExclusiveConstraintComponent",
            "sh:maxInclusive": "https://www.w3.org/TR/shacl/#MaxInclusiveConstraintComponent",
            "sh:minLength": "https://www.w3.org/TR/shacl/#MinLengthConstraintComponent",
            "sh:maxLength": "https://www.w3.org/TR/shacl/#MaxLengthConstraintComponent",
            "sh:pattern": "https://www.w3.org/TR/shacl/#PatternConstraintComponent",
            "sh:languageIn" : "https://www.w3.org/TR/shacl/#LanguageInConstraintComponent",
            "sh:uniqueLang" : "https://www.w3.org/TR/shacl/#UniqueLangConstraintComponent",
            "sh:equals": "https://www.w3.org/TR/shacl/#EqualsConstraintComponent",
            "sh:disjoint": "https://www.w3.org/TR/shacl/#DisjointConstraintComponent",
            "sh:lessThan":"https://www.w3.org/TR/shacl/#LessThanConstraintComponent",
            "sh:lessThanOrEquals":"https://www.w3.org/TR/shacl/#LessThanOrEqualsConstraintComponent",
            "sh:not": "https://www.w3.org/TR/shacl/#NotConstraintComponent",
            "sh:and": "https://www.w3.org/TR/shacl/#AndConstraintComponent",
            "sh:or": "https://www.w3.org/TR/shacl/#OrConstraintComponent",
            "sh:xone": "https://www.w3.org/TR/shacl/#XoneConstraintComponent",
            "sh:node": "https://www.w3.org/TR/shacl/#NodeConstraintComponent",
            "sh:property": "https://www.w3.org/TR/shacl/#PropertyConstraintComponent",
            "sh:qualifiedValueShape": "https://www.w3.org/TR/shacl/#QualifiedValueShapeConstraintComponent",
            "sh:closed": "https://www.w3.org/TR/shacl/#ClosedConstraintComponent",
            "sh:hasValue": "https://www.w3.org/TR/shacl/#HasValueConstraintComponent",
            "sh:in": "https://www.w3.org/TR/shacl/#InConstraintComponent",
            "Astrea Documentation" : "https://astrea.linkeddata.es/documentation.html"
        }

        #set windows theme
        self.style = ttk.Style(self)
        self.style.theme_use('winnative')

        self.grid_columnconfigure(index=0,weight=1)
        self.grid_columnconfigure(index=1,weight=1)
        self.grid_columnconfigure(index=2,weight=1)
        self.grid_columnconfigure(index=3,weight=1)
        self.grid_columnconfigure(index=4,weight=1)
        self.grid_columnconfigure(index=5,weight=1)

        self.menu = LabelFrame(self, text='Menu')
        self.menu.grid(column=0, columnspan=6, row=0, padx=1, pady=1)

        #add configuration button for the prefixes
        self.prefix_btn = Button(self.menu, text="Configure relevant prefixes", command=self.openConfig)
        self.prefix_btn.grid(column=0, row=0, padx=1, pady=1)

        #add upload button for the merged ontology graph
        self.ont_btn = Button(self.menu, text="Choose Ontology Workfolder", command=self.openFile)
        self.ont_btn.grid(column=1, row=0, padx=1, pady=1)

        #the user can also immediately switch to validation mode
        self.open_val_view = Button(self.menu, text="Open Validation View", command = self.openValidationView)
        self.open_val_view.grid(column=2,row=0, padx=1, pady=1)

        #help menu as a combobox
        help_values = list(self.help_dict.keys())

        self.help_menu = AutocompleteCombobox(self.menu,completevalues=help_values)
        self.help_menu.set('Help')
        self.help_menu.bind("<<ComboboxSelected>>",self.openHelpLink)
        self.help_menu.grid(column=3,row=0, padx=1, pady=1)

        self.CreateToolTip(self.help_menu, text="Here you can get help on different topics/constraint components (CCs)\nby selecting the respective topic. After the selection, a web page with\nmore detailed information and examples will be opened.")
    
    def openHelpLink(self,event):
        topic = self.help_menu.get()
        if len(topic) != 0 and topic != 'Help':
            webbrowser.open_new(self.help_dict[topic])
            self.help_menu.set('Help')
    
    def ctrlEvent(self,event):
        if(12==event.state and event.keysym=='c' ):
            return
        else:
            return "break"

    def openConfig(self):
        ConfigurationView(self)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()
    
    def CreateToolTip(self,widget, text):
        toolTip = ToolTip(widget)
        def enter(event):
            toolTip.showtip(text)
        def leave(event):
            toolTip.hidetip()
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)
    
    #function that clears all widgets except the basic ones
    def clear_grid(self,option):

        self.other_constraints_frame.destroy()
        self.non_validating_frame.destroy()
        self.cardinality_frame.destroy()
        self.value_type_frame.destroy()
        self.shape_based_frame.destroy()
        self.property_pair_constraint.destroy()
        self.logical_constraint.destroy()

        if self.name != "PropertyShapeChild":
            self.newPs.destroy()

        if self.hasNumericalDtype:
            self.value_range_frame.destroy()
            self.hasNumericalDtype = False
        if self.hasStringDtype:
            self.string_based_frame.destroy()
            self.hasStringDtype = False
        
        if option == "newNodeShape":
            self.path_lbl.destroy()
            self.path_combo.destroy()
        
        if option == "everything":
            self.target_frame.destroy()
            self.shapes_frame.destroy()

           
    def openFile(self):

        ontology_directory = askdirectory(title="Choose Directory containing all the Ontologies")
        #parse all the ontologies inside the directory 
        for ontology_file_path in os.listdir(ontology_directory):
            self.dm.parse_ontologies(ontology_directory+"/"+ontology_file_path)

        if len(self.dm.ont_graph) != 0:
            self.ont_btn['state'] = DISABLED

        domain_includes = URIRef("https://schema.org/domainIncludes")
        range_includes = URIRef("https://schema.org/rangeIncludes")

        #for lbd graphs this condition will be true and specific querys will be loaded 
        if (None,domain_includes,None) in self.dm.ont_graph or (None,range_includes,None) in self.dm.ont_graph:
            self.class_query = self.dm.getQueryString("class","lbd")
            self.path_query = self.dm.getQueryString("path","lbd")
            self.properties_query = self.dm.getQueryString("properties","lbd")
            self.subject_query = self.dm.getQueryString("subject","lbd")
            self.range_query = self.dm.getQueryString("range","lbd")
            self.datatype_query = self.dm.getQueryString("datatype","lbd")
            self.object_query = self.dm.getQueryString("object","lbd")
        #for other ontologies simplified queries are loaded
        else:
            self.class_query = self.dm.getQueryString("class","default")
            self.path_query = self.dm.getQueryString("path","default")
            self.properties_query = self.dm.getQueryString("properties","default")
            self.subject_query = self.dm.getQueryString("subject","default")
            self.range_query = self.dm.getQueryString("range","default")
            self.datatype_query = self.dm.getQueryString("datatype","default")
            self.object_query = self.dm.getQueryString("object","default")
           

        # save all classes in a python list - conditions exclude bnodes and classes from non-relevant ontologies
        #self.raw_classes = [r["c"] for r in self.dm.ont_graph.query(self.class_query) if "bot" in r["c"] or "cto" in r["c"] or "Linkset" in r["c"]]
        self.raw_classes = [r["c"] for r in self.dm.ont_graph.query(self.class_query) if [s for s in self.inp_dict if self.inp_dict[s] in r["c"]] != []]
        #clear the prefixes for the drop-down menu
        self.class_list = [re.sub(".*#","",cstring) for cstring in self.raw_classes]

        self.raw_properties = [r["p"] for r in self.dm.ont_graph.query(self.properties_query) if [s for s in self.inp_dict if self.inp_dict[s] in r["p"]] != []]
        self.property_list = [re.sub(".*#","",cstring) for cstring in self.raw_properties]

        #exclude classes with zero outgoing properties (e.g. ls:Identifier, cto:TaskContext) from the list to get the final list
        self.class_list = [c for c in self.class_list if [r["p"] for r in self.dm.ont_graph.query(self.path_query, initBindings={'class': [i for i in self.raw_classes if re.search(".*#+"+c+"$",i) != None][0]})] != []]

        self.target_modes = ["Select Class Target:","Select Subject Target:","Select Object Target:"]

        self.target_frame = LabelFrame(self, text='Target and Property Definitions')
        self.target_frame.grid(column=0, columnspan=2,row=1,rowspan=2, padx=1, pady=1, sticky="nsew")

        self.target_frame.grid_columnconfigure(index=0,weight=1)
        self.target_frame.grid_columnconfigure(index=1,weight=1)

        #add label and autocomplete combobox for the targets
        self.target_lbl = AutocompleteCombobox(self.target_frame,completevalues=self.target_modes)
        self.target_lbl.set("Select Class Target:")
        self.target_lbl.bind("<<ComboboxSelected>>",self.setTargetMode)
        self.target_lbl.grid(column=0, row=1, padx=1, pady=1, sticky="nsew")

        self.display_class_list = []
        for c in self.class_list:
            for i in range(self.class_list.count(c)):
                self.display_class_list.append(c + " ("+FunctionManager.get_namespace(self.inp_dict,self.raw_classes,c,i)+")")
        
        self.display_class_list = list(set( self.display_class_list))
  
        
        self.display_property_list = []
        for p in self.property_list:
            for i in range(self.property_list.count(p)):
                self.display_property_list.append(p + " ("+FunctionManager.get_namespace(self.inp_dict,self.raw_properties,p,i)+")")

        self.display_property_list = list(set(self.display_property_list))

        self.target_combo = AutocompleteCombobox(self.target_frame,completevalues=self.display_class_list)
        self.target_combo.bind("<<ComboboxSelected>>",self.createPathCombo)
        self.target_combo.grid(column=1, row=1, padx=1, pady=1, sticky="nsew")

        self.CreateToolTip(self.target_combo,text="Here, either the classes whose instances are to be restricted or the\nproperties whose subjects or objects are to be restricted can be\nselected.")

        self.shapes_frame = LabelFrame(self, text='Shape In Progress')
        self.shapes_frame.grid(column=2,columnspan=4, row=1,rowspan=7, padx=1, pady=1, sticky="nsew")

        self.shapes_frame.grid_columnconfigure(index=2,weight=1)
        self.shapes_frame.grid_columnconfigure(index=3,weight=1)
        self.shapes_frame.grid_columnconfigure(index=4,weight=1)
        self.shapes_frame.grid_columnconfigure(index=5,weight=1)

        #window for the shapes in progress
        self.shapes_window = scrolledtext.ScrolledText(self.shapes_frame,height=15)
        self.shapes_window.bind("<Key>", lambda e: self.ctrlEvent(e))
        self.shapes_window.grid(column=2,columnspan=4,row=1,rowspan=6, padx=1, pady=1)
    
    def setTargetMode(self,event):
        
        if self.target_lbl.get() == "Select Class Target:":
            self.targetMode = "class"
            self.target_combo.set_completion_list(self.display_class_list)

        elif self.target_lbl.get() == "Select Subject Target:":
            self.targetMode = "subject"
            self.target_combo.set_completion_list(self.display_property_list)

        elif self.target_lbl.get() == "Select Object Target:":
            self.targetMode = "object"
            self.target_combo.set_completion_list(self.display_property_list)

    def createPathCombo(self, event):
        self.shapes_window.delete(1.0,END)
        self.possible_properties = []
        self.shapes_frame.configure(text='Shape In Progress')
        if self.name == "Root":
            self.ridx = 2
        else:
            self.ridx = 1
            if self.name == "PropertyShapeChild":
                self.indentation ="\t"

        #get node shape string and namespace of selected target
        if self.name == "Root":
            if self.targetMode == "class":
                self.ns_str, self.namespace, self.target_iri = FunctionManager.get_ns_string(self.raw_classes, self.target_combo.get(),self.inp_dict,None,self.targetMode)
            else:
                self.ns_str, self.namespace, self.target_iri = FunctionManager.get_ns_string(self.raw_properties, self.target_combo.get(),self.inp_dict,None,self.targetMode)
                
        elif self.name == "NodeShapeChild":
            if self.targetMode == "class":
                self.ns_str, self.namespace, self.target_iri = FunctionManager.get_ns_string(self.raw_classes, self.target_combo.get(),self.inp_dict,self.label,self.targetMode)
            else:
                self.ns_str, self.namespace, self.target_iri = FunctionManager.get_ns_string(self.raw_properties, self.target_combo.get(),self.inp_dict,self.label,self.targetMode)

        if self.name != "PropertyShapeChild":
            self.shapes_window.delete(1.0,END)
            self.shapes_window.insert(INSERT,self.ns_str)
        else:
            self.shapes_window.delete(1.0,END)
        
        if self.targetMode == "class" and self.name != "PropertyShapeChild":
            TargetNodeView(self)
        
        self.target_lbl['state'] = DISABLED
        self.target_combo['state'] = DISABLED

        self.path_lbl = Label(self.target_frame, text="Select Path Property:")
        self.path_lbl.grid(column=0, row=self.ridx, padx=1, pady=1, sticky="nsew")

        if self.name != "PropertyShapeChild":
            if self.targetMode == "class":
                self.properties = [r["p"] for r in self.dm.ont_graph.query(self.path_query, initBindings={'class': self.target_iri})]
            else:
                if self.targetMode == "subject":
                    tmp_classes = [r["class"] for r in self.dm.ont_graph.query(self.subject_query, initBindings={'p': self.target_iri})]
                elif self.targetMode == "object":
                    tmp_classes = [r["range"] for r in self.dm.ont_graph.query(self.range_query, initBindings={'property': self.target_iri})]
                self.properties = []
                for c in tmp_classes:
                    tmp_raw_properties = [r["p"] for r in self.dm.ont_graph.query(self.path_query, initBindings={'class': c})]
                    self.properties.append(tmp_raw_properties)

                self.properties = list(set([item for sublist in self.properties for item in sublist]))

        else:
            # for a property shape no explicit class was chosen, which means we compute the domain for ALL POSSIBLE classes
            self.properties = []
            if self.targetMode == "class":
                for c in self.display_class_list:
                    if c != str(None):
                        _,_,tmp_target_iri = FunctionManager.get_ns_string(self.raw_classes,c,self.inp_dict,self.label,self.targetMode)
                        tmp_raw_properties = [r["p"] for r in self.dm.ont_graph.query(self.path_query, initBindings={'class': tmp_target_iri})]
                        self.properties.append(tmp_raw_properties)
            
            #flatten list of list into single list and remove duplicates
            self.properties = list(set([item for sublist in self.properties for item in sublist]))
        
        #from here on property shape and node shape behave the same
        self.properties_list = [re.sub(".*#","",pstring) for pstring in self.properties]

        #self.display_properties_list = [p + " ("+FunctionManager.get_namespace(self.inp_dict,self.raw_properties,p)+")" for p in self.properties_list]

        self.display_properties_list = []

        for p in self.properties_list:
            for i in range(self.properties_list.count(p)):
                self.display_properties_list.append(p + " ("+FunctionManager.get_namespace(self.inp_dict,self.raw_properties,p,i)+")")
        
        self.display_properties_list = list(set( self.display_properties_list))

        self.path_combo = AutocompleteCombobox(self.target_frame,completevalues=self.display_properties_list)

        self.path_combo.bind("<<ComboboxSelected>>",self.displayPath)
        self.path_combo.grid(column=1,row=self.ridx, padx=1, pady=1, sticky="nsew")

        self.CreateToolTip(self.path_combo,text="Here you can select the property of the targets for which a\nPropertyShape should be created.")

        if self.name == "Root":
            #some functionalities that are only necessary for the root window
            self.newNs = Button(self.shapes_frame, text="Save", command = self.addNewNodeShape)
            self.newNs.grid(column=2,row=self.ridx+5, padx=1, pady=1)

            #resetting inner shapes can already be done by simply closing the pop-up windows
            self.resetNs = Button(self.shapes_frame, text="Reset", command = self.resetNodeShape)
            self.resetNs.grid(column=3,row=self.ridx+5, padx=1, pady=1)
            
            self.downloadShapes = Button(self.shapes_frame, text="Download", command = self.downloadShapesGraph)
            self.downloadShapes.grid(column=5,row=self.ridx+5, padx=1, pady=1)
            
    def resetNodeShape(self):
        if len(self.target_combo.get()) !=0:
            if messagebox.askokcancel(title="Node Shape Removal",message="Are you sure that you want to delete the current shape in progress ? This operation can not be undone."):
                self.shapes_window.delete(1.0,END)
                if len(self.path_combo.get()) != 0:
                    self.clear_grid(option="newNodeShape")
                else:
                    self.path_lbl.destroy()
                    self.path_combo.destroy()
                
                self.target_lbl['state'] = NORMAL
                self.target_combo['state'] = NORMAL
                self.target_combo.set("")

                self.newNs['state'] = DISABLED


    def toggleClosedness(self):
        self.add("closed",str(self.chk_state.get()).lower(),self.chk_state.get(),target="NodeShape")

        if self.chk_state.get():
            IgnoredPropertiesView(self)
        else:
            if self.contains("ignoredProperties",target="NodeShape"):
                self.remove("ignoredProperties",target="NodeShape")

    #validation function for cardinality entries that forces input to be uint or empty string/deletion 
    def validateUnsignedInt(self,inp):
        try:
            int(inp)
        except:
            if inp != "":
                messagebox.showerror(title="Non valid cardinality input",message="For Cardinalities only unsigned int is allowed as input.")
                return False
        return True
    
    def validateRegEx(self,inp):
        try:
            re.compile(inp)
        except re.error:
            messagebox.showerror(title="Non valid regex pattern",message="The pattern you are trying to add is not a valid regex pattern.")
            return False
        return True

    def displayPath(self, event):


        #registering validation functions for some of the entries to prevent false user input
        self.vcmd_uint = (self.register(self.validateUnsignedInt),'%P')
        self.vcmd_regex = (self.register(self.validateRegEx),'%P')

        if self.name != "PropertyShapeChild":
            if self.name != "NodeShapeChild":
                if self.possible_properties == []:
                    self.path_string = FunctionManager.get_path_string(self.shapes_window.get(1.0,END),self.inp_dict,self.raw_properties,self.path_combo.get())
                else:
                    self.path_string = FunctionManager.getNewPathPropertyString(self.shapes_window.get(1.0,END),self.inp_dict,self.raw_properties,self.path_combo.get())
            else:
                if self.possible_properties == []:
                    self.path_string = FunctionManager.get_path_string(self.shapes_window.get(1.0,END),self.inp_dict,self.raw_properties,self.path_combo.get(),True)
                else:
                    self.path_string = FunctionManager.getNewPathPropertyString(self.shapes_window.get(1.0,END),self.inp_dict,self.raw_properties,self.path_combo.get(),True)
        else:
                self.path_string, self.namespace, self.property_iri = FunctionManager.get_ps_string(self.properties,self.path_combo.get(),self.label,self.inp_dict)
        
        self.shapes_window.delete(1.0,END)
        self.shapes_window.insert(INSERT,self.path_string)

        if self.possible_properties == []:
            self.possible_properties = [i for i in self.display_properties_list if i != self.path_combo.get()]
        else:
            self.possible_properties = [i for i in self.possible_properties if i != self.path_combo.get()]

        self.path_combo['state'] = DISABLED

        self.other_constraints_frame = LabelFrame(self,text="Other Constraint Components")
        self.other_constraints_frame.grid(row=self.ridx+6,column=2,columnspan=2,rowspan=3,padx=1, pady=1, sticky="nsew")

        
        self.other_constraints_frame.grid_columnconfigure(index=2,weight=1)
        self.other_constraints_frame.grid_columnconfigure(index=3,weight=1)

        closedness_tooltip = dedent('''\
        By setting the checkmark, the class is considered closed. "Closed" in the
        SHACL context means that instances of the restricted class may only
        have the properties specified under sh:path. Exceptions for properties
        that should not be affected by this restriction can optionally be selected
        in a separate pop-up window after setting the checkmark.''')

        if self.name != "PropertyShapeChild" and self.targetMode == "class" and not self.contains('targetNode','NodeShape'):
            #add a checkbutton for sh:closed
            self.chk_state = BooleanVar()
            self.chk_state.set(False) #set check state
            self.chk = Checkbutton(self.other_constraints_frame, text='Toggle Class Closedness', var=self.chk_state, onvalue=True, offvalue=False,command =self.toggleClosedness)
            self.chk.grid(column=2,columnspan=2, row=self.ridx+6,padx=1, pady=1, sticky="nsew")

            self.CreateToolTip(self.chk,text= closedness_tooltip)

        self.non_validating_frame = LabelFrame(self,text="Non-Validating Constraint Components")
        self.non_validating_frame.grid(column=0,columnspan=2,row=self.ridx+5,rowspan=2, padx=1, pady=1, sticky="nsew")

        
        self.non_validating_frame.grid_columnconfigure(index=0,weight=1)
        self.non_validating_frame.grid_columnconfigure(index=1,weight=1)

        #combobox for sh:severity
        self.severity_lbl = Label(self.non_validating_frame,text="Select Severity:")
        self.severity_lbl.grid(column=0,row=self.ridx+5, padx=1, pady=1, sticky="nsew")
        self.severity_combo = AutocompleteCombobox(self.non_validating_frame,completevalues=["Info","Warning","Violation"])
        self.severity_combo.bind("<<ComboboxSelected>>",self.addSeverity)
        self.severity_combo.grid(column=1,row=self.ridx+5, padx=1, pady=1, sticky="nsew")

        self.CreateToolTip(self.severity_combo, text = 'Here you can select the severity level for a possible violation of\nthe PropertyShape. Only three classes are supported, with\nsh:Violation being the default class.')

        #button and entry bos for sh:message
        self.message_txt = Entry(self.non_validating_frame)
        self.message_txt.grid(column=1, row=self.ridx+6, padx=1, pady=1, sticky="nsew")
        self.CreateToolTip(self.message_txt, text = 'Here you can define a string message that will be displayed to the\nuser in case of a violation.')

        self.message_btn = Button(self.non_validating_frame, text="Add Message", command=lambda: self.add("message",self.message_txt.get()))
        self.message_btn.grid(column=0, row=self.ridx+6, padx=1, pady=1, sticky="nsew")

        self.cardinality_frame = LabelFrame(self,text="Cardinality Constraint Components")
        self.cardinality_frame.grid(column=0,columnspan=2, row=self.ridx+3,rowspan=2, padx=1, pady=1, sticky="nsew")

        self.cardinality_frame.grid_columnconfigure(index=0,weight=1)
        self.cardinality_frame.grid_columnconfigure(index=1,weight=1)


        #button and entry box for sh:minCount -> only positive int is allowed, other input is blocked
        self.minc_txt = Entry(self.cardinality_frame, validate='key', validatecommand=self.vcmd_uint)
        self.minc_txt.grid(column=1, row=self.ridx+3, padx=1, pady=1, sticky="nsew")
        self.CreateToolTip(self.minc_txt,text='Here you can define the minimum number of relations via the\nselected path property that the targets must have.')
        self.minc_btn = Button(self.cardinality_frame, text="Add minCount", command=lambda: self.add("minCount",self.minc_txt.get()))
        self.minc_btn.grid(column=0, row=self.ridx+3, padx=1, pady=1, sticky="nsew")

        #button entry box for sh:maxCount -> only positive int is allowed, other input is blocked
        self.maxc_txt = Entry(self.cardinality_frame, validate='key', validatecommand=self.vcmd_uint)
        self.maxc_txt.grid(column=1, row=self.ridx+4, padx=1, pady=1, sticky="nsew")
        self.CreateToolTip(self.maxc_txt,text='Here you can define the maximum number of relations via the\nselected path property that the targets must have.')
        self.maxc_btn = Button(self.cardinality_frame, text="Add maxCount", command=lambda: self.add("maxCount",self.maxc_txt.get()))
        self.maxc_btn.grid(column=0, row=self.ridx+4, padx=1, pady=1, sticky="nsew")

        hasValue_tooltip = dedent('''\
        sh:hasValue specifies the condition that at least one value node is equal
        to the specified RDF term. IRIs, literals and blank nodes are collectively
        known as RDF terms.''')

        in_tooltip = dedent('''\
        sh:in specifies the condition that each value node is a member
        of a provided SHACL list of RDF terms. IRIs, literals and blank
        nodes are collectively known as RDF terms.''')

        #button and entry box for sh:hasValue
        self.hasValue_txt = Entry(self.other_constraints_frame)
        self.hasValue_txt.grid(column=3,columnspan=2, row=self.ridx+7, padx=1, pady=1, sticky="nsew")
        self.hasValue_btn = Button(self.other_constraints_frame, text="Add hasValue", command=lambda: self.add("hasValue",self.hasValue_txt.get()))
        self.hasValue_btn.grid(column=2, row=self.ridx+7, padx=1, pady=1, sticky="nsew")

        self.CreateToolTip(self.hasValue_txt,text=hasValue_tooltip)

        #button and entry box for sh:in
        self.in_txt = Entry(self.other_constraints_frame)
        self.in_txt.grid(column=3,columnspan=2, row=self.ridx+8, padx=1, pady=1, sticky="nsew")
        self.in_btn = Button(self.other_constraints_frame, text="Add in", command=lambda: self.add("in",self.in_txt.get()))
        self.in_btn.grid(column=2, row=self.ridx+8, padx=1, pady=1, sticky="nsew")

        self.CreateToolTip(self.in_txt,text=in_tooltip)



        #check whether selected property is a datatype or object property
        self.property_iri = FunctionManager.get_property_iri(self.path_combo.get(),self.inp_dict,self.raw_properties)
        self.isDatatype = self.dm.ont_graph.query(self.datatype_query, initBindings={'property': self.property_iri})
        self.isObject = self.dm.ont_graph.query(self.object_query, initBindings={'property': self.property_iri})

        self.value_type_frame = LabelFrame(self,text="Value Type Constraint Components")
        self.value_type_frame.grid(column=0,columnspan=2, row=self.ridx+1,rowspan=2, padx=1, pady=1, sticky="nsew")

        
        self.value_type_frame.grid_columnconfigure(index=0,weight=1)
        self.value_type_frame.grid_columnconfigure(index=1,weight=1)

        

        #if it is a datatype property then also display a combobox for possible ranges 
        if(bool(self.isDatatype)):

            #add a checkbutton for sh:nodeKind, which sets it to sh:Literal when checked
            self.nodeKind_state = BooleanVar()
            self.nodeKind_state.set(False) #set check state
            self.nodeKind = Checkbutton(self.value_type_frame , text='Toggle NodeKind Constraint', var=self.nodeKind_state, onvalue=True, offvalue=False,command = self.toggleLiteralNodeKind)
            self.nodeKind.grid(column=0,columnspan=2,row=self.ridx+1, padx=1, pady=1, sticky="nsew")

            self.CreateToolTip(self.nodeKind, 'If you check this box, then based on the property type (which\n'+
            'distinguishes between object properties and data type properties) the\n'+
            'RDF node type (SHACL distinguishes between IRI, BlankNode, Literal or\n'+
            'all pairwise disjunctions of these three types) is added as a nodeKind\n'+
            'constraint, which all objects (so-called value nodes) of this property\n'+ 
            'must then fulfill.')

            self.raw_ranges = [r["range"] for r in self.dm.ont_graph.query(self.range_query, initBindings={'property': self.property_iri})]
            self.range_list = [re.sub(".*#","",rstring) for rstring in self.raw_ranges]
            self.range_lbl = Label(self.value_type_frame, text="Add Datatype Constraint")
            self.range_lbl.grid(column=0, row=self.ridx+2, padx=1, pady=1, sticky="nsew")

            #if there is no range the full list of all xsd datatypes is shown 
            if self.range_list == []:
                self.range_list = FunctionManager.getXSDDatatypes()

            self.range_combo = AutocompleteCombobox(self.value_type_frame,completevalues=self.range_list)
            self.range_combo.bind("<<ComboboxSelected>>",self.addDatatype)
            self.range_combo.grid(column=1,row=self.ridx+2, padx=1, pady=1, sticky="nsew")

            self.CreateToolTip(self.range_combo, 'Here you can select the data type to which the value nodes must then\n'+
            'belong. The suggested data types correspond to the values of the\n'+
            'rdfs:range predicate in the ontologies based on the selected property or\n'+
            '(if no rdfs:range is defined) to the list of XML Schema data types\n'+
            'recommended by the W3C Recommendation on RDF Semantics.')

        #if it is an object property display a checkbox for setting sh:nodeKind to sh:IRI
        elif (bool(self.isObject)):

            #add a checkbutton for sh:nodeKind, which sets it to sh:IRI when checked
            self.nodeKind_state = BooleanVar()
            self.nodeKind_state.set(False) #set check state
            self.nodeKind = Checkbutton(self.value_type_frame, text='Toggle NodeKind Constraint', var=self.nodeKind_state, onvalue=True, offvalue=False,command = self.toggleNodeKind)
            self.nodeKind.grid(column=0,row=self.ridx+1,columnspan=2, padx=1, pady=1, sticky="nsew")

            self.CreateToolTip(self.nodeKind, 'If you check this box, then based on the property type (which\n'+
            'distinguishes between object properties and data type properties) the\n'+
            'RDF node type (SHACL distinguishes between IRI, BlankNode, Literal or\n'+
            'all pairwise disjunctions of these three types) is added as a nodeKind\n'+
            'constraint, which all objects (so-called value nodes) of this property\n'+ 
            'must then fulfill.')

            #add a combobox for adding a property class constraint
            self.raw_ranges = [r["range"] for r in self.dm.ont_graph.query(self.range_query, initBindings={'property': self.property_iri})]
            self.range_list = [re.sub(".*#","",rstring) for rstring in self.raw_ranges]
            #self.display_range_list =  [r + " ("+FunctionManager.get_namespace(self.inp_dict,self.raw_classes,r)+")" for r in self.range_list]

            self.display_range_list = []
            for r in self.range_list:
                for i in range(self.range_list.count(r)):
                    ns = FunctionManager.get_namespace(self.inp_dict,self.raw_ranges,r,i)
                    if ns != str('None'):
                        self.display_range_list.append(r + " ("+ns+")")
            
            self.display_range_list = list(set(self.display_range_list))

            '''
            if self.display_range_list == []:
                self.display_range_list = self.display_class_list
                if 'None' in self.display_range_list:
                    self.display_range_list.remove('None')
            ''' 

            self.range_lbl = Button(self.value_type_frame, text="Add Class Constraint",command=self.addPropClass)
            self.range_lbl.grid(column=0, row=self.ridx+2, padx=1, pady=1, sticky="nsew")

            self.object_range_combo = AutocompleteCombobox(self.value_type_frame,completevalues=self.display_range_list)
            self.object_range_combo.bind("<<ComboboxSelected>>",self.addPropertyClass)
            self.object_range_combo.grid(column=1,row=self.ridx+2, padx=1, pady=1, sticky="nsew")

            self.CreateToolTip(self.object_range_combo, 'Here you can select the class to which the value nodes must then \n'+
            'belong. The proposed classes correspond to the values of the rdfs:range \n'+
            'predicate in the ontologies with respect to the selected property or\n'+
            '(if no rdfs:range is defined) to the list of all classes in the ontologies.')
        
        self.shape_based_frame = LabelFrame(self,text="Shape-based Constraint Components")
        self.shape_based_frame.grid(row=self.ridx+7,column=0,columnspan=2,rowspan=4,padx=1, pady=1, sticky="nsew")

        self.shape_based_frame.grid_columnconfigure(index=0,weight=1)
        self.shape_based_frame.grid_columnconfigure(index=1,weight=1)
        
        #button for adding a sh:node constraint
        self.node_constraint = Button(self.shape_based_frame, text="Add Node Constraint", command=lambda: self.newWindow("","",True))
        self.node_constraint.grid(column=0,columnspan=2, row=self.ridx+10, padx=1, pady=1, sticky="nsew")

        self.CreateToolTip(self.node_constraint,text='Click this button to define a NodeShape that must be satisfied by\nall value nodes.')
        
        qual_count_tooltip = dedent('''\
        When you add a qualified count (min or max) for the first time, you can
        define a qualified value shape (which can be either a NodeShape or a
        PropertyShape) that must be satisfied by the specified number of value 
        nodes. Once a qualified value shape has been added at least one count
        must always remain defined and must not be deleted as this is a
        mandatory parameter.''')

        qual_disj_tooltip = dedent('''\
        This constraint only has an effect if more than one qualified value shape
        has been defined for a path property. If this is the case and the 
        checkmark is set, it means that the sets of entities satisfying the different
        qualified value shapes must be disjoint.''')

        #button and entry box for sh:qualifiedMinCount -> only positive int is allowed, other input is blocked
        self.qminc_txt = Entry(self.shape_based_frame, validate='key', validatecommand=self.vcmd_uint)
        self.qminc_txt.grid(column=1, row=self.ridx+8, padx=1, pady=1, sticky="nsew")
        self.qminc_btn = Button(self.shape_based_frame, text="Add qualifiedMinCount", command=lambda: self.newWindow("qualifiedMinCount",self.qminc_txt.get()))
        self.qminc_btn.grid(column=0, row=self.ridx+8, padx=1, pady=1, sticky="nsew")

        self.CreateToolTip(self.qminc_txt,text=qual_count_tooltip)

        #button entry box for sh:qualifiedMaxCount -> only positive int is allowed, other input is blocked
        self.qmaxc_txt = Entry(self.shape_based_frame, validate='key', validatecommand=self.vcmd_uint)
        self.qmaxc_txt.grid(column=1, row=self.ridx+9, padx=1, pady=1, sticky="nsew")
        self.qmaxc_btn = Button(self.shape_based_frame, text="Add qualifiedMaxCount", command=lambda: self.newWindow("qualifiedMaxCount",self.qmaxc_txt.get()))
        self.qmaxc_btn.grid(column=0, row=self.ridx+9, padx=1, pady=1, sticky="nsew")

        self.CreateToolTip(self.qmaxc_txt,text=qual_count_tooltip)

        #checkbutton for sh:qualifiedValueShapesDisjoint
        self.qvs_disjoint_state = BooleanVar()
        self.qvs_disjoint = Checkbutton(self.shape_based_frame, text='Toggle Qualified Disjointness', var=self.qvs_disjoint_state, onvalue=True, offvalue=False,state = DISABLED,command = self.toggleQvsDisjointness)
        self.qvs_disjoint.grid(column=0,row=self.ridx+7,columnspan=2, padx=1, pady=1, sticky="nsew")

        self.CreateToolTip(self.qvs_disjoint,text=qual_disj_tooltip)

        propertypair_tooltip = dedent('''\
        Property pair constraint components specify conditions on the sets
        of value nodes in relation to other properties. There are four
        different constraint types, which can be selected in a separate pop-
        up window.''')

        logical_tooltip = dedent('''\
        Logical constraint components implement the common logical
        operators AND, OR and NOT, as well as a variation of EXCLUSIVE OR. 
        The different types can be defined in a separate pop-up window.''')

        #button for adding property pair constraint
        self.property_pair_constraint = Button(self, text="Add Property Pair Constraint", command=self.newPPC)
        self.property_pair_constraint.grid(column=2,columnspan=2, row=self.ridx+9, padx=1, pady=1, sticky="nsew")

        self.CreateToolTip(self.property_pair_constraint,text=propertypair_tooltip)

        #button for adding logical constraints
        self.logical_constraint = Button(self, text="Add Logical Constraint", command=self.newLC)
        self.logical_constraint.grid(column=2,columnspan=2, row=self.ridx+10, padx=1, pady=1, sticky="nsew")

        self.CreateToolTip(self.logical_constraint,text=logical_tooltip)

        #children can also finalize, which ends the recursion/nesting by adding the shape to the parent window and closing the window
        if self.name == "NodeShapeChild":
            self.finalize_btn = Button(self.shapes_frame,text='Finalize',command =self.finalize)
            self.finalize_btn.grid(column=2,columnspan=2, row=self.ridx+5, padx=1, pady=1)
        
        if self.name == "PropertyShapeChild":
            self.finalize_btn = Button(self.shapes_frame,text='Finalize',command =self.finalize)
            self.finalize_btn.grid(column=2,columnspan=4, row=self.ridx+5, padx=1, pady=1)
        
        if self.name != "PropertyShapeChild":
            #buttons for adding more property shapes to the current Node Shape
            self.newPs = Button(self.shapes_frame, text="Add Path", command=self.addNewPs)
            if self.name == "Root":
                self.newPs.grid(column=4,row=self.ridx+5, padx=1, pady=1)
            else:
                self.newPs.grid(column=4,columnspan=2,row=self.ridx+5, padx=1, pady=1)

    
    def newLC(self):
        LogicalConstraintView(self)
    
    def newPPC(self):
        PropertyPairView(self)
        
    def toggleLiteralNodeKind(self):
        self.add("nodeKind", "sh:Literal", self.nodeKind_state.get())
    
    def toggleQvsDisjointness(self):
        self.add("qualifiedValueShapesDisjoint",str(self.qvs_disjoint_state.get()).lower(),self.qvs_disjoint_state.get())
    
    def addPropertyClass(self,event):
        self.add("class",self.object_range_combo.get())
    
    def addPropClass(self):
        self.add("class",self.object_range_combo.get())
    
    def openValidationView(self):
        ValidationView(self)
    
    def addSeverity(self,event):
        self.add("severity","sh:"+self.severity_combo.get())

    def addNewPs(self):
        #clear all lower widgets every time a new property shape is added 
        self.clear_grid(option="newPropertyShape")

        self.path_combo['state'] = NORMAL

        self.path_combo.set("")
    
    def addNewNodeShape(self):
        self.shapes_frame.configure(text='Shapes Graph Preview')
        finished_node_shape = self.shapes_window.get(1.0,END)
        if len(finished_node_shape) != 0:
            if self.checkValidity(finished_node_shape):

                self.dm.shapes_graph.parse(data=self.finished_shapes_graph)

                self.finishedNodeShapes.append(finished_node_shape)
                self.possible_properties = []
                self.clear_grid(option="newNodeShape")
                
                if self.possible_classes == []:
                    self.possible_classes = [i for i in self.class_list if i != self.target_combo.get()]
                else:
                    self.possible_classes = [i for i in self.possible_classes if i != self.target_combo.get()]
                
                self.target_lbl['state'] = NORMAL
                self.target_lbl.set("Select Class Target:")
                self.target_combo['state'] = NORMAL
                self.target_combo.set_completion_list(self.display_class_list)
                self.target_combo.set("")

                self.shapes_window.delete(1.0,END)
                self.shapes_window.insert(INSERT,self.dm.shapes_graph.serialize(format="turtle"))

                self.newNs['state'] = DISABLED
                self.resetNs['state'] = DISABLED

                messagebox.showinfo(title="NodeShape Added Successfully",message="The Node Shape passed the validity check and was added successfully. You can now download the current shapes graph or start a new Node Shape by selecting a new target.")
            else:
                messagebox.showerror(title="ParserError",message='This Node Shape is not valid ! Please check the correctness of your input and also check if you provided all the necessary prefixes !')

        self.shapes_graph_str = "\n".join(self.finishedNodeShapes)
    
    def checkValidity(self,shape):
        ont_lines = self.dm.ont_graph.serialize(format="turtle").split("\n")
        prefixes = [line for line in ont_lines if "@prefix" in line]

        #always append the SHACL prefix 
        self.inp_dict["sh"] = "http://www.w3.org/ns/shacl#"

        for prefix in self.inp_dict:
            test_line = "@prefix "+prefix+": <"+self.inp_dict[prefix]+"> ."
            if test_line not in prefixes:
                    prefixes.append(test_line)
        prefix_header = "\n".join(prefixes)
        self.finished_shapes_graph = prefix_header+"\n"+shape
        try:
            Graph().parse(data=self.finished_shapes_graph)
        except(ParserError):
            return False

        return True

    def downloadShapesGraph(self):
        if self.finishedNodeShapes != []:
            file = asksaveasfile(defaultextension=".ttl")
            file.write(self.dm.shapes_graph.serialize(format="turtle"))

        else:
            messagebox.showerror('Empty Shapes Graph', 'You are trying to download an empty Shapes Graph. You have to save at least one Node Shape by using the corresponding button. The textbox just shows \'Shapes in Progress\' that are not considered finished until you have saved them.')

    #function for adding shacl constructs to shapes 
    def add(self,type,txt_input, add=True, target="PropertyShape"):
        if len(txt_input) != 0:

            #first element of x = outer node shape
            x = self.shapes_window.get(1.0,END).split("#")
            if target=="PropertyShape":
                y = x[0].split("sh:property")
                #cur_str corresponds to the last property shape
                cur_str = y[-1].split(";")
            if target=="NodeShape":
                cur_str = x[0].split(";")

            #delete old value, if it exists
            if type != "qualifiedValueShape" and type != "in":
                cur_str = [i for i in cur_str if type not in i]
            elif type == "qualifiedValueShape" or type == "in":
                cur_str = [i for i in cur_str if txt_input not in i]

            if type=="datatype":
                txt_input = "xsd:"+txt_input
            if type=="pattern" or type =="message":
                txt_input = "\""+txt_input+"\""
            if type=="class":
                namespace = txt_input.split("(")[1].split(")")[0]
                c = txt_input.split(" ")[0]
                txt_input = namespace+":"+c
            
            #for checkboxes this might be false
            if add:
                #insert the new constraint
                if target=="PropertyShape":
                    cur_str.insert(1,"\n"+self.indentation+"sh:"+str(type)+" "+str(txt_input)+" ")
                else:
                    cur_str.insert(1,"\n\t"+"sh:"+str(type)+" "+str(txt_input)+" ")

            if target=="PropertyShape":
                #reversing the splits 
                y[-1] = ";".join(cur_str)
                x[0] = "sh:property".join(y)
            if target=="NodeShape":
                x[0] = ";".join(cur_str)

            if not self.checkValidity("#".join(x)):
                messagebox.showerror(title="Parser Error",message="The Input for this field was not valid and could not be added.")
                if add:
                    #delete the new constraint
                    if target=="PropertyShape":
                        cur_str.remove("\n"+self.indentation+"sh:"+str(type)+" "+str(txt_input)+" ")
                         #reversing the splits 
                        y[-1] = ";".join(cur_str)
                        x[0] = "sh:property".join(y)
                    else:
                        cur_str.remove("\n\t"+"sh:"+str(type)+" "+str(txt_input)+" ")
                        x[0] = ";".join(cur_str)

            #updating the shapes window
            self.shapes_window.delete(1.0,END)
            self.shapes_window.insert(INSERT,"#".join(x))

        #if entry string is passed or prior input is deleted before clicking the add/change button it is removed
        else:
            self.remove(type,target)

            if type=="pattern":
                self.remove("flags",target)
    
    #function for removing shacl constructs to shapes 
    def remove(self,type,target="PropertyShape"):
        #first element of x = outer node shape
        x = self.shapes_window.get(1.0,END).split("#")
        if target=="PropertyShape":
            y = x[0].split("sh:property")
            #cur_str corresponds to the last property shape
            cur_str = y[-1].split(";")
        if target=="NodeShape":
            cur_str = x[0].split(";")

        cur_str = [i for i in cur_str if type not in i]   
        
        if target=="PropertyShape":
            #reversing the splits 
            y[-1] = ";".join(cur_str)
            x[0] = "sh:property".join(y)
        if target=="NodeShape":
            x[0] = ";".join(cur_str)

        #updating the shapes window
        self.shapes_window.delete(1.0,END)
        self.shapes_window.insert(INSERT,"#".join(x))
    
    #function for checking the containment of shacl constructs in shapes 
    def contains(self,type,target="PropertyShape"):
        #first element of x = outer node shape
        x = self.shapes_window.get(1.0,END).split("#")
        
        if target=="PropertyShape":
            y = x[0].split("sh:property")
            #cur_str corresponds to the last property shape
            cur_str = y[-1].split(";")
        
        if target=="NodeShape":
            cur_str = x[0].split(";")

        new_str = [i for i in cur_str if type not in i]   

        #if the construct is present new_str will be smaller and True is returned
        if len(new_str) < len(cur_str):
            return True
        else:
            return False

    
    def toggleNodeKind(self):
        self.add("nodeKind", "sh:BlankNodeOrIRI", self.nodeKind_state.get())
    
    def addDatatype(self, event):
        if len(self.range_combo.get()) != 0:

            reset_constructs = ["minExclusive", "minInclusive", "maxExclusive","maxInclusive","minLength","maxLength","pattern","languageIn","uniqueLang","flags"]
            for i in reset_constructs:
                self.remove(i)

            self.add("datatype", self.range_combo.get())
        
            #if the user has chosen a numerical datatype, then add value range constraint components
            if self.range_combo.get() in ["decimal", "float", "double", "integer", "int","positiveInteger", "nonPositiveInteger",\
                        "negativeInteger", "nonNegativeInteger", "long", "short", "byte","unsignedByte","unsignedInt","unsignedLong","unsignedShort",\
                            "date", "dateTime","gDay","gMonth","gMonthDay","gYear","gYearMonth","time"]:
                if self.hasStringDtype:
                    self.hasStringDtype = False
                    self.string_based_frame.destroy()

                if not self.hasNumericalDtype:

                    self.value_range_frame = LabelFrame(self,text="Value Range Constraint Components")
                    self.value_range_frame.grid(column=4,columnspan=2, row=self.ridx+6,rowspan=5, padx=1, pady=1, sticky="ew")

                    self.value_range_frame.grid_columnconfigure(index=4,weight=1)
                    self.value_range_frame.grid_columnconfigure(index=5,weight=1)

                    self.CreateToolTip(self.value_range_frame,text="The following constraint components specify value range\nconditions to be satisfied by value nodes that are comparable\nvia operators such as <, <=, > and >=.")
                    
                    self.minExc_txt = Entry(self.value_range_frame)
                    self.minExc_txt.grid(column=5, row=self.ridx+6, padx=1, pady=1, sticky="nsew")
                    self.minExc_btn = Button(self.value_range_frame, text="Add Exclusive Lower Bound:",command=lambda: self.add("minExclusive", self.minExc_txt.get()))
                    self.minExc_btn.grid(column=4, row=self.ridx+6, padx=1, pady=1, sticky="nsew")

                    self.minInc_txt = Entry(self.value_range_frame)
                    self.minInc_txt.grid(column=5, row=self.ridx+7, padx=1, pady=1, sticky="nsew")
                    self.minInc_btn = Button(self.value_range_frame, text="Add Inclusive Lower Bound:",command=lambda: self.add("minInclusive", self.minInc_txt.get()))
                    self.minInc_btn.grid(column=4, row=self.ridx+7, padx=1, pady=1, sticky="nsew")

                    self.maxExc_txt = Entry(self.value_range_frame)
                    self.maxExc_txt.grid(column=5, row=self.ridx+8, padx=1, pady=1, sticky="nsew")
                    self.maxExc_btn = Button(self.value_range_frame, text="Add Exclusive Upper Bound:",command=lambda: self.add("maxExclusive", self.maxExc_txt.get()))
                    self.maxExc_btn.grid(column=4, row=self.ridx+8, padx=1, pady=1, sticky="nsew")

                    self.maxInc_txt = Entry(self.value_range_frame)
                    self.maxInc_txt.grid(column=5, row=self.ridx+9, padx=1, pady=1, sticky="nsew")
                    self.maxInc_btn = Button(self.value_range_frame, text="Add Inclusive Upper Bound:",command=lambda: self.add("maxInclusive", self.maxInc_txt.get()))
                    self.maxInc_btn.grid(column=4, row=self.ridx+9, padx=1, pady=1, sticky="nsew")

                    self.hasNumericalDtype = True

            #if the user has chosen a string datatype, then add string-based constraint components
            elif self.range_combo.get() in ["string", "normalizedString", "token", "language", "Name","NMTOKEN","NCName","anyURI","base64Binary","boolean",\
                    "hexBinary"]:
                if self.hasNumericalDtype:
                    self.hasNumericalDtype = False
                    self.value_range_frame.destroy()

                if not self.hasStringDtype:
                    self.string_based_frame = LabelFrame(self,text="String-based Constraint Components")
                    self.string_based_frame.grid(column=4,columnspan=2, row=self.ridx+6,rowspan=5, padx=1, pady=1, sticky="nsew")

                    self.string_based_frame.grid_columnconfigure(index=4,weight=1)
                    self.string_based_frame.grid_columnconfigure(index=5,weight=1)

                    self.minLg_txt = Entry(self.string_based_frame, validate='key', validatecommand=self.vcmd_uint)
                    self.minLg_txt.grid(column=5, row=self.ridx+9, padx=1, pady=1, sticky="nsew")
                    self.minLg_btn = Button(self.string_based_frame, text="Add Minimal String Length:",command=lambda: self.add("minLength", self.minLg_txt.get()))
                    self.minLg_btn.grid(column=4, row=self.ridx+9, padx=1, pady=1, sticky="nsew")

                    self.CreateToolTip(self.minLg_txt,text="sh:minLength specifies the minimum string length of each\nvalue node that satisfies the condition.")

                    self.maxLg_txt = Entry(self.string_based_frame, validate='key', validatecommand=self.vcmd_uint)
                    self.maxLg_txt.grid(column=5, row=self.ridx+8, padx=1, pady=1, sticky="nsew")
                    self.maxLg_btn = Button(self.string_based_frame, text="Add Maximal String Length:",command=lambda: self.add("maxLength", self.maxLg_txt.get()))
                    self.maxLg_btn.grid(column=4, row=self.ridx+8, padx=1, pady=1, sticky="nsew")

                    self.CreateToolTip(self.maxLg_txt,text="sh:maxLength specifies the maximum string length of each\nvalue node that satisfies the condition.")

                    self.pattern_txt = Entry(self.string_based_frame, validate='key', validatecommand=self.vcmd_regex)
                    self.pattern_txt.grid(column=5, row=self.ridx+7, padx=1, pady=1, sticky="nsew")
                    self.pattern_btn = Button(self.string_based_frame, text="Add RegEx Constraint:",command=self.addRegEx)
                    self.pattern_btn.grid(column=4, row=self.ridx+7, padx=1, pady=1, sticky="nsew")

                    self.CreateToolTip(self.pattern_txt,text="sh:pattern specifies a regular expression that each value node\nmatches to satisfy the condition. Additonal flags for the pattern can\noptionally be defined in a separate pop-up window.")

                    self.langIn_btn = Button(self.string_based_frame, text="Define Language Tag(s)",command=self.openlangView)
                    self.langIn_btn.grid(column=4,columnspan=2,row=self.ridx+10, padx=1, pady=1, sticky="nsew")

                    self.CreateToolTip(self.langIn_btn,text="The condition specified by sh:languageIn is that the allowed\nlanguage tags for each value node are limited by a given list of\nlanguage tags.")

                    self.uniqueLang_state = BooleanVar()
                    self.uniqueLang = Checkbutton(self.string_based_frame, text='Add Unique Language Constraint', var=self.uniqueLang_state, onvalue=True, offvalue=False,command = self.toggleUniqueLang)
                    self.uniqueLang.grid(column=4, columnspan=2, row=self.ridx+6, padx=1, pady=1, sticky="nsew")

                    self.CreateToolTip(self.uniqueLang,text="The property sh:uniqueLang can be set to true to specify that\nno pair of value nodes may use the same language tag.")

                    self.hasStringDtype = True
    
    def addRegEx(self):
        self.add("pattern", self.pattern_txt.get())
        if len(self.pattern_txt.get()) != 0:
            FlagsView(self)
    
    def toggleUniqueLang(self):
        self.add("uniqueLang", str(self.uniqueLang_state.get()).lower(), self.uniqueLang_state.get())
    
    def openlangView(self):
        LanguageView(self)
    
    def newWindow(self,type="",type_value="",openNodeConstraint=False):
        self.nested_ctr += 1
        if not openNodeConstraint:
            #qualified counts can always be updated/removed
            self.add(type,type_value)
            #new window is only opened for the first time, property shapes may have only one qualified value shape
            if not self.contains("qualifiedValueShape") and len(type_value) != 0:
                self.qvs_disjoint['state'] = NORMAL
                label="_:"+"inner_shape"+str(self.nested_ctr)

                self.add("qualifiedValueShape",label)
                InnerShapeView(self, label)
        #node constraints have no cardinalities or other parameters
        else:
            label = "_:"+"inner_shape"+str(self.nested_ctr)
            self.add("node",label)
            InnerShapeView(self, label, True)

    def finalize(self):
        inner_shape = self.shapes_window.get(1.0,END)
        outer_shape = self.master.shapes_window.get(1.0,END)

        full_shape = "\n#".join((outer_shape+"#inner shape with label "+self.label+"\n"+inner_shape).split("#"))

        self.master.shapes_window.delete(1.0,END)
        self.master.shapes_window.insert(INSERT,full_shape)
        self.master.nested_ctr = self.nested_ctr
        self.destroy()

class InnerShapeView(Toplevel,App):
    def __init__(self, master=None, label=None, isNodeConstraint=False,logicalType=None,logicalView=None):
        #configure child window
        super().__init__(master = master)
        self.name = "Child"
        self.nested_ctr = master.nested_ctr
        self.indentation="\t\t"
        self.possible_properties = []
        self.logical_type =logicalType
        self.logicalView = logicalView
        self.title("Define Inner Shape")
        self.resizable(0,0)

        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.undo)

        #set windows theme
        self.style = ttk.Style(self)
        self.style.theme_use('winnative')

        self.inp_dict = master.inp_dict

        #copy relevant graphs and data from master
        self.dm = master.dm
        self.label = label
        self.isNodeConstraint = isNodeConstraint
        self.range_query = master.range_query
        self.path_query = master.path_query
        self.datatype_query = master.datatype_query
        self.object_query = master.object_query
        self.property_iri = master.property_iri
        self.targetMode = "class"
        self.raw_properties = master.raw_properties
        self.hasNumericalDtype = False
        self.hasStringDtype = False

        #here the class list corresponds to the ranges of the selected property of the master window
        self.raw_classes = [r["range"] for r in self.dm.ont_graph.query(self.range_query, initBindings={'property': self.property_iri})]
        self.class_list = [re.sub(".*#","",cstring) for cstring in self.raw_classes]

        #self.display_class_list = [c + " ("+FunctionManager.get_namespace(self.inp_dict,self.raw_classes,c)+")" for c in self.class_list]

        self.display_class_list = []
        for c in self.class_list:
            for i in range(self.class_list.count(c)):
                self.display_class_list.append(c + " ("+FunctionManager.get_namespace(self.inp_dict,self.raw_classes,c,i)+")")
                self.class_list.remove(c)

        #because inner shapes can also be property shapes we add 'None' to the list for that case, except for sh:node which can only be a value node
        if not self.isNodeConstraint:
            self.display_class_list.append(str(None))

        self.target_frame = LabelFrame(self, text='Target and Property Definitions')
        self.target_frame.grid(column=0, columnspan=2,row=0,rowspan=2, padx=1, pady=1, sticky="nsew")

        self.target_frame.grid_columnconfigure(index=0,weight=1)
        self.target_frame.grid_columnconfigure(index=1,weight=1)

        #add label and autocomplete combobox for the targets
        self.target_lbl = Label(self.target_frame, text="Select Class Target:")
        self.target_lbl.grid(column=0, row=0, padx=1, pady=1, sticky="nsew")


        self.target_combo = AutocompleteCombobox(self.target_frame,completevalues=self.display_class_list)
        self.target_combo.bind("<<ComboboxSelected>>",self.createInnerPathCombo)
        self.target_combo.grid(column=1, row=0, padx=1, pady=1, sticky="nsew")

        self.master.CreateToolTip(self.target_combo,text="Here you can select the classes whose instances are to be restricted. In\naddition, in some cases the option 'None' can be selected if an inner\nPropertyShape is to be created instead of an inner NodeShape.")

        self.shapes_frame = LabelFrame(self, text='Shape In Progress')
        self.shapes_frame.grid(column=2,columnspan=4, row=0,rowspan=7, padx=1, pady=1, sticky="nsew")

        self.shapes_frame.grid_columnconfigure(index=2,weight=1)
        self.shapes_frame.grid_columnconfigure(index=3,weight=1)
        self.shapes_frame.grid_columnconfigure(index=4,weight=1)
        self.shapes_frame.grid_columnconfigure(index=5,weight=1)

        #window for the shapes in progress
        self.shapes_window = scrolledtext.ScrolledText(self.shapes_frame,height=15)
        self.shapes_window.bind("<Key>", lambda e: self.master.ctrlEvent(e))
        self.shapes_window.grid(column=2,columnspan=4,row=0,rowspan=6, padx=1, pady=1)

        self.mainloop()

    def createInnerPathCombo(self,event):

        #if a class was chosen this means we create a node shape and we can basically copy superclass method
        if self.target_combo.get() != str(None):
            self.name = "NodeShapeChild"
            super().createPathCombo(event)

        #if class = None, this means we create a property shape, which from the path entry on, is the same as above
        else:
            self.name = "PropertyShapeChild"
            #self.targetMode=""
            super().createPathCombo(event)
    
    def undo(self):
        if self.logical_type == None:
            if messagebox.askokcancel("Nested Shape Removal", "Do you want to remove the current Nested Shape from the parent window and return there ?"):
                #remove triples from property shape of parent window
                self.shapes_window = self.master.shapes_window

                if not self.isNodeConstraint:
                    self.master.remove("qualifiedMinCount")
                    self.master.remove("qualifiedMaxCount")
                    self.master.remove("qualifiedValueShapesDisjoint")
                    self.master.remove("qualifiedValueShape")
                    self.master.qminc_txt.delete('0', 'end')
                    self.master.qmaxc_txt.delete('0', 'end')
                    self.master.qvs_disjoint['state'] = DISABLED

                else:
                    self.master.remove("node")
        else:
            self.logicalView.undo_lc(True)

        #reduce nested counter by 1
        self.master.nested_ctr = self.nested_ctr -1

        #finally close the toplevel window
        self.destroy()

class ValidationView(Toplevel):
    def __init__(self, master=None):
        #configure validation view
        super().__init__(master = master)
        self.title("SHACL Editor - Rule Execution")
        self.resizable(0,0)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        #set windows theme
        self.style = ttk.Style(self)
        self.style.theme_use('winnative')

        width = str(int(self.master.winfo_width()))
        #height= str(int(0.25*self.master.winfo_height()))

        self.config(width=width)


        self.dm = master.dm

        #create a copy of the shapes graph to avoid clashes when this view is closed and re-opened later
        self.shapes_graph = Graph().parse(data=self.dm.shapes_graph.serialize(format="turtle"))
        self.inst_graph = Graph()

        self.shapes_frame = LabelFrame(self, text='Shapes Graph')
        self.shapes_frame.grid(column=0, columnspan=3,row=0,rowspan=2, padx=1, pady=1)

        #window on the left side for the shapes graph
        self.shapes_graph_window = scrolledtext.ScrolledText(self.shapes_frame,height=10,width=55)
        self.shapes_graph_window.bind("<Key>", lambda e: self.master.ctrlEvent(e))
        self.shapes_graph_window.grid(column=0,columnspan=3,row=0, padx=1, pady=1)

        #if rules were created by the user it is inserted into the window
        if len(self.master.shapes_graph_str) != 0:
            self.shapes_graph_window.insert(INSERT,self.shapes_graph.serialize(format="turtle"))
            
        #in any case additional external shapes can be added 
        self.add_external_shapes = Button(self.shapes_frame, text="Choose Workfolder", command = self.addExternalShapes)
        self.add_external_shapes.grid(column=2,row=1, padx=1, pady=1)

        #also astrea shapes can be added just like external shapes
        self.add_astrea_shapes = Button(self.shapes_frame, text="Add Astrea Shapes", command = self.addAstreaShapes)
        self.add_astrea_shapes.grid(column=1,row=1, padx=1, pady=1)

        #adownload shapes button
        self.download_shapes = Button(self.shapes_frame, text="Download", command = self.downloadShapesGraph)
        self.download_shapes.grid(column=0,row=1, padx=1, pady=1)

        self.instance_frame = LabelFrame(self, text='Data Graph')
        self.instance_frame.grid(column=3, columnspan=2,row=0,rowspan=2, padx=1, pady=1)

        #window on the right side for the instance data after it was uploaded
        self.instance_graph_window = scrolledtext.ScrolledText(self.instance_frame,height=10,width=55)
        self.instance_graph_window.bind("<Key>", lambda e: self.master.ctrlEvent(e))
        self.instance_graph_window.grid(column=3,columnspan=2,row=0, padx=1, pady=1)

        self.add_instance_data = Button(self.instance_frame, text="Choose Workfolder", command = self.addInstanceData)
        self.add_instance_data.grid(column=3,row=1, padx=1, pady=1)

        #adownload instance button
        self.download_shapes = Button(self.instance_frame, text="Download", command = self.downloadDataGraph)
        self.download_shapes.grid(column=4,row=1, padx=1, pady=1)

        #button to execute the shapes on the data graph
        self.execution_btn = Button(self, text="Execute Rules", state=DISABLED, command = self.executeRules)
        self.execution_btn.grid(column=0,columnspan=5,row=2, padx=1, pady=1)

        self.mainloop()
    
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()

    def addExternalShapes(self):
        
        shapes_directory = askdirectory(title="Choose Directory containing all the external Shapes")
        #parse all the shapes inside the directory 
        for shapes_file_path in os.listdir(shapes_directory):
            self.shapes_graph.parse(shapes_directory+"/"+shapes_file_path)

        self.shapes_graph_window.delete(1.0,END)
        self.shapes_graph_window.insert(INSERT,self.shapes_graph.serialize(format="turtle"))

    def addAstreaShapes(self):
        if len(self.dm.ont_graph) == 0:
            ontology_directory = askdirectory(title="Choose Directory containing all the Ontologies")
            #parse all the ontologies inside the directory 
            for ontology_file_path in os.listdir(ontology_directory):
                self.dm.parse_ontologies(ontology_directory+"/"+ontology_file_path)
        
        if len(self.dm.ont_graph) != 0:
            #get and parse the astrea shapes, update the window after it and deactivate the button
            astrea_shapes = FunctionManager.getAstreaShapes(self.dm.ont_graph)

            astrea_graph = Graph().parse(astrea_shapes)

            name = URIRef("http://www.w3.org/ns/shacl#name")
            descr = URIRef("http://www.w3.org/ns/shacl#description")
            ps = URIRef("http://www.w3.org/ns/shacl#PropertyShape")
            pa = URIRef("http://www.w3.org/ns/shacl#path")
            minCount = URIRef("http://www.w3.org/ns/shacl#minCount")
            maxCount = URIRef("http://www.w3.org/ns/shacl#maxCount")

            astrea_graph.remove((None,RDFS.label,None))
            astrea_graph.remove((None,RDFS.isDefinedBy,None))
            astrea_graph.remove((None,name,None))
            astrea_graph.remove((None,descr,None))

            #pyshacl.errors.ShapeLoadError: A shape defined as a PropertyShape must be the subject of a 'sh:path' predicate
            valid_property_shapes_triples = list(astrea_graph.triples((None,pa,None)))
            property_shapes_triples = list(astrea_graph.triples((None,RDF.type,ps)))

            non_valid_property_shapes = [i[0] for i in property_shapes_triples if [j[0] for j in valid_property_shapes_triples if j[0] == i[0]] == []]

            #removing non-valid property shapes according to the pyshacl processor 
            for i in non_valid_property_shapes:
                astrea_graph.remove((i,None,None))
                astrea_graph.remove((None,None,i))
            
            #pyshacl.errors.ConstraintLoadError: Counts must be a literal with datatype xsd:integer but astrea uses xsd:NonNegativeInteger
            minCount = URIRef("http://www.w3.org/ns/shacl#minCount")
            maxCount = URIRef("http://www.w3.org/ns/shacl#maxCount")
            qualMinCount = URIRef("http://www.w3.org/ns/shacl#qualifiedMinCount")
            qualMaxCount = URIRef("http://www.w3.org/ns/shacl#qualifiedMaxCount")

            counts = [minCount,maxCount,qualMinCount,qualMaxCount]

            count_triples = [list(astrea_graph.triples((None,count,None))) for count in counts]

            count_triples = list(set([item for sublist in count_triples for item in sublist]))

            for i in count_triples:
                new_object = Literal(int(i[2]))
                astrea_graph.remove((i[0],i[1],i[2]))
                astrea_graph.add((i[0],i[1],new_object))
            
            #pyshacl.errors.ConstraintLoadError: NodeKindConstraintComponent must have at most one sh:nodeKind predicate

            nodeKind = URIRef("http://www.w3.org/ns/shacl#nodeKind")

            nodeKind_triples = list(astrea_graph.triples((None,nodeKind,None)))
            nodeKind_subjects = [i[0] for i in nodeKind_triples]
            nodeKind_multiplicity = [nodeKind_subjects.count(s) for s in nodeKind_subjects]
            invalid_subjects = list(set([nodeKind_subjects[i] for i in range(len(nodeKind_subjects)) if nodeKind_multiplicity[i] > 1]))

            for i in invalid_subjects:
                for j in nodeKind_triples:
                    if j[0] == i:
                        #always keep the more generic nodeKind constraint
                        if "Or" not in j[2]:
                            astrea_graph.remove((i,j[1],j[2]))
            
            #since classes and object propertiy values can be blank nodes or iris the objects for these kind of constraints also have to be changed

            iri = URIRef("http://www.w3.org/ns/shacl#IRI")
            bnode_or_iri = URIRef("http://www.w3.org/ns/shacl#BlankNodeOrIRI")

            iri_triples = list(astrea_graph.triples((None,nodeKind,iri)))

            for i in iri_triples:
                astrea_graph.remove((i[0],i[1],i[2]))
                astrea_graph.add((i[0],i[1],bnode_or_iri))
            
            #cardinality clash detection between own shapes and astrea shapes

            targetClass = URIRef("http://www.w3.org/ns/shacl#targetClass")
            prop = URIRef("http://www.w3.org/ns/shacl#property")

            astrea_ns_triples = list(astrea_graph.triples((None,targetClass,None)))

            own_ns_triples = list(self.shapes_graph.triples((None,targetClass,None)))

            for i in astrea_ns_triples:
                astrea_class_target = i[2]
                
                astrea_property_shapes_list = list(astrea_graph.triples((i[0],prop,None)))

                if len(astrea_property_shapes_list) != 0:

                    astrea_property_shape = astrea_property_shapes_list[0][2]
                    astrea_path = list(astrea_graph.triples((astrea_property_shape,pa,None)))[0][2]
                    astrea_counts = [list(astrea_graph.triples((astrea_property_shape,count,None))) for count in counts]
                    astrea_counts = list(set([item for sublist in astrea_counts for item in sublist]))

                    for j in own_ns_triples:

                        own_class_target = j[2]
                        own_property_shapes_list = list(self.shapes_graph.triples((j[0],prop,None)))

                        if len(own_property_shapes_list) != 0:

                            own_property_shape = own_property_shapes_list[0][2]
                            own_path = list(self.shapes_graph.triples((own_property_shape,pa,None)))[0][2]
                            own_counts = [list(self.shapes_graph.triples((own_property_shape,count,None))) for count in counts]
                            own_counts = list(set([item for sublist in own_counts for item in sublist]))

                            if astrea_class_target == own_class_target and astrea_path == own_path:
                                for k in astrea_counts:
                                    for l in own_counts:
                                        if k[1] == l[1] and k[2] != l[2]:
                                            
                                            # create astrea subgraph
                                            astrea_subgraph = Graph()
                                            astrea_subgraph.bind("sh", "http://www.w3.org/ns/shacl#")
                                            # add all relevant triples 
                                            astrea_subgraph += astrea_graph.triples((i[0], None, None))
                                            astrea_subgraph += astrea_graph.triples((astrea_property_shape, None, None))

                                            #create own subgraph
                                            own_subgraph = Graph()
                                            own_subgraph.bind("sh", "http://www.w3.org/ns/shacl#")
                                            # add all relevant triples 
                                            own_subgraph += self.shapes_graph.triples((j[0], None, None))
                                            own_subgraph += self.shapes_graph.triples((own_property_shape, None, None))

                                            msg = str(k[1])+" Clash found between the following two subgraphs:\n\n---Astrea Subgraph---\n\n"+astrea_subgraph.serialize(format='turtle')+"\n\n---Your Subgraph---\n\n"+own_subgraph.serialize(format='turtle')
                                            msg += "Do you want to keep yours (Click Yes) or do you want to take the cardinalities from the Astrea Tool (Click No) ?"

                                            answer = askyesno(title="Cardinality Clash", message=msg)

                                            if answer:
                                                astrea_graph.remove(k)
                                            elif not answer:
                                                self.shapes_graph.remove(l)
                                                
            self.shapes_graph.parse(data=astrea_graph.serialize(format="turtle"))
            self.shapes_graph_window.delete(1.0,END)
            self.shapes_graph_window.insert(INSERT,self.shapes_graph.serialize(format="turtle"))
            self.add_astrea_shapes['state'] = DISABLED

    def addInstanceData(self):
        
        instances_directory = askdirectory(title="Choose Directory containing all the Instances")
        #parse all the instances inside the directory 
        for instance_file_path in os.listdir(instances_directory):
            self.inst_graph.parse(instances_directory+"/"+instance_file_path)
        
        if len(self.inst_graph) != 0:
            self.execution_btn['state'] = NORMAL
            self.instance_graph_str = self.inst_graph.serialize(format="turtle")
            self.instance_graph_window.delete(1.0,END)
            self.instance_graph_window.insert(INSERT,self.instance_graph_str)
    
    def executeRules(self):
        r = validate(data_graph= self.inst_graph,shacl_graph=self.shapes_graph)
        
        conforms, self.results_graph, results_text = r

        self.validation_frame = LabelFrame(self, text='Validation Report')
        self.validation_frame.grid(column=0, columnspan=5,row=3,rowspan=2, padx=5, pady=5)

        #write the report into a result window
        self.validation_report_window = scrolledtext.ScrolledText(self.validation_frame,height=10,width=100)
        self.validation_report_window.bind("<Key>", lambda e: self.master.ctrlEvent(e))
        self.validation_report_window.grid(column=0,columnspan=5,row=3, padx=1, pady=1)
        self.validation_report_window.insert(INSERT,self.results_graph.serialize(format="turtle"))

        #button to download the resulting validation report
        self.download_report = Button(self.validation_frame, text="Download Validation Report", command = self.downloadReport)
        self.download_report.grid(column=0,columnspan=5,row=4, padx=1, pady=1)

        if conforms:
            messagebox.showinfo(title="No Violations found",message=results_text)
        else:
            messagebox.showinfo(title="Violations found",message=results_text)
    
    def downloadReport(self):
        file = asksaveasfile(defaultextension=".ttl")
        file.write(self.results_graph.serialize(format="turtle"))
    
    def downloadDataGraph(self):
        if len(self.inst_graph) != 0:
            file = asksaveasfile(defaultextension=".ttl")
            file.write(self.inst_graph.serialize(format="turtle"))
        else:
            messagebox.showerror(title="Empty Data Graph", message = "The data graph is empty ! ")
    
    def downloadShapesGraph(self):
        if len(self.shapes_graph) != 0:
            file = asksaveasfile(defaultextension=".ttl")
            file.write(self.shapes_graph.serialize(format="turtle"))
        else:
            messagebox.showerror(title="Empty Shapes Graph", message = "The shapes graph is empty ! ")


class ConfigurationView(Toplevel):
    
    def __init__(self, master=None):
        #configure configuration view
        super().__init__(master = master)
        self.title("SHACL Editor - Prefix Configuration")
        self.resizable(0,0)
        self.grab_set()

        #set windows theme
        self.style = ttk.Style(self)
        self.style.theme_use('winnative')

        width = str(int(0.5*self.master.winfo_width()))
        #height= str(int(0.25*self.master.winfo_height()))

        self.config(width=width)

        self.grid_columnconfigure(index=0,minsize=int(0.5*self.master.winfo_width()))

        #informative text 
        self.config_info = Message(self,width=int(0.4*self.master.winfo_width()),text="You need to configure all prefixes and namespaces necessary for parsing the shapes graph as key-value pairs. The sh: prefix should always be kept plus all the prefixes for the ontology constructs (and possibly also for the concrete instances) that you want to constrain.")
        self.config_info.grid(column=0,row=0,padx=5, pady=5)

        #window in the middle for the prefix dictionary
        self.prefix_window = scrolledtext.ScrolledText(self,width=40,height=10)
        self.prefix_window.grid(column=0,row=1, padx=5, pady=5)

        #insert the default values
        self.prefix_window.insert(INSERT,json.dumps(self.master.inp_dict))


        #button for changing/adding to the default ontologies bot,cto,ls
        self.add_prefix_btn = Button(self, text="Save Changes", command = self.setPrefixes)
        self.add_prefix_btn.grid(column=0,row=2, padx=5, pady=5)

        self.mainloop()

    def setPrefixes(self):
        if self.checkJson() == True:
            new_inp_dict = json.loads(self.prefix_window.get(1.0,END))
            if new_inp_dict != self.master.inp_dict:
                self.master.inp_dict = new_inp_dict

                #always append the SHACL prefix after it was updated
                self.master.inp_dict["sh"] = "http://www.w3.org/ns/shacl#"

                messagebox.showinfo(title="Changes Saved",message="Changes saved successfully !")
                self.destroy()
            else:
                messagebox.showerror(title="Missing Changes",message="No Changes have been made !")
        else:
            messagebox.showerror(title="JSONDecodeError",message="The input you provided is not a valid json and can not be saved !")
    
    def checkJson(self):
        try:
            json.loads(self.prefix_window.get(1.0,END))
        except (JSONDecodeError):
            return False
        
        return True

class IgnoredPropertiesView(Toplevel):
    #a view for defining ignored properties
    def __init__(self, master=None):
        super().__init__(master = master)
        self.title("Set Ignored Properties")
        self.resizable(0,0)
        self.grab_set()

        #set windows theme
        self.style = ttk.Style(self)
        self.style.theme_use('winnative')

        width = str(int(0.5*self.master.winfo_width()))
        #height= str(int(0.25*self.master.winfo_height()))

        self.config(width=width)

        self.grid_columnconfigure(index=0,minsize=int(0.5*self.master.winfo_width()))

        self.ignored_properties = []
        self.c_state_list = []

        self.info_lbl = Message(self,width=int(0.4*self.master.winfo_width()), text="Here you can optionally define the ignored properties for the current node shape. If you select None or if you close this window no ignored properties will be added.")
        self.info_lbl.grid(row=0,column=0, padx=5, pady=5)

        self.idx = int()

        if self.master.possible_properties == []:
            
            for i, property in enumerate(self.master.display_properties_list):

                self.c_state_list.append(tk.BooleanVar())
                c = Checkbutton(self, text=property, var=self.c_state_list[i], onvalue=True, offvalue=False)
                c.grid(row=i+1,column=0, padx=5, pady=5)
                self.idx=i    
        else:
            for i, property in  enumerate(self.master.possible_properties):
                
                self.c_state_list.append(tk.BooleanVar())
                c = Checkbutton(self, text=property, var=self.c_state_list[i], onvalue=True, offvalue=False)
                c.grid(row=i+1,column=0, padx=5, pady=5)
                self.idx=i
                
        self.submit_btn = Button(self, text="Submit", command = self.setIgnoredProperties)
        self.submit_btn.grid(row=self.idx+2,column=0, padx=5, pady=5)


    def setIgnoredProperties(self):
        constraint_type = "ignoredProperties"

        for r in range(0,self.idx+1):
            if self.c_state_list[r].get() == True:
                self.ignored_properties.append(self.grid_slaves(column=0,row=r+1)[0].cget("text"))

        if self.ignored_properties != []:
            if len(self.ignored_properties) == 1:
                ns = self.ignored_properties[0].split("(")[1].split(")")[0] +":"
                c = self.ignored_properties[0].split(" ")[0]
                constraint_value = "( "+ns +c+" )"
            else:
                constraint_value = "( "
                for p in self.ignored_properties:
                    ns = p.split("(")[1].split(")")[0] +":"
                    p = ns + p.split(" ")[0]
                    constraint_value += p +" "
                constraint_value += ")"
            self.master.add(constraint_type,constraint_value,target="NodeShape")

        else:
           self.master.remove(constraint_type,target="NodeShape")

        self.destroy()     

class LanguageView(Toplevel):

    #a view for defining language tags
    def __init__(self, master=None):
        super().__init__(master = master)
        self.title("Set Language Tag(s)")
        self.resizable(0,0)
        self.grab_set()

        self.master = master

        #set windows theme
        self.style = ttk.Style(self)
        self.style.theme_use('winnative')

        width = str(int(0.5*self.master.winfo_width()))
        #height= str(int(0.25*self.master.winfo_height()))

        self.config(width=width)

        self.grid_columnconfigure(index=0,minsize=int(0.125*self.master.winfo_width()))
        self.grid_columnconfigure(index=1,minsize=int(0.125*self.master.winfo_width()))
        self.grid_columnconfigure(index=2,minsize=int(0.125*self.master.winfo_width()))
        self.grid_columnconfigure(index=3,minsize=int(0.125*self.master.winfo_width()))


        #dictionary containing the codes as keys and the countries as values
        self.RFC5646_LANGUAGE_TAGS = FunctionManager.getlangTags()
        self.chosen_values = []
        self.constraint_value = str()
        self.constraint_type = "languageIn"

        #the values of the tag dictionary are used for an autocomplete combobox on the top
        self.lang_lbl = Label(self, text="Select Language Tag to be added:")
        self.lang_lbl.grid(column=1, row=0,sticky=tk.E, padx=5, pady=5)
        self.lang_combo = AutocompleteCombobox(self,completevalues=list(self.RFC5646_LANGUAGE_TAGS.values()))

        self.lang_combo.bind("<<ComboboxSelected>>",self.addLangTag)
        self.lang_combo.grid(column=2, row=0,sticky=tk.W, padx=5, pady=5)

        self.master.CreateToolTip(self.lang_combo,text="You can select as many tags as you want one after the other.\nWhen you are done just click the button below to add them to\nthe property shape.")

        #below is a textbox where the chosen tags are provided as a SHACL List, with a confirmation button
        self.tags_window = Text(self)
        self.tags_window.bind("<Key>", lambda e: self.master.ctrlEvent(e))
        self.tags_window.grid(column=1,columnspan=2,row=1, padx=5, pady=5)
        #initialized with an empty list
        self.tags_window.insert(INSERT,"( )")

        #button for confirming the selections and adding them to the master window
        self.submit_tags = Button(self, text="Add Tags", command=self.submitTags)
        self.submit_tags.grid(column=0,columnspan=4, row=2, padx=5, pady=5)

    
    def addLangTag(self,event):
        #cur str is everything except the last character (the closing bracket)
        cur_str = self.tags_window.get(1.0,'end-2c')

        #find the key (tag) of the selected value
        key = [key for key,value in self.RFC5646_LANGUAGE_TAGS.items() if value==self.lang_combo.get()][0]

        #concatenate the new key
        self.constraint_value = cur_str + '"'+key+'" )'

        #updating the window for the user to keep track of the selection
        self.tags_window.delete(1.0,END)
        self.tags_window.insert(INSERT,self.constraint_value)

        #tags that were already selected are removed from the completion list
        self.chosen_values.append(self.lang_combo.get())
        self.lang_combo.set_completion_list([i for i in list(self.RFC5646_LANGUAGE_TAGS.values()) if i not in self.chosen_values])
    
    def submitTags(self):

        if self.chosen_values != []:
            self.master.add(self.constraint_type,self.constraint_value)
        else:
            self.master.remove(self.constraint_type)
        
        self.destroy()

class FlagsView(Toplevel):

    #a view for defining regex flags
    def __init__(self, master=None):
        super().__init__(master = master)
        self.title("Set RegEx Flag(s)")
        self.resizable(0,0)
        self.grab_set()

        #set windows theme
        self.style = ttk.Style(self)
        self.style.theme_use('winnative')

        width = str(int(0.5*self.master.winfo_width()))
        #height= str(int(0.25*self.master.winfo_height()))

        self.config(width=width)

        self.grid_columnconfigure(index=0,minsize=int(0.5*self.master.winfo_width()))


        self.info_lbl = Message(self,width=int(0.4*self.master.winfo_width()),text="Here you can optionally select RegEx Flags for the pattern you just entered. You can find more information about the flags on the link below.")
        self.info_lbl.grid(column=0,row=0)

        self.info_link = Label(self,text="https://www.w3.org/TR/xpath-functions/#flags",fg="blue")
        self.info_link.bind("<Button-1>",lambda e: self.openLink("https://www.w3.org/TR/xpath-functions/#flags"))
        self.info_link.grid(column=0,row=1)

        self.flags = FunctionManager.getFlags()
        self.nr_of_flags = len(self.flags)
        self.flag_keys = list(self.flags.keys())
        self.flag_values = list(self.flags.values())
        self.selected_flags = []
        self.c_state_list = []

        for i in range(self.nr_of_flags):
            self.c_state_list.append(tk.BooleanVar())
            c = Checkbutton(self, text=self.flag_values[i], var=self.c_state_list[i], onvalue=True, offvalue=False)
            c.grid(row=i+2,column=0, padx=5, pady=5)
        
        self.submit_flags = Button(self, text="Add Flags to the Node Shape", command=self.submitFlags)
        self.submit_flags.grid(column=0, row=self.nr_of_flags+2, padx=5, pady=5)
    
    def openLink(self, url):
        webbrowser.open_new(url)

    def submitFlags(self):
        constraint_type = "flags"
        constraint_value = ""
        for i in range(self.nr_of_flags):
            if self.c_state_list[i].get() == True:
                self.selected_flags.append(self.flag_keys[i])
        
        if self.selected_flags != []:
            for f in self.selected_flags:
                constraint_value += f
            constraint_value = '"'+constraint_value+'"'
            self.master.add(constraint_type,constraint_value)
        else:
            self.master.remove(constraint_type)
        
        self.destroy()

class TargetNodeView(Toplevel):
    def __init__(self, master=None):
        super().__init__(master = master)

        self.title("Definition Of Target Node(s)")
        self.resizable(0,0)
        self.grab_set()

        #set windows theme
        self.style = ttk.Style(self)
        self.style.theme_use('winnative')

        self.master = master
        self.indentation="\t"

        width = str(int(0.5*self.master.winfo_width()))
        #height= str(int(0.25*self.master.winfo_height()))

        self.config(width=width)

        self.grid_columnconfigure(index=0,minsize=int(0.5*self.master.winfo_width()))

        self.info_txt = Message(self,width=int(0.4*self.master.winfo_width()),text="If you do not want to constrain the whole class, but one or more instances of the class please provide  the prefixed instances as a comma-separated list below. If you want to constrain the whole class, then just close this window.")
        self.info_txt.grid(column=0,row=0, padx=5, pady=5)

        self.entry = Entry(self)
        self.entry.grid(column=0,row=1, padx=5, pady=5)

        self.btn = Button(self,text="Add Target Node(s)",command=self.replace)
        self.btn.grid(column=0,row=2,padx=5, pady=5)
    
    def replace(self):
        if len(self.entry.get()) != 0:
            self.master.add('targetNode',self.entry.get(),True,'NodeShape')
            if self.master.contains("targetNode","NodeShape"):
                self.master.remove('targetClass','NodeShape')
                self.master.remove('nodeKind','NodeShape')
                self.destroy()


class PropertyPairView(Toplevel):
    #a view for defining property pair constraints
    def __init__(self, master=None):
        super().__init__(master = master)
        self.title("Definition Of Property Pair Constraints")
        self.resizable(0,0)
        self.grab_set()

        #set windows theme
        self.style = ttk.Style(self)
        self.style.theme_use('winnative')

        self.master = master

        width = str(int(0.5*self.master.winfo_width()))
        #height= str(int(0.25*self.master.winfo_height()))

        self.config(width=width)

        self.grid_columnconfigure(index=0,minsize=int(0.25*self.master.winfo_width()))
        self.grid_columnconfigure(index=1,minsize=int(0.25*self.master.winfo_width()))

        self.info_lbl = Message(self,width=int(0.4*self.master.winfo_width()),text="Here you can select and add property pair constraints for the current property shape, On the left side you can select the constraint type and on the right side the corresponding property as the object of that constraint type.")
        self.info_lbl.grid(column=0,columnspan=2,row=0, padx=5, pady=5)

        self.type_combo = AutocompleteCombobox(self,completevalues=["equals","disjoint","lessThan","lessThanOrEquals"])
        self.type_combo.grid(column=0,row=1, padx=5, pady=5)

        #the values are all properties except the one that is currently selected
        value_list = [i for i in self.master.display_properties_list if i != self.master.path_combo.get()]
        
        self.value_combo = AutocompleteCombobox(self,completevalues=value_list)
        self.value_combo.grid(column=1,row=1, padx=5, pady=5)

        self.submit_ppc = Button(self,text="Add Property Pair Constraint",command=self.addPPC)
        self.submit_ppc.grid(column=0,columnspan=2,row=2, padx=5, pady=5)

    
    def addPPC(self):
        if len(self.type_combo.get()) != 0:
            if len(self.value_combo.get()) != 0:
                ns = self.value_combo.get().split("(")[1].split(")")[0] +":"
                prop = self.value_combo.get().split(" ")[0]
                self.master.add(self.type_combo.get(),ns+prop)
            #empty value means resetting 
            else:
                self.master.remove(self.type_combo.get())

class LogicalConstraintView(Toplevel):
    #a view for defining property pair constraints
    def __init__(self, master=None):
        super().__init__(master = master)
        self.title("Definition Of Logical Constraints")
        self.resizable(0,0)
        self.grab_set()

        #set windows theme
        self.style = ttk.Style(self)
        self.style.theme_use('winnative')

        self.master = master
        self.idx = 0
        self.protocol("WM_DELETE_WINDOW", self.undo_lc)

        width = str(int(0.5*self.master.winfo_width()))
        #height= str(int(0.5*self.master.winfo_height()))

        self.config(width=width)
        
        self.grid_columnconfigure(index=0,minsize=int(0.25*self.master.winfo_width()),weight=1)
        self.grid_columnconfigure(index=1,minsize=int(0.25*self.master.winfo_width()),weight=1)

        self.info_lbl = Message(self,width=int(0.5*self.master.winfo_width()),text="First define the number of inner shapes and then choose the logical type of the constraint. After adding the constraint to the node shape you have to define each inner shape in a separate window by clicking on the corresponding buttons.")
        self.info_lbl.grid(column=0,columnspan=2,row=0, padx=5, pady=5, sticky='nsew')

        self.nr_lbl = Label(self,text="Number of inner Shapes")
        self.nr_lbl.grid(row=1,column=0, padx=5, pady=5, sticky='nsew')

        self.nr_entry = Entry(self,validate="key",validatecommand=self.master.vcmd_uint)
        self.nr_entry.grid(row=1,column=1, padx=5, pady=5, sticky='nsew')

        self.type_lbl =Label(self, text= "Type of logical constraint:")
        self.type_lbl.grid(row=2,column=0, padx=5, pady=5, sticky='nsew')

        types = ["not","and","or","xone"]

        #there should only be one value for each type
        self.type_value = AutocompleteCombobox(self,completevalues=[i for i in types if not self.master.contains("sh:"+str(i))])
        self.type_value.grid(row=2,column=1, padx=5, pady=5, sticky='nsew')

        self.confirm_lc = Button(self,text="Add Constraint",command=self.addLC)
        self.confirm_lc.grid(row=3,column=0,columnspan=2, padx=5, pady=5)
    
    def addLC(self): 
        if len(self.type_value.get()) != 0 and self.nr_entry.get() != str(0):
            self.label_list = []
            for i in range(int(self.nr_entry.get())):
                self.master.nested_ctr += 1
                label = "_:inner_shape"+str(self.master.nested_ctr)
                self.label_list.append(label)

                tmp_btn = Button(self,text="Define "+label,command= lambda i=i,label=label: self.openInnerShapesWindow(label,i))
                tmp_btn.grid(row=4+i,column=0,columnspan=2, padx=5, pady=5, sticky='nsew')

            if len(self.label_list) > 1:
                if self.type_value.get() == "not":
                    constraint_value = ",".join(self.label_list)
                    self.master.add("not",constraint_value)
                else:
                    constraint_value = "( "+" ".join(self.label_list) +" )"
                    self.master.add(self.type_value.get(),constraint_value)
            else:
                if self.type_value.get() == "not":
                    self.master.add("not",self.label_list[0])
                else:
                    self.master.add(self.type_value.get(),"( "+self.label_list[0]+" )")  
            
            self.confirm_lc['state'] = DISABLED
            self.nr_entry['state'] = DISABLED
            self.type_value['state'] = DISABLED

    def openInnerShapesWindow(self,label,i):
        #should only be defined once
        self.grid_slaves(row=4+i,column=0)[0]['state'] = DISABLED

        InnerShapeView(self.master,label,False,self.type_value.get(),self)
    
    def undo_lc(self,forced=False):
        if not forced:
            finished = True
        else:
            finished = False

        missing = 0

        if len(self.nr_entry.get()) != 0:
            for i in range(int(self.nr_entry.get())):
                if self.grid_slaves(row=3+i,column=0) != []:
                    if self.grid_slaves(row=3+i,column=0)[0]['state'] != DISABLED:
                        finished = False
                        missing += 1
        if finished:
            self.destroy()
        else:
            if messagebox.askokcancel("Missing Definitions", "If you leave without defining all inner shapes your changes will be undone. Are you sure ?"):
                self.master.remove(self.type_value.get())

                txt = self.master.shapes_window.get(1.0,END)

                #get all the seperate shapes and remove those with the labels in it, if they exist
                tmp_txt = txt.split("#")
                tmp_txt = [ i for i in tmp_txt if ([label for label in self.label_list if label in i] == [])]

                new_txt = "#".join(tmp_txt)

                #update the window and the counter
                self.master.shapes_window.delete(1.0,END)
                self.master.shapes_window.insert(INSERT,new_txt)

                self.master.nested_ctr -= int(self.nr_entry.get())

                self.destroy()

class ToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

if __name__ == "__main__":

    app = App()
    app.mainloop()
