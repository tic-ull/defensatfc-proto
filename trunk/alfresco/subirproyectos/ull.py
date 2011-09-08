import re
from subirproyectos.settings import *


def is_student (username):
   if re.match("alu\d{10}", username):
      return True
   else: 
      return False
      

def is_library_staff (username) :
   for bibliotecarios in LIBRARY_STAFF.values():
      if username in bibliotecarios:
         return True
   return False      
   
   
def is_faculty_staff (username) :
   for secretarios in FACULTY_STAFF.values():
      if username in secretarios:
         return True
   return False    
   
def get_faculties():
   return LIBRARY_STAFF.keys()
   
def get_faculty(username):
   if is_library_staff(username):
      return find_key(LIBRARY_STAFF, username)
   if is_faculty_staff(username):
      return find_key(FACULTY_STAFF, username)
      
def find_key (dic, val):
   for k, v in dic.iteritems(): 
      if val in v:
	return k
   
   
def is_professor(username):
   return not (is_student(username) or is_library_staff(username) or is_faculty_staff(username))