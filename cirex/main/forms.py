#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 10:47:15 2018

@author: kazeem
"""

from flask_wtf import FlaskForm
from wtforms import SubmitField, TextField, FileField
from flask_wtf.file import FileRequired, FileAllowed
from wtforms.validators import DataRequired

class retrieval_form(FlaskForm):
    retrieve_button = SubmitField("Retrieve citation records")
    
class exisitng_search_form(FlaskForm):
    search_name = TextField("Search title: ")
    searchbtn = SubmitField("Load search record")
    
class new_search_form(FlaskForm):
    search_id = TextField("Enter a name for this search: ")
    upload_button = SubmitField("Upload!")
    file = FileField(validators=[FileRequired(), FileAllowed(['txt', 'ris', 'csv'], "File type not allowed!")]) 


class processing_form(FlaskForm):
    process_button = SubmitField("Begin processing")
    
    
    
# =============================================================================
# class uploadForm(FlaskForm): 
#     chosen_file = FileField(validators=[FileRequired()]) 
# =============================================================================