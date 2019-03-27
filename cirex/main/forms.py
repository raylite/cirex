#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 10:47:15 2018

@author: kazeem
"""

from flask_wtf import FlaskForm
from wtforms import SubmitField, TextField, FileField
from flask_wtf.file import FileRequired, FileAllowed
from wtforms.validators import DataRequired, ValidationError
from cirex.models import Search

class retrieval_form(FlaskForm):
    retrieve_button = SubmitField("Retrieve citation records")
    
class exisitng_search_form(FlaskForm):
    search_name = TextField("Input name of search to retrieve: ", validators=[DataRequired()])
    searchbtn = SubmitField("Load search record")
    
    def validate_search_name(self, search_name):
        search = Search.query.filter_by(name = search_name.data).first()
        if search is None:
            raise ValidationError("The name you searched does not exist.")
    
class new_search_form(FlaskForm):
    search_name = TextField("Enter a name for this search: ", validators=[DataRequired()])
    file = FileField(validators=[FileRequired(), FileAllowed(['txt', 'ris', 'csv'], "File type not allowed!")]) 
    upload_button = SubmitField("Upload!")
    
    
    def validate_search_name(self, search_name):
        search = Search.query.filter_by(name = search_name.data).first()
        if search is not None:
            raise ValidationError("The name you entered already exist. You may retrieve its results by clicking the retrieve button or provide a new name.")


class processing_form(FlaskForm):
    process_button = SubmitField("Begin processing")
    
    
    
# =============================================================================
# class uploadForm(FlaskForm): 
#     chosen_file = FileField(validators=[FileRequired()]) 
# =============================================================================