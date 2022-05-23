from os import mkdir, getcwd, path
import random,os,string

DATA_PATH = path.join(getcwd(), 'data')
EMPLOYEE = None
STUDENT = None
TECHDEPT = None
UNIQUE_NAME = 'AAAAAA'
DEPT_LIST = ["dept 1", "dept 2", "dept 3", "dept 4", "dept 5", "dept 6", "dept 7", "dept 8", "dept 9", "dept 10"]
UNIQUE_SSNUM = 1

# generate data
def generate():
    __open_files()
    __generate_Employee()
    __generate_Student()
    __generate_Techdept()

def __generate_Employee():
    global EMPLOYEE
    global STUDENT
    i = 0
    while i < 70000:
        EMPLOYEE.write(str(__get_next_ssnum()))
        EMPLOYEE.write("\t")
        EMPLOYEE.write(__get_next_unique_name())
        EMPLOYEE.write("\t")
        EMPLOYEE.write(__get_random_manager())
        EMPLOYEE.write("\t")
        EMPLOYEE.write(str(__get_random_dept()))
        EMPLOYEE.write("\t")
        EMPLOYEE.write(str(__get_random_integer()))
        EMPLOYEE.write("\t")
        EMPLOYEE.write(str(__get_random_integer()))
        EMPLOYEE.write("\n")
        i = i + 1
    while i < 30000:
        ssnum = __get_next_ssnum()
        name = __get_next_unique_name()
        # Employee part
        EMPLOYEE.write(str(ssnum))
        EMPLOYEE.write("\t")
        EMPLOYEE.write(name)
        EMPLOYEE.write("\t")
        EMPLOYEE.write(__get_random_manager())
        EMPLOYEE.write("\t")
        EMPLOYEE.write(__get_random_dept())
        EMPLOYEE.write("\t")
        EMPLOYEE.write(str(__get_random_integer()))
        EMPLOYEE.write("\t")
        EMPLOYEE.write(str(__get_random_integer()))
        EMPLOYEE.write("\n")
        # Student part
        STUDENT.write(str(ssnum))
        STUDENT.write("\t")
        STUDENT.write(name)
        STUDENT.write("\t")
        STUDENT.write(str(__get_random_course()))
        STUDENT.write("\t")
        STUDENT.write(str(__get_random_grade()))
        STUDENT.write("\n")
        i = i + 1
    EMPLOYEE.close()

def __generate_Student():
    global STUDENT
    i = 0
    while i < 70000:
        STUDENT.write(str(__get_next_ssnum()))
        STUDENT.write("\t")
        STUDENT.write(__get_next_unique_name())
        STUDENT.write("\t")
        STUDENT.write(str(__get_random_course()))
        STUDENT.write("\t")
        STUDENT.write(str(__get_random_grade()))
        STUDENT.write("\n")
        i = i + 1
    STUDENT.close()

def __generate_Techdept():
    global TECHDEPT
    global DEPT_LIST
    i = 0
    while i <= 9:
        TECHDEPT.write(DEPT_LIST[i])
        TECHDEPT.write("\t")
        TECHDEPT.write(__get_random_manager())
        TECHDEPT.write("\t")
        TECHDEPT.write(DEPT_LIST[i-1])
        TECHDEPT.write("\n")
        i = i + 1
    TECHDEPT.close()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~ code from stackoverflow ~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def increment_char(c):
    """
    Increment an uppercase character, returning 'A' if 'Z' is given
    """
    return chr(ord(c) + 1) if c != 'Z' else 'A'

def increment_str(s):
    lpart = s.rstrip('Z')
    if not lpart:  # s contains only 'Z'
        new_s = 'A' * (len(s) + 1)
    else:
        num_replacements = len(s) - len(lpart)
        new_s = lpart[:-1] + increment_char(lpart[-1])
        new_s += 'A' * num_replacements
    return new_s

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~ end ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def __open_files():
    global EMPLOYEE
    global STUDENT
    global TECHDEPT

    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)

    if os.path.exists(DATA_PATH+"/employee.tsv"):
        os.remove(DATA_PATH+"/employee.tsv")
    if os.path.exists(DATA_PATH+"/student.tsv"):
        os.remove(DATA_PATH+"/student.tsv")
    if os.path.exists(DATA_PATH+"/techdept.tsv"):
        os.remove(DATA_PATH+"/techdept.tsv")
    EMPLOYEE = open(DATA_PATH+"/employee.tsv","w+")
    STUDENT = open(DATA_PATH+"/student.tsv","w+")
    TECHDEPT = open(DATA_PATH+"/techdept.tsv","w+")

def __get_next_unique_name():
    global UNIQUE_NAME
    returnVal = UNIQUE_NAME
    UNIQUE_NAME = increment_str(UNIQUE_NAME)
    return UNIQUE_NAME

def __get_next_ssnum():
    global UNIQUE_SSNUM
    returnVal = UNIQUE_SSNUM
    UNIQUE_SSNUM = UNIQUE_SSNUM + 1
    return returnVal

def __get_random_manager():
    return ''.join(random.choice(string.ascii_uppercase) for x in range(6))

def __get_random_integer():
    return random.randint(1, 10000)

def __get_random_dept():
    if random.randint(0, 9) == 1:
        return DEPT_LIST[random.randint(0, 9)]
    else:
        return 'null'

def __get_random_course():
    return random.randint(1,100)

def __get_random_grade():
    return random.randint(1,5)
