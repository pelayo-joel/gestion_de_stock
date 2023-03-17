import mysql.connector

SHOP = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "sqlroot",
    database = "boutique",
    autocommit = True
)

DB_CURSOR = SHOP.cursor(buffered=True)


class CRUD:
    def __init__(self, cursor, tableName:str):
        self.__cursor = cursor

        if '"' not in tableName:
            self.__currentTable = tableName

        self.__tableColumns = self.__GetColumns()




    '''Public methods'''

    #To me, there isn't any C operations to do on a table
    '''def C_Operations(self, op:str):
        return None'''
    


    def R_Operations(self, columnToRead:str="*", columnCondition:str=None, valueCondition=None):
        try:
            if (columnToRead == "*" or columnToRead.lower() in self.__tableColumns or columnToRead.lower() == "id") and not self.__FragSqlInjection(columnToRead):
                columnUpdate = columnToRead.lower()

        except Exception as e:
            exit(f"Specified column name or index are not in this table\n {e}")


        if columnCondition != None and (not self.__FragSqlInjection(columnCondition) and not self.__FragSqlInjection(valueCondition)):
            if isinstance(valueCondition, str):
                valueCondition = "'" + valueCondition + "'"

            self.__cursor.execute(f"SELECT {columnUpdate} FROM {self.__currentTable} WHERE {columnCondition} = {valueCondition};")
        
        else:
            self.__cursor.execute(f"SELECT {columnUpdate} FROM {self.__currentTable}")

        '''for data in self.__cursor:
            print(data)'''
    


    def U_Operations(self, op:str, valueUpdate, columnToUpdate, columnComparison=None, columnCompValue=None, allowDupe:bool=False):
        if isinstance(columnToUpdate, str) and columnToUpdate.lower() in self.__tableColumns and not self.__FragSqlInjection(columnToUpdate):
            columnUpdate = "(" + columnToUpdate.lower() + ")"

        elif isinstance(columnToUpdate, tuple):
            print(columnToUpdate)
            columnUpdate = self.__ColumnTuple(columnToUpdate)

        else:
            exit('Specified column name or index are not in this table, or " char was used')


        if op == "INSERT":
            nValues = self.__nValuesToUpdate(valueUpdate)

            if allowDupe:
                query = f"""INSERT INTO {self.__currentTable} {columnUpdate}
                                 VALUES {nValues}"""
            elif not allowDupe:
                self.__Dupe(valueUpdate)
                query = f"""INSERT INTO {self.__currentTable} {columnUpdate}
                                 VALUES {nValues}"""
        
            self.__cursor.execute(query, valueUpdate)
            

        elif op == "UPDATE":
            if isinstance(columnComparison, str) and (columnComparison.lower() in self.__tableColumns or columnComparison.lower() == "id") and not self.__FragSqlInjection(columnComparison):
                columnComp = columnComparison.lower()
            elif isinstance(columnComparison, int) and 0 <= columnComparison <= len(self.__tableColumns) and not self.__FragSqlInjection(columnComparison):
                columnComp = self.__tableColumns[columnComparison]
            else:
                exit('Column to compare has not been given or is not in this table, or " char was used')

            if isinstance(valueUpdate, str):
                valueUpdate = "'" + valueUpdate + "'"


            self.__cursor.execute(f"UPDATE {self.__currentTable}\
                                       SET {columnToUpdate} = {valueUpdate}\
                                     WHERE {columnComp} = {columnCompValue}")



    def D_Operations(self, op:str, columnName:str, dataToDELETE:str):
        print(columnName, dataToDELETE)
        try:
            if isinstance(columnName, str) and columnName.lower() in self.__tableColumns and not self.__FragSqlInjection(columnName):
                self.__cursor.execute(f"DELETE FROM {self.__currentTable}\
                                              WHERE {columnName.lower()} = '{dataToDELETE}';")

        except Exception as e:
            exit(f'Specified column name or index are not in this table, or " char was used\n {e}')
    

    #Getters/Setters

    def GetCurrentCursor(self):
        return self.__cursor

    def GetTable(self):
        return self.__currentTable
    
    def GetTableColumns(self):
        return self.__tableColumns
    


    
    """Private methods"""


    def __GetColumns(self):
        columnList = []
        self.__cursor.execute(f"SHOW COLUMNS FROM {self.__currentTable};")
        self.__columnData = self.__cursor.fetchall()

        for column in self.__columnData:
            if column[0] != "id":
                columnList.append(column[0])

        return tuple(columnList)
    


    def __FragSqlInjection(self, queryValue:str):
        if isinstance(queryValue, str) and '"' in queryValue:
            exit(f"Prevented Fragmented SQL Injection: {queryValue}")

        return False
    


    def __Dupe(self, valueToCheck):
        self.__cursor.execute(f"SELECT * FROM {self.__currentTable}")

        for data in self.__cursor:
            if valueToCheck in data:
                exit("Specified value is a dupe, query aborted")



    def __nValuesToUpdate(self, valueTuple:tuple):
        values = "("

        for value in valueTuple:
            if not self.__FragSqlInjection(value):
                values += f"%s, "

        return values[:-2] + f")"
    


    def __ColumnTuple(self, strColumnTuple:tuple):
        tupleToStr = "("
        for column in strColumnTuple:
            tupleToStr += column + ", " 

        return tupleToStr[:-2] + ")"
