#-------------------------------------------------------------------------------
# Name:        course_name_converter
# Purpose:     Given a department code and course name, queries the sql 
#              database to find the number of the course. If the given 
#              combination of dept and course name does not exist, the course 
#              does not exist and convert_course_name_to_course_num returns None.
#              The code to generate word clouds and graphs uses course_num, so 
#              this helper function simplifies the output generation process.
#
# Author:      Lily Li
#
# Created:     03/09/2018
#-------------------------------------------------------------------------------


import sqlite3
import os

# Use this filename for the database
DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'reevaluations.db')


def convert_course_name_to_course_num(dept, course_name):
    '''
    If a user inputs a course_name, convert it to a course_num for the word cloud and graph code
    '''
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    r = c.execute("SELECT DISTINCT course_number FROM courses \
        WHERE dept = ? AND course = ?", (dept, course_name))
    course_num = list(r.fetchall()) # list of tuples
    if len(course_num) > 0:
        return course_num[0][0] # only return the first result, in the rare case 
        # the course went through a number change
    else:
        return None # the user inputted a dept and course name pair that isn't valid
