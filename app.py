from flask import Flask, Response, session
from flask_session.__init__ import Session

import ifcopenshell
import ifcopenshell.api

from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

ifc_file = None

@app.route('/loadIfc')
def load_ifc():
    global ifc_file
    ifc_file = ifcopenshell.open("AC20-FZK-Haus.ifc")
    
    return Response("OK", status=200)

@app.route('/loadTemplate')
def load_template():
    session["template"] = ifcopenshell.open("template.ifc").to_string()
    
    return Response("OK", status=200)


@app.route('/addTemplateToObject')
def add_template_to_object():
    global ifc_file
    ifc_template = ifcopenshell.file.from_string(session["template"])
    
    object_step_id = 27421
    
    ifc_object = ifc_file.by_id(object_step_id)
    pset_template = ifc_template.by_id(1)
    
    pset_name = pset_template.Name
    property_templates = pset_template.HasPropertyTemplates

    properties = {}

    new_pset = ifcopenshell.api.run("pset.add_pset", ifc_file, product=ifc_object, name=pset_name)

    for prop_template in property_templates:
        prop_name = prop_template.Name
        prop_template_type = prop_template.TemplateType
        prop_measure_type = prop_template.PrimaryMeasureType


        if prop_template_type == "P_SINGLEVALUE":
            properties[prop_name] = ""
            ifc_value_entity = ifc_file.create_entity("IfcLabel", "")

        elif prop_template_type == "P_ENUMERATEDVALUE":
            enum_values = prop_template.Enumerators.EnumerationValues

            ifc_property_enumeration = ifc_file.create_entity(
                "IFCPROPERTYENUMERATION",
                Name=prop_name,
                EnumerationValues=enum_values,
            )

            ifc_value_entity = ifc_file.create_entity(
                "IFCPROPERTYENUMERATEDVALUE",
                Name=prop_name,
                EnumerationReference=ifc_property_enumeration,
                EnumerationValues=(
                    enum_values[0],
                ),  # TODO: EnumerationValues is optional in IFC4, but required in IFC2x3.  Need to handle this based on the current file schema
            )
    

        ifcopenshell.api.run("pset.edit_pset", ifc_file, pset=new_pset, properties={prop_name: ifc_value_entity})
    
    return Response("OK", status=200)

@app.route('/getProperties')
def get_properties():
    global ifc_file
    
    return Response("OK", status=200)