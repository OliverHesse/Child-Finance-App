import os
import csv
import operator
class BinaryTree:
  def add_node(data1,data2):
    pass
class Database:
  
  def __init__(self, db_folder):
    #read in the table names and create a new table object for each
    self.db_folder = os.getcwd() + "/" + db_folder
    self.tables = {}
    self.tableFileType = ".csv"
    for filename in os.listdir(path=self.db_folder):
      if filename.endswith(self.tableFileType):
        self.tables[filename.replace(".csv", "")] = Table(
            f"{self.db_folder}/{filename}", filename.strip(".csv"))
    
    

  def MAX(self,table,columns,where = None):
    if table in self.tables and len(columns) > 0:
      return self.tables[table].MAX(columns,where)
    raise Exception("error parsing input")

  def MIN(self,table,columns,where = None):
    if table in self.tables and len(columns) > 0:
      return self.tables[table].MIN(columns,where)
    raise Exception("error parsing input")

  def TOTAL(self,table,columns,where = None):
    if table in self.tables and len(columns) > 0:
      return self.tables[table].TOTAL(columns,where)
    raise Exception("error parsing input")

  def setup_from_csv(self, file_path):
    #use schema file to construct tables
    file = open(file_path + ".csv", "r")
    reader = csv.reader(file)

    for row in reader:
      #split into table name and columns
      table_name = ""
      columnCount = 0
      columns = []
      for column in row:
        if columnCount == 0:
          table_name = column

        else:
          columns.append(column.split(":"))
        columnCount += 1
      #create new table with data
      if table_name not in self.tables:
        self.create(table_name, columns)
    file.close()

  def create(self, table_name, columns):
    #columns should be in format [[c1 , type],[c2,type]]
    file = open(self.db_folder + "/" + table_name + ".csv", "w")
    row_text = []
    for column in columns:
      if len(column) != 2:
        raise Exception("Error: column not recognised")
      #makes sure the column is a valid data type
      match column[1]:
        case "int": 
          pass
        case "str":
          pass
        case "float":
          pass
        case "bool":
          pass
        case _:
          raise Exception("Error: Invalid Data Type")
      row_text.append(str(column[0]) + ":" + str(column[1]))
    writer = csv.writer(file)
    writer.writerow(row_text)
    self.tables[table_name] = Table(self.db_folder + "/" + table_name + ".csv",table_name)
    file.close()

  def select(self,Table,columns,where = None):
    #check if table exists
    if Table in self.tables:
      #table exists
      return self.tables[Table].select(columns,where)
    raise Exception("Error: Table does not exist")

  def update(self,Table,columns,data,where = None):
    if Table in self.tables and len(columns) == len(data):
      #table exists and columns and data are of the same length
      return self.tables[Table].update(columns,data,where)
    raise Exception("Error when parsing command")

  def insert(self,Table,data):
    #check if table exists
    if Table in self.tables:
      return self.tables[Table].insert(data)
    raise Exception("Table does not exist")

  def delete(self,Table,where = None):
    #check if table exists
    if Table in self.tables:
      return self.tables[Table].delete(where)
    raise Exception("Error: Table not found")

  def commit(self,Tables=None):
    #commit all Tables
    if Tables is None:
      for table in self.tables:
        self.tables[table].commit()
    else:
      #for each table call their commit function
      for table in Tables:
        if table in self.tables:
          self.tables[table].commit()
        else:
          raise Exception(f"Error Unkown table {table}")
