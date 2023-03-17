from Shop import *
from tkinter import *
from tkinter import messagebox
import tkinter.ttk as ttk
import pathlib
import csv





class App(Tk):
    def __init__(self):
        super().__init__()

        """---------------SQL APP GLOBALS---------------"""

        self.__cursor = DB_CURSOR

        self.__productsOP = CRUD(self.__cursor, "produit")
        self.__sectionsOP = CRUD(self.__cursor, "categorie")

        self.__productColumns = self.__productsOP.GetTableColumns()
        #self.__sectionColumns = self.__sectionsOP.GetTableColumns()


        """---------------TKINTER APP GLOBALS---------------"""

        #----------Setup tkinter's main window----------#
        self.geometry("750x600")
        self.title("Shop Manager")
        self.resizable(height=False, width=False)
        
        self.__icon = PhotoImage(file="images-src/stock-icon.png")
        self.iconphoto(False, self.__icon)

        """-----MainFrame and elements on it-----"""
        #----------Setup a Frame on the window----------#
        self.__mainFrame = Frame(self)
        self.__mainFrame.pack(expand=True, fill="both")

        #----------Frame for tabs----------#
        self.__tabsFrame = ttk.Notebook(self.__mainFrame, height=400)
        self.__tabsFrame.pack(fill="x")

        #----------Tabs Frame----------#
        self.__InitTabs()

        #-----Product list by category-----#
        self.__InitCategoriesTreeview()

        #----------Buttons----------#
        self.__InitButtons()
    



    """Private methods"""
    
    #Initial data from database in each category
    def __TreesData(self, section:str):
        self.__sectionsOP.R_Operations()
        for data in self.__productsOP.GetCurrentCursor():
            if data[1] == section:
                sectionID = data[0]

        self.__productsOP.R_Operations(columnCondition="id_categorie", valueCondition=sectionID)


        for data in self.__productsOP.GetCurrentCursor():
            self.__tabs[section]["Product List"].insert('', END, values=(f"{data[1]}", f"{data[2]}", f"{data[3]}", f"{data[4]}", f"{data[5]}"))
    


    """Button Commands"""

    def __AddWindow(self, section:str):
        def Add(name:str, desc:str, price:int, quantity:int, id:int):
            try:
                self.__productsOP.U_Operations("INSERT", (name, desc, price, quantity, id), ("nom", "description", "prix", "quantite", "id_categorie"))
                self.__tabs[section]["Product List"].insert('', END, values=(f"{name}", f"{desc}", f"{price}", f"{quantity}"))
                addBox.destroy()

            except Exception as e:
                messagebox.showerror("Error", f"Values are invalid\n {e}")


        self.__sectionsOP.R_Operations()
        for data in self.__sectionsOP.GetCurrentCursor():
            if data[1] == section:
                sectionID = data[0]


        addBox = Toplevel()
        addBox.geometry("550x60")
        addBox.title(f"New product in category {section}")
        addBox.iconphoto(False, self.__icon)

        entriesFrame = Frame(addBox)
        entriesFrame.pack(fill="x")
        entries = []

        for i in range(len(self.__productColumns)):
            if self.__productColumns[i] != "id_categorie":
                if self.__productColumns[i] == "description":
                    columnLab = Label(entriesFrame, text=self.__productColumns[i][0].upper() + self.__productColumns[i][1:])
                    columnLab.grid(row=0, column=i, sticky='W')
                    entry = Entry(entriesFrame, width=45)
                    entry.grid(row=1, column=i, sticky='W')
                    entries.append(entry)

                else:
                    columnLab = Label(entriesFrame, text=self.__productColumns[i][0].upper() + self.__productColumns[i][1:])
                    columnLab.grid(row=0, column=i, sticky='W')
                    entry = Entry(entriesFrame, width=15)
                    entry.grid(row=1, column=i, sticky='W')
                    entries.append(entry)


        addButton = Button(addBox, text="Add", command=lambda:Add(entries[0].get(), entries[1].get(), entries[2].get(), entries[3].get(), sectionID))
        addButton.pack(side=BOTTOM)
    


    def __Delete(self, section:str):
        selectedProduct = self.__tabs[section]["Product List"].item(self.__tabs[section]["Product List"].focus())

        if self.__tabs[section]["Product List"].focus() != "":
            self.__productsOP.D_Operations("DELETE", "nom", selectedProduct['values'][0])
            self.__tabs[section]["Product List"].delete(self.__tabs[section]["Product List"].focus())

        else:
            messagebox.showerror("Error", "No product has been selected to be deleted")
    


    def __UpdateWindow(self, section:str):
        def Update(name:str, desc:str, price:int, quantity:int):
            try:
                newValues = [name, desc, int(price), int(quantity)]
                valueChanged = False

                for i in range(len(self.__productColumns) - 1):
                    if selectedProduct['values'][i] != newValues[i]:
                        self.__productsOP.U_Operations("UPDATE", (newValues[i]), self.__productColumns[i], columnComparison="id", columnCompValue=productID)
                        valueChanged = True

                if valueChanged:
                    self.__tabs[section]["Product List"].insert('', END, values=(f"{name}", f"{desc}", f"{price}", f"{quantity}"))
                    self.__tabs[section]["Product List"].delete(selectedProduct)
                    updateBox.destroy()


            except Exception as e:
                messagebox.showerror("Error", f"Values are invalid\n {e}")


        try:
            selectedProduct = self.__tabs[section]["Product List"].item(self.__tabs[section]["Product List"].focus())
            self.__productsOP.R_Operations(columnToRead="id", columnCondition="nom", valueCondition=selectedProduct['values'][0])
            
            for data in self.__productsOP.GetCurrentCursor():
                productID = data[0]


            if self.__tabs[section]["Product List"].focus() != "":
                updateBox = Toplevel()
                updateBox.geometry("550x60")
                updateBox.title(f"Updating {selectedProduct['values'][0]}")
                updateBox.iconphoto(False, self.__icon)
                
                updateFrame = Frame(updateBox)
                updateFrame.pack(fill="x")
                entries = []

                for i in range(len(self.__productColumns)):
                    if self.__productColumns[i] != "id_categorie":
                        if self.__productColumns[i] == "description":
                            columnLab = Label(updateFrame, text=self.__productColumns[i][0].upper() + self.__productColumns[i][1:])
                            columnLab.grid(row=0, column=i, sticky='W')
                            entry = Entry(updateFrame, width=45)
                            entry.grid(row=1, column=i, sticky='W')
                            entry.insert(0, selectedProduct['values'][i])
                            entries.append(entry)

                        else:
                            columnLab = Label(updateFrame, text=self.__productColumns[i][0].upper() + self.__productColumns[i][1:])
                            columnLab.grid(row=0, column=i, sticky='W')
                            entry = Entry(updateFrame, width=15)
                            entry.grid(row=1, column=i, sticky='W')
                            entry.insert(0, selectedProduct['values'][i])
                            entries.append(entry)

                
                updateButton = Button(updateBox, text="Update", command=lambda:Update(entries[0].get(), entries[1].get(), entries[2].get(), entries[3].get()))
                updateButton.pack(side=BOTTOM)
            
        except:
            messagebox.showerror("Error", "No product has been selected to be modified")



    def __ExportToCSV(self, section:str):
        self.__sectionsOP.R_Operations()
        for data in self.__productsOP.GetCurrentCursor():
            if data[1] == section:
                sectionID = data[0]

        self.__productsOP.R_Operations(columnCondition="id_categorie", valueCondition=sectionID)


        if pathlib.Path(f"./ShopCSVs/{section}.csv"):
            with open(f"ShopCSVs/{section}.csv", "w") as sectionCSV:
                csvWriter = csv.writer(sectionCSV, delimiter=",")
                columnHeader = ("id","nom","description","prix","quantite","id_categorie")

                csvWriter.writerow(columnHeader)
                for row in self.__productsOP.GetCurrentCursor():
                    csvWriter.writerow(row)

        else:
            with open(f"ShopCSVs/{section}.csv", "w") as sectionCSV:
                csvWriter = csv.writer(sectionCSV, delimiter=",")
                
                for row in self.__productsOP.GetCurrentCursor():
                    csvWriter.writerow(row)
    


    """Utility when initializing the app"""

    def __InitTabs(self):
        self.__tabs = {}
        self.__sectionsOP.R_Operations("nom")

        for section in self.__sectionsOP.GetCurrentCursor():
            sectionName = str(section)
            tabFrame = Frame(self.__tabsFrame)
            tabFrame.pack(expand=True, fill="both")
            self.__tabsFrame.add(tabFrame, text=sectionName[2:-3])
            self.__tabs.update({sectionName[2:-3]:{"Frame":tabFrame}})



    def __InitCategoriesTreeview(self):
        for tab in self.__tabs:
            productTree = ttk.Treeview(self.__tabs[tab]["Frame"], columns=self.__productColumns, show='headings')
            for column in self.__productColumns:
                productTree.heading(column, text=column[0].upper() + column[1:])
                productTree.column(column, width=175, stretch=NO, anchor=CENTER)
                
                if column == "id_categorie":
                    continue
                elif column == "description":
                    productTree.column(column, minwidth=250, width=425, stretch=NO)
                elif column == "prix":
                    productTree.column(column, minwidth=35, width=70, stretch=NO)
                elif column == "quantite":
                    productTree.column(column, minwidth=40, width=80, stretch=NO)
            
            productTree.pack(expand=True, fill="both")

            self.__tabs[tab]["Product List"] = productTree
            self.__TreesData(tab)



    def __InitButtons(self):
        self.__addButton = Button(self.__mainFrame, text="Add product", command=lambda:self.__AddWindow(self.__tabsFrame.tab(self.__tabsFrame.select(), "text")))
        self.__addButton.pack(side=LEFT, padx=10)
        self.__delButton = Button(self.__mainFrame, text="Delete product", command=lambda:self.__Delete(self.__tabsFrame.tab(self.__tabsFrame.select(), "text")))
        self.__delButton.pack(side=LEFT, padx=10)
        self.__updateButton = Button(self.__mainFrame, text="Modify product", command=lambda:self.__UpdateWindow(self.__tabsFrame.tab(self.__tabsFrame.select(), "text")))
        self.__updateButton.pack(side=LEFT, padx=10)
        self.__exportToCSVButton = Button(self.__mainFrame, text="Export to CSV", command=lambda:self.__ExportToCSV(self.__tabsFrame.tab(self.__tabsFrame.select(), "text")))
        self.__exportToCSVButton.pack(side=LEFT, padx=10)









if __name__ == "__main__":
    program = App()
    program.mainloop()