class Table:
  #construct the in memory table and meta data
  def __init__(self, filePath, name):
    self.tableName = name

    self.tableFilePath = filePath
    table_file = open(filePath, "r")
    csv_reader = csv.reader(table_file, delimiter=',')
    count = 0
    self.ColumnMetaData = {}

    self.table = []
    tempMap = {}
    #create a mapping of column id -> name,type
    for row in csv_reader:
      if count == 0:
        for header_i in range(0, len(row)):
          column_meta = row[header_i].split(":")
          if len(column_meta) != 2:
            raise Exception(
              "cannot parse: column header must include Name:Type")
          tempMap[header_i] = {
            "columnName": column_meta[0],
            "columnType": column_meta[1]
          }
          self.ColumnMetaData[column_meta[0]] = {
            "column_id": header_i,
            "type": column_meta[1],
            "searchTree": BinaryTree()
          }

      else:
        self.table.append([])
        for header_i in range(0, len(row)):
          #check if it is corect data type and insert into table

          try:
            value = None
            if tempMap[header_i]["columnType"] == "int":
              self.table[count - 1].append(int(row[header_i]))
              value = int(row[header_i])
            if tempMap[header_i]["columnType"] == "str":
              self.table[count - 1].append(str(row[header_i]))
              value = str(row[header_i])
            if tempMap[header_i]["columnType"] == "float":
              self.table[count - 1].append(float(row[header_i]))
              value = float(row[header_i])
            if tempMap[header_i]["columnType"] == "bool":
              self.table[count - 1].append(bool("True" == row[header_i]))
              value = bool("True" == row[header_i])
            #update meta data
            self.ColumnMetaData[tempMap[header_i]["columnName"]]["searchTree"].add_node(
                                  [value, count - 1])
          except:
            raise Exception(
              "cannot read table: field type does not match column type")
      count += 1
    self.tempMap = tempMap
    

  def where(self,statements):
    
    #for this prototype only
    num_of_statements = len(statements)
    #there will always be an odd numeber of statements
    if num_of_statements%2 == 0:
      raise Exception("no enough WHERE conditions satisfied")

    #how many statements have i performed.
    #once it is 2 i will perform the AND/OR operation on the results
    operations_performed = 0
    current_operation = ""
    #i will use a set
    last_result = set()
    
    for statement in statements:
      
      if statement != "OR" and statement != "AND":
        #normal statement begin proccesing
        if len(statement) != 3:
          raise Exception(f"Error: statement expects 3 items you provided{len(statement)}")

        #check if column exists

        if statement[0] not in self.ColumnMetaData:
          raise Exception(f"Error: column {statement[0]} does not exist")
        current_column = statement[0]
        #check if the data they provided is the right type
        value = None
        try:
          print(self.ColumnMetaData[current_column]["column_id"])
          print( self.ColumnMetaData[current_column]["type"])
          if self.ColumnMetaData[current_column]["type"] == "int":
            value = int(statement[2])

          if self.ColumnMetaData[current_column]["type"] == "str":
            value=str(statement[2]).strip()
          if self.ColumnMetaData[current_column]["type"] == "float":
            value = float(statement[2])

          if self.ColumnMetaData[current_column]["type"] == "bool":
            if statement[2].strip() == "True":
              value = True
            elif statement[2].strip() == "False":
              value =False
        except TypeError:
          raise Exception("Error: invalid datatype")

        #check the operator they provided
        operand = statement[1]
        results = set()
        ops = {
          "==":operator.eq,
          ">":operator.gt,
          "<":operator.lt,
          ">=":operator.ge,
          "<=":operator.le,
          "!=":operator.ne}
        if operand not in ops:
          raise Exception(f"invalid operand {operand}")
        #perform opeartion using operation map
        for index in range(0,len(self.table)):

          if ops[operand](self.table[index][self.ColumnMetaData[current_column]["column_id"]],value):

            results.add(index)

        operations_performed += 1
        if operations_performed == 2:
          #combine results using sets 
          
          if current_operation != "OR" and current_operation != "AND":
            raise  Exception("Invalid operation")
          elif current_operation == "AND":

            last_result.intersection_update(results)
          elif current_operation == "OR":
            last_result.update(results)

          current_operation = ""
          operations_performed=1
        else:
          last_result = results

      else:
        #its and AND/OR Statement

        if current_operation != "":
          #they put 2 AND/OR in a row
          raise Exception(f"invalid operation at {statement}")
        current_operation = statement

    return last_result

  def select(self,columns,where = None):
    rows = self.where(where) if where is not None else "*"

    if columns == []:
      #Select All
      if rows != "*":
        data = []
        for index in rows:
          data.append(self.table[index][:])
        return data[:]
      else:
        #return all rows
        #currently only a shallow copy so be very carefull
        return self.table[:]
    elif len(columns) > 0:
      #return only specified columns
      column_indexes = []
      for column in columns:
        if column in self.ColumnMetaData:
          column_indexes.append(self.ColumnMetaData[column]["column_id"])
        else:
          raise Exception(f"Error: Column {column} does not exist")
      data = []
      #specific columns
      if rows != "*":

        for index in rows:
          new_row = []
          for c_index in column_indexes:
            new_row.append(self.table[index][c_index])
          data.append(new_row)

      else:
        #return all rows 
        for row in self.table:
          new_row = []
          for c_index in column_indexes:
            new_row.append(row[c_index])
          data.append(new_row)
      return data
    else:
      raise Exception("Invalid columns")

  def update(self,columns,data,where=None):
    #first validate data (check data type)
    column_indexes = []
    for i in range(0,len(columns)):
      #make sure it is a valud data type
      try:

        if self.ColumnMetaData[columns[i]]["type"] == "int":
          int(data[i])

        elif self.ColumnMetaData[columns[i]]["type"] == "str":
          str(data[i]).strip()
        elif self.ColumnMetaData[columns[i]]["type"] == "float":
          float(data[i])

        elif self.ColumnMetaData[columns[i]]["type"] == "bool" and  (data[i].strip() != "True" and data[i].strip() != "False"):
          raise Exception("Error: not a bool")

      except KeyError:
        raise Exception("cannot read table: invalid column")
      except TypeError:
        raise Exception("cannor read table: invalud data type")
      column_indexes.append(self.ColumnMetaData[columns[i]]["column_id"])
    #update rows that satisfy the where condtion
    rows = self.where(where) if where is not None else "*"
    if rows != "*":
      for row_i in rows:
        for i in range(0,len(columns)):
          column_index = self.ColumnMetaData[columns[i]]["column_id"]
          self.table[row_i][column_index] = data[i]
    else:
      #no where condtion update them all
      for i in range(0,len(self.table)):
        for x in range(0,len(columns)):
          column_index = self.ColumnMetaData[columns[x]]["column_id"]
          self.table[i][column_index] = data[x]

  def insert(self,data):

    #first validate all the data
    for i in range(0,len(self.tempMap)):
      try:
        #validate data type
        if self.tempMap[i]["columnType"] == "int":
          int(data[i])

        if self.tempMap[i]["columnType"] == "str":
          str(data[i]).strip()
        if self.tempMap[i]["columnType"] == "float":
          float(data[i])
        condition = data[i] != True and data[i] != False
        if self.tempMap[i]["columnType"] == "bool" and condition:
          raise Exception("Error: not a bool")

      except KeyError:
        raise Exception("cannot read table: invalid column")
      except TypeError:
        raise Exception("cannor read table: invalud data type")
    #insert into table
    self.table.append(data)
    
  def delete(self,where = None):
    if where is None:
      self.table = []
    else:
      rows = self.where(where)
      #remove rows that satisfy where condition
      for row in sorted(rows, reverse=True):
        self.table.pop(row)

  def commit(self):
    #open the file
    with open(self.tableFilePath, mode='w') as table_file:
      #create a csv writer to write to the table
      table_writer = csv.writer(table_file, delimiter=',')
      tableMetaData = []
      #turn metadata into a string
      for i in range(0,len(self.ColumnMetaData)):
        columnName = self.tempMap[i]["columnName"]
        columnType = self.tempMap[i]["columnType"]
        tableMetaData.append(f"{columnName}:{columnType}")
      #write metadata to first line
      table_writer.writerow(tableMetaData)

      #write rows into table
      for row in self.table:
        table_writer.writerow(row)
  def MAX(self,columns,where = None):
    running_maxes = []
    #validate columns
    for column in columns:
      if column not in self.ColumnMetaData:
        raise Exception(f"Error: Invalid Column:{column}")
      running_maxes.append(0)
    rows = []
    if where is not None:
      #only checks rows that satisfy where condition
      rows = self.where(where)
      for row_i in rows:
        for i in range(0,len(columns)):
          if self.table[row_i][self.ColumnMetaData[columns[i]]["column_id"]] > running_maxes[i]:
            running_maxes[i] = self.table[row_i][self.ColumnMetaData[columns[i]]["column_id"]]
      return running_maxes
    for row in self.table:
      #standard running maximum 
      for i in range(0,len(columns)):
        if row[self.ColumnMetaData[columns[i]]["column_id"]] > running_maxes[i]:
          running_maxes[i] = row[self.ColumnMetaData[columns[i]]["column_id"]]
    return running_maxes

  def MIN(self,columns,where = None):
    running_mins = []
    #validate columns
    for column in columns:
      if column not in self.ColumnMetaData:
        raise Exception(f"Error: Invalid Column:{column}")
      running_mins.append(0)
    rows = []
    if where is not None:
      #only checks ones that satisfy where condition
      rows = self.where(where)
      for row_i in rows:
        for i in range(0,len(columns)):
          if self.table[row_i][self.ColumnMetaData[columns[i]]["column_id"]] < running_mins[i]:
            running_mins[i] = self.table[row_i][self.ColumnMetaData[columns[i]]["column_id"]]
      return running_mins
    for row in self.table:
      #standard running min
      for i in range(0,len(columns)):
        if row[self.ColumnMetaData[columns[i]]["column_id"]] < running_mins[i]:
          running_mins[i] = row[self.ColumnMetaData[columns[i]]["column_id"]]
    return running_mins
  def TOTAL(self,columns,where = None):
    running_totals = []
    #validate columns
    for column in columns:
      if column not in self.ColumnMetaData:
        raise Exception(f"Error: Invalid Column:{column}")
      running_totals.append(0)
    rows = []
    if where is not None:
      #only accepts rows that satisfy where condition
      rows = self.where(where)
      for row_i in rows:
        for i in range(0,len(columns)):
          running_totals[i] += self.table[row_i][self.ColumnMetaData[columns[i]]["column_id"]]
      return running_totals
    for row in self.table:
      #standard running total
      for i in range(0,len(columns)):
        running_totals[i] += row[self.ColumnMetaData[columns[i]]["column_id"]]
    return running_totals
