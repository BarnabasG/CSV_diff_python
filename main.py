from PyQt5 import QtCore, QtWidgets
import sys
import os
from glob import glob

import pandas as pd
from collections import Counter
from datetime import datetime
import copy

import time

class Ui_Dialog(object):

    pre_name, post_name = None, None
    before_data, after_data = None, None
    changes = {}
    conditions = []
    
    def auto_complete_files(self):

        files = sorted(glob("*.xlsx")+glob("*.csv")+glob("*.xls"))
        completer1 = QtWidgets.QCompleter(files)
        self.file1.setCompleter(completer1)
        self.file2.setCompleter(completer1)

    def load_names(self):

        # Set the 2 csv files to compare
        """
        pre_name="MOCK_DATA.csv"
        post_name = "MOCK_DATA_2.xlsx"
        """
        
        pre_name = self.file1.text()
        post_name = self.file2.text()
        missing = []
        if not os.path.isfile(pre_name):
            if pre_name.strip() == "":
                missing.append("File1")
            else:
                missing.append(pre_name)
        if not os.path.isfile(post_name):
            if post_name.strip() == "":
                missing.append("File2")
            else:
                missing.append(post_name)
        if missing:
            QtWidgets.QMessageBox.question(self, 'Error', "Cannot find "+",".join(missing), QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
            return   
        
        start_time = time.time()
        try:
            try:
                before_data = pd.read_csv(pre_name)
            except:
                before_data = pd.read_excel(pre_name)
            try:
                after_data = pd.read_csv(post_name)
            except:
                after_data = pd.read_excel(post_name)
        
        except:
            QtWidgets.QMessageBox.question(self, 'Error', "Failed to load data", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
            return
              
        end_time = time.time()
        print(end_time - start_time)

        print()
        print(after_data.dtypes)

        try:
            self.populate_fields(before_data.columns, after_data.columns)
        except:
            return

        self.pre_name = pre_name
        self.post_name = post_name
        self.before_data = before_data
        self.after_data = after_data
        return
    
    def populate_fields(self, pre_cols, post_cols):

        self.primaryFields.clear()
        self.ignoredFields.clear()
        self.fieldBox.clear()
        self.conditions.clear()
        self.populate_operations()

        shared_cols = sorted(set(pre_cols) & set(post_cols), key=list(pre_cols).index)
        for column in shared_cols:
            items = []
            for _ in range(2):
                items.append(QtWidgets.QListWidgetItem())
                items[-1].setText(str(column))
                items[-1].setFlags(items[-1].flags() | QtCore.Qt.ItemIsUserCheckable)
                items[-1].setCheckState(QtCore.Qt.Unchecked)
            self.primaryFields.addItem(items[0])
            self.ignoredFields.addItem(items[1])
        
        self.fieldBox.addItems(shared_cols)
        
        self.show_fields()
    
    def populate_operations(self):

        self.operatorBox.clear()
        operations = ["==","!=","<","<=",">",">=","CONTAINS"]
        self.operatorBox.addItems(operations)

    def populate_tables(self):

        print(self.pre_name, self.post_name)
        self.prePostBox.clear()
        tables = ["All tables",self.pre_name,self.post_name]
        self.prePostBox.addItems(tables)
    
    def show_fields(self):

        self.primaryLbl.show()
        self.ignoreLbl.show()
        self.ignoredFields.show()
        self.primaryFields.show()
        self.fileWriteBox.show()
        self.fileWriteLbl.show()
        self.compareBtn.show()

        self.andBtn.hide()
        self.orBtn.hide()
    
    def compare(self):

        primary_fields, ignored_fields = self.check_fields()
        if not primary_fields:
            return
        if (set(primary_fields).intersection(set(ignored_fields))):
            return

        if self.before_data is None or self.after_data is None:
            return
        
        self.populate_tables()
        self.show_tabs()

        self.run(self.pre_name, self.post_name, self.before_data, self.after_data, primary_fields, ignored_fields)
    
    def check_fields(self):

        primary_fields, ignored_fields = [], []
        primary_items, ignored_items = [], []
        for index in range(self.primaryFields.count()):
            primary_items.append(self.primaryFields.item(index))
        for index in range(self.ignoredFields.count()):
            ignored_items.append(self.ignoredFields.item(index))
        for i in primary_items:
            if int(i.checkState()) == 2:
                primary_fields.append(i.text())
        for i in ignored_items:
            if int(i.checkState()) == 2:
                ignored_fields.append(i.text())
        return primary_fields, ignored_fields

    def add_condition(self):
        
        field = str(self.fieldBox.currentText())
        operation = str(self.operatorBox.currentText())
        value = str(self.value.text())
        print(field, operation, value)
        if [field,operation,value] not in self.conditions:
            self.conditions.append({"field":field,"operation":operation,"value":value,"connective":''})
            self.queryList.append("{} {} {}".format(field,operation,value))
        
        self.show_conditions()
    
    def add_operation(self, connective, op_string):

        self.conditions[-1]["connective"] = connective
        self.queryList.append(op_string)

        self.hide_conditions()
    
    def show_conditions(self):

        self.fieldBox.hide()
        self.operatorBox.hide()
        self.value.hide()
        self.addConditionBtn.hide()

        self.andBtn.show()
        self.orBtn.show()

    def hide_conditions(self):

        self.fieldBox.show()
        self.operatorBox.show()
        self.value.show()
        self.addConditionBtn.show()

        self.andBtn.hide()
        self.orBtn.hide()

    def run_query(self):

        table = str(self.prePostBox.currentText())

        if table == self.pre_name:
            self.query(self.before_data, "pre")      
        elif table == self.post_name:
            self.query(self.after_data, "post")
        else:
            self.query(self.before_data, "pre")
            self.query(self.after_data, "post")
    
    def query(self, dataframe, table):

        cons = copy.deepcopy(self.conditions)
        if not self.conditions:
            model = PandasModel(dataframe.head(50))
        else:
            cons[-1]["connective"] = ""
            query = ' '.join([self.generate_query_string(x) for x in cons])

            print("query:", query)
            if query:
                if "CONTAINS" in [x.get('operation') for x in cons]:
                    dataframe = dataframe.query(query, engine='python')
                else:
                    dataframe = dataframe.query(query)
            if dataframe.empty:
                model = None
            else:
                model = PandasModel(dataframe)
        try:
            if table == "pre":
                self.queryOutputPre.setModel(model)
            elif table == "post":
                self.queryOutputPost.setModel(model)
        except:
            return

    def generate_query_string(self, x):

        if x["value"].isnumeric():
            q_string = '{} {} {} {}'.format(x["field"], x["operation"], x["value"], x["connective"])
        else:
            if x["operation"] == "CONTAINS":
                q_string = '{}.str.contains("{}") {}'.format(x["field"], x["value"], x["connective"])
            else:
                q_string = '{} {} "{}" {}'.format(x["field"], x["operation"], x["value"], x["connective"])
        return q_string


    def show_tabs(self):

        self.tabWidget.show()
        self.clearBtn.show()

    def run(self, pre_name, post_name, before_data, after_data, primary_fields, ignored_fields):
        
        # All other columns set for comparisson
        other_fields = [x for x in list(set(before_data.columns).intersection(set(after_data.columns))) if x not in primary_fields+ignored_fields]

        before_lists = [list(before_data[pf].astype(str)) for pf in primary_fields]
        after_lists = [list(after_data[pf].astype (str)) for pf in primary_fields]
        pk_before = list(zip(*before_lists))
        pk_after = list(zip(*after_lists))

        #Get duplicate keys this should return 0
        duplicate_keys_before = sorted([(k, v) for (k,v) in Counter (pk_before).items() if v > 1])
        duplicate_keys_after = sorted ([(k, v) for (k,v) in Counter (pk_after).items() if v > 1])

        count_b, count_a = len(pk_before), len(pk_after)

        other_fields_before, other_fields_after = [], []

        for field in other_fields:
            other_fields_before.append(before_data[field].astype(str))
            other_fields_after.append(after_data[field].astype(str))

        dict_before, dict_after = {},{}

        for i, exc in enumerate (pk_before):
            dict_before[exc] = [x[i] for x in other_fields_before]

        for i, exc in enumerate (pk_after):
            dict_after[exc] = [x[i] for x in other_fields_after]

        # Get newly found and completely lost rows
        new = list(set(pk_after) - set(pk_before))
        new2 = [(x,dict_after[x]) for x in new]
        lost = list(set(pk_before) - set(pk_after))
        lost2 = [(x,dict_before[x]) for x in lost]

        # Get changes
        counts = {}
        self.changes = {}
        for key in dict_after:
            if key in dict_before:
                for i, val in enumerate (dict_after[key]):
                    if val != dict_before [key][i]:
                        changed_field = other_fields[i]
                        change = str(dict_before[key][i])+"  ->  "+val
                        add = (changed_field,change)
                        if key in self.changes:
                            self.changes[key].append(add)
                        else:
                            self.changes[key] = [add]
                        if changed_field in counts:
                            if change in counts[changed_field]:
                                counts[changed_field][change] += 1
                            else:
                                counts[changed_field][change] = 1
                            counts[changed_field]["total"] += 1
                        else:
                            counts[changed_field] = {change: 1}
                            counts[changed_field]["total"] = 1

        totals = sorted(counts.items(), key=lambda x: x[1]["total"], reverse=True)

        self.write_summary(pre_name,post_name,duplicate_keys_before,duplicate_keys_after,new,lost,count_a,count_b,self.changes,totals)
        self.write_duplicates(duplicate_keys_before,duplicate_keys_after)
        self.write_changes(self.changes,totals)
        self.populate_reasons(totals)
        self.write_new_rows(new,new2,count_a)
        self.write_rows_lost(lost,lost2,count_b)

        filewrite = self.fileWriteBox.isChecked()
        if filewrite:
            # Write to output file
            self.write_to_file(pre_name,post_name,duplicate_keys_before,duplicate_keys_after,new,lost,new2,lost2,count_a,count_b,self.changes,totals)
    
    def write_summary(self,pre_name,post_name,duplicate_keys_before,duplicate_keys_after,new,lost,count_a,count_b,changes,totals):
        self.summary.append("+++ SUMMARY +++")
        self.summary.append(str(datetime.now()))
        self.summary.append("\n{} -> {}".format(pre_name,post_name))
        self.summary.append("===Duplicate keys before | after : {} | {}".format(str(len(duplicate_keys_before)),str(len(duplicate_keys_after))))
        self.summary.append(f"===New rows: {str(len(new))} - total rows post: {str(count_a)}===")
        self.summary.append(f"===Rows lost : {str(len(lost))} - total rows pre: {str(count_b)}===")
        self.summary.append(f"===Changes: {str(len(changes))}===")
        self.summary.append("-> Top Changes")
        for field in totals[:min(3, len(totals))]:
            self.summary.append(field[0]+" - "+str(field[1]["total"])+" changes")
            top = sorted([(k, v) for k, v in field[1].items() if k!="total"],key=lambda x: x[1],reverse=True)[:min(3,len(field[1].items())-1)]
            for c in top:
                self.summary.append("   {} - count: {}".format(str(c[0]),str(c[1])))
        self.summary.append("+++++++++++++++\n\n")
    
    def write_duplicates(self,duplicate_keys_before,duplicate_keys_after):
        self.duplicates.append("===Duplicate keys===\n")
        self.duplicates.append("Before Count: "+str(len(duplicate_keys_before)))
        if len(duplicate_keys_before) > 0:
            self.duplicates.append("'"+"','".join([x[0][0] for x in duplicate_keys_before])+"'\n")
        [self.duplicates.append(x[0][0]+" - "+str(x[1])) for x in duplicate_keys_before]
        self.duplicates.append('')
        self.duplicates.append("After Count: "+str(len(duplicate_keys_after)))
        if len(duplicate_keys_after) > 0:
            self.duplicates.append("'"+"','".join([x[0][0] for x in duplicate_keys_after])+"'\n")
        [self.duplicates.append(x[0][0]+" - "+str(x[1])) for x in duplicate_keys_after]
        self.duplicates.append('\n')
    
    def write_changes(self, changes, totals):
        self.changesWindow.append("===Change Summary===")
        for field in totals:
            self.changesWindow.append(field[0]+" - "+str(field[1]["total"])+" changes")
        self.changesWindow.append('')
        self.changesWindow.append("===Changes : "+str(len(changes))+"===")
        self.changesWindow.append("Expand a change reason below")
        #if len(changes) > 0:
        #    self.changesWindow.append("'"+"','".join([x[0] for x in changes.keys()])+"'\n")
        #for key, value in changes.items():
        #    self.changesWindow.append(str(key if len(key)>1 else key[0])+' : '+str([str(v[0])+" : "+str(v[1]) for v in value]))
        self.changesWindow.append('\n')
    
    def write_new_rows(self, new, new2, count_a):
        self.newRows.append("===New rows : "+str(len(new))+" - total rows post: "+str(count_a) +"===")
        if count_a > 0:
            self.newRows.append("'"+"','".join([x[0] for x in new])+"'")
        self.newRows.append('')
        [self.newRows.append(str(x[0] if len(x[0])>1 else x[0][0])+' : '+str(x[1])) for x in new2]
        self.newRows.append('\n')
    
    def write_rows_lost(self, lost, lost2, count_b):
        self.rowsLost.append("===Rows lost : "+str(len(lost))+" total rows pre: "+str(count_b)+"===")
        if count_b > 0:
            self.rowsLost.append("'"+"','".join([x[0] for x in lost])+"'")
        self.rowsLost.append('')
        [self.rowsLost.append(str(x[0] if len(x[0])>1 else x[0][0])+' : '+str(x[1])) for x in lost2]
        self.rowsLost.append('\n')
    
    def clear(self):

        self.summary.clear()
        self.duplicates.clear()
        self.changesWindow.clear()
        self.newRows.clear()
        self.rowsLost.clear()
        self.queryOutputPre.setModel(None)
        self.queryOutputPost.setModel(None)
    
    def clear_query(self):

        self.conditions.clear()
        self.queryList.clear()
        self.hide_conditions()

    def populate_reasons(self, totals):

        self.changeFieldsLst.clear()
        self.changeFieldsLst.addItem("All Changes ({})".format(str(len(self.changes))))
        self.changeFieldsLst.addItems(["{} ({})".format(t[0],str(t[1]["total"])) for t in totals])
    
    def expand_reason(self):

        field = self.changeFieldsLst.currentText().rsplit(' (')[0]

        if field == "All Changes":
            self.changesWindow.append("===All Changes : {}===".format(str(len(self.changes))))
            for key, value in self.changes.items():
                self.changesWindow.append(str(key)+' : '+str(value))
            self.changesWindow.append('\n')
        else:
            relevant_changes = {}
            for key,value in self.changes.items():
                for v in value:
                    if v[0] == field:
                        relevant_changes[key] = v[1]
            self.changesWindow.append("==={} Changes : {}===".format(field,str(len(relevant_changes))))
            for key, value in relevant_changes.items():
                self.changesWindow.append(str(key)+' : '+str(value))
            self.changesWindow.append('\n')
    
    def write_to_file(self,pre_name,post_name,duplicate_keys_before,duplicate_keys_after,new,lost,new2,lost2,count_a,count_b,changes,totals):
        files = "{}-{}".format(pre_name,post_name)
        with open('changes_summary_'+files+'.txt', 'w') as f:
            f.write("+++ SUMMARY +++\n")
            f.write(str(datetime.now()))
            f.write("\n{} -> {}\n".format(pre_name,post_name))
            f.write("===Duplicate keys before | after: {} | {}\n".format(str(len(duplicate_keys_before)),str(len(duplicate_keys_after))))
            f.write("===New rows: "+str(len(new))+" - total rows post: "+str(count_a)+"===\n")
            f.write("===Rows lost: "+str(len(lost))+" total rows pre: "+str(count_b)+"===\n")
            f.write("===Changes: "+str(len(changes))+"===\n")
            f.write("-> Top Changes\n")
            for field in totals[:min(3, len(totals))]:
                f.write(field [0]+" - "+str(field[1]["total"])+" changes\n")
                top = sorted([(k,v) for k,v in field[1].items() if k!="total"],key=lambda x: x[1],reverse=True)[:min(3,len(field[1].items())-1)]
                for c in top:
                    f.write("       {} - count: {}\n".format(str(c[0]),str(c[1])))
            f.write("+++++++++++++++\n\n")
            f.write("===Duplicate keys===\n")
            f.write("Before Count : "+str(len(duplicate_keys_before))+'\n')
            if len(duplicate_keys_before) > 0:
                f.write("'"+"','".join([x[0][0] for x in duplicate_keys_before])+"'\n\n")
            [f.write(x[0][0] +" - "+str(x[1])+'\n') for x in duplicate_keys_before]
            f.write("\n")
            f.write("After Count : "+str(len(duplicate_keys_after))+'\n')
            if len(duplicate_keys_after) > 0:
                f.write("'"+"','".join([x[0][0] for x in duplicate_keys_after])+"'\n\n")
            [f.write(x[0][0]+", "+str(x[1])+'\n') for x in duplicate_keys_after]

            f.write('\n')
            f.write("===Change Summary===\n")
            for field in totals:
                f.write(field[0]+" - "+str(field[1]["total"])+" changes\n")
            f.write('\n')
            f.write("===Changes : "+str(len(changes))+"===\n")
            if len(changes) > 0:
                f.write("'"+"','".join([x[0] for x in changes.keys()])+"'\n\n")
            for key, value in changes.items():
                f.write(str(key if len(key)>1 else key[0])+' : '+str([str(v[0])+" : "+str(v[1]) for v in value])+'\n')
            f.write('\n')
            f.write("===New rows : "+str(len(new))+" - total rows post: "+str(count_a)+"===\n")
            if count_a > 0:
                f.write("'"+"','".join([x[0] for x in new])+"'")
            f.write('\n')
            [f.write(str(x[0] if len(x[0])>1 else x[0][0])+' : '+str(x[1])) for x in new2]
            f.write('\n\n')
            f.write("===Rows Lost : "+str(len(lost))+" - total rows pre: "+str(count_b)+"===\n")
            if count_b > 0:
                f.write("'"+"','".join([x[0] for x in lost])+"'")
            f.write('\n')
            [f.write(str(x[0] if len(x[0])>1 else x[0][0])+' : '+str(x[1])) for x in lost2]
            f.write('\n')
            
            f.close()
    
    #PyQt5 UI design
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(666, 647)
        self.file1 = QtWidgets.QLineEdit(Dialog)
        self.file1.setGeometry(QtCore.QRect(60, 10, 221, 20))
        self.file1.setObjectName("file1")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(9, 9, 25, 16))
        self.label.setObjectName("label")
        self.file2 = QtWidgets.QLineEdit(Dialog)
        self.file2.setGeometry(QtCore.QRect(350, 10, 221, 20))
        self.file2.setObjectName("file2")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(320, 9, 25, 16))
        self.label_2.setObjectName("label_2")
        self.loadBtn = QtWidgets.QPushButton(Dialog)
        self.loadBtn.setGeometry(QtCore.QRect(580, 10, 75, 23))
        self.loadBtn.setObjectName("loadBtn")
        self.tabWidget = QtWidgets.QTabWidget(Dialog)
        self.tabWidget.setGeometry(QtCore.QRect(10, 130, 651, 481))
        self.tabWidget.setObjectName("tabWidget")
        self.summaryTab = QtWidgets.QWidget()
        self.summaryTab.setObjectName("summaryTab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.summaryTab)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.summary = QtWidgets.QTextBrowser(self.summaryTab)
        self.summary.setObjectName("summary")
        self.verticalLayout_2.addWidget(self.summary)
        self.tabWidget.addTab(self.summaryTab, "")
        self.duplicatesTab = QtWidgets.QWidget()
        self.duplicatesTab.setObjectName("duplicatesTab")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.duplicatesTab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.duplicates = QtWidgets.QTextBrowser(self.duplicatesTab)
        self.duplicates.setObjectName("duplicates")
        self.verticalLayout.addWidget(self.duplicates)
        self.tabWidget.addTab(self.duplicatesTab, "")
        self.changesTab = QtWidgets.QWidget()
        self.changesTab.setObjectName("changesTab")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.changesTab)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.changesWindow = QtWidgets.QTextBrowser(self.changesTab)
        self.changesWindow.setObjectName("changesWindow")
        self.verticalLayout_3.addWidget(self.changesWindow)
        self.changeFieldsLst = QtWidgets.QComboBox(self.changesTab)
        self.changeFieldsLst.setObjectName("changeFieldsLst")
        self.verticalLayout_3.addWidget(self.changeFieldsLst)
        self.filterChangesBtn = QtWidgets.QPushButton(self.changesTab)
        self.filterChangesBtn.setObjectName("filterChangesBtn")
        self.verticalLayout_3.addWidget(self.filterChangesBtn)
        self.tabWidget.addTab(self.changesTab, "")
        self.newRowsTab = QtWidgets.QWidget()
        self.newRowsTab.setObjectName("newRowsTab")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.newRowsTab)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.newRows = QtWidgets.QTextBrowser(self.newRowsTab)
        self.newRows.setObjectName("newRows")
        self.verticalLayout_4.addWidget(self.newRows)
        self.tabWidget.addTab(self.newRowsTab, "")
        self.rowsLostTab = QtWidgets.QWidget()
        self.rowsLostTab.setObjectName("rowsLostTab")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.rowsLostTab)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.rowsLost = QtWidgets.QTextBrowser(self.rowsLostTab)
        self.rowsLost.setObjectName("rowsLost")
        self.verticalLayout_5.addWidget(self.rowsLost)
        self.tabWidget.addTab(self.rowsLostTab, "")
        self.queryTab = QtWidgets.QWidget()
        self.queryTab.setObjectName("queryTab")
        self.runQueryBtn = QtWidgets.QPushButton(self.queryTab)
        self.runQueryBtn.setGeometry(QtCore.QRect(520, 110, 111, 23))
        self.runQueryBtn.setObjectName("runQueryBtn")
        self.fieldBox = QtWidgets.QComboBox(self.queryTab)
        self.fieldBox.setGeometry(QtCore.QRect(10, 10, 141, 22))
        self.fieldBox.setObjectName("fieldBox")
        self.addConditionBtn = QtWidgets.QPushButton(self.queryTab)
        self.addConditionBtn.setGeometry(QtCore.QRect(520, 10, 111, 23))
        self.addConditionBtn.setObjectName("addConditionBtn")
        self.value = QtWidgets.QLineEdit(self.queryTab)
        self.value.setGeometry(QtCore.QRect(250, 10, 261, 20))
        self.value.setObjectName("value")
        self.queryList = QtWidgets.QTextBrowser(self.queryTab)
        self.queryList.setGeometry(QtCore.QRect(10, 40, 501, 91))
        self.queryList.setObjectName("queryList")
        self.operatorBox = QtWidgets.QComboBox(self.queryTab)
        self.operatorBox.setGeometry(QtCore.QRect(160, 10, 81, 22))
        self.operatorBox.setObjectName("operatorBox")
        self.prePostBox = QtWidgets.QComboBox(self.queryTab)
        self.prePostBox.setGeometry(QtCore.QRect(520, 80, 111, 22))
        self.prePostBox.setObjectName("prePostBox")
        self.clearQueryBtn = QtWidgets.QPushButton(self.queryTab)
        self.clearQueryBtn.setGeometry(QtCore.QRect(520, 50, 111, 23))
        self.clearQueryBtn.setObjectName("clearQueryBtn")
        self.queryOutputPre = QtWidgets.QTableView(self.queryTab)
        self.queryOutputPre.setGeometry(QtCore.QRect(10, 140, 627, 151))
        self.queryOutputPre.setObjectName("queryOutputPre")
        self.queryOutputPost = QtWidgets.QTableView(self.queryTab)
        self.queryOutputPost.setGeometry(QtCore.QRect(10, 300, 627, 151))
        self.queryOutputPost.setObjectName("queryOutputPost")
        self.andBtn = QtWidgets.QPushButton(self.queryTab)
        self.andBtn.setGeometry(QtCore.QRect(140, 10, 101, 23))
        self.andBtn.setObjectName("andBtn")
        self.orBtn = QtWidgets.QPushButton(self.queryTab)
        self.orBtn.setGeometry(QtCore.QRect(320, 10, 101, 23))
        self.orBtn.setObjectName("orBtn")
        self.tabWidget.addTab(self.queryTab, "")
        self.primaryLbl = QtWidgets.QLabel(Dialog)
        self.primaryLbl.setGeometry(QtCore.QRect(9, 40, 51, 31))
        self.primaryLbl.setObjectName("primaryLbl")
        self.compareBtn = QtWidgets.QPushButton(Dialog)
        self.compareBtn.setGeometry(QtCore.QRect(580, 40, 75, 23))
        self.compareBtn.setObjectName("compareBtn")
        self.ignoreLbl = QtWidgets.QLabel(Dialog)
        self.ignoreLbl.setGeometry(QtCore.QRect(310, 39, 41, 41))
        self.ignoreLbl.setObjectName("ignoreLbl")
        self.ignoredFields = QtWidgets.QListWidget(Dialog)
        self.ignoredFields.setGeometry(QtCore.QRect(350, 40, 221, 81))
        self.ignoredFields.setAlternatingRowColors(True)
        self.ignoredFields.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.ignoredFields.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ignoredFields.setObjectName("ignoredFields")
        self.primaryFields = QtWidgets.QListWidget(Dialog)
        self.primaryFields.setGeometry(QtCore.QRect(60, 40, 221, 81))
        self.primaryFields.setAlternatingRowColors(True)
        self.primaryFields.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.primaryFields.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.primaryFields.setObjectName("primaryFields")
        self.fileWriteBox = QtWidgets.QCheckBox(Dialog)
        self.fileWriteBox.setGeometry(QtCore.QRect(610, 90, 16, 17))
        self.fileWriteBox.setText("")
        self.fileWriteBox.setObjectName("fileWriteBox")
        self.fileWriteLbl = QtWidgets.QLabel(Dialog)
        self.fileWriteLbl.setGeometry(QtCore.QRect(590, 70, 61, 16))
        self.fileWriteLbl.setObjectName("fileWriteLbl")
        self.clearBtn = QtWidgets.QPushButton(Dialog)
        self.clearBtn.setGeometry(QtCore.QRect(16, 620, 631, 23))
        self.clearBtn.setObjectName("clearBtn")

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "CSV/Excel Diff"))
        self.label.setText(_translate("Dialog", "File 1"))
        self.label_2.setText(_translate("Dialog", "File 2"))
        self.loadBtn.setText(_translate("Dialog", "Load"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.summaryTab), _translate("Dialog", "Summary"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.duplicatesTab), _translate("Dialog", "Duplicate Keys"))
        self.filterChangesBtn.setText(_translate("Dialog", "Filter Changes"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.changesTab), _translate("Dialog", "Changes"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.newRowsTab), _translate("Dialog", "New Rows"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.rowsLostTab), _translate("Dialog", "Rows Lost"))
        self.runQueryBtn.setText(_translate("Dialog", "Run"))
        self.addConditionBtn.setText(_translate("Dialog", "Add Condition"))
        self.clearQueryBtn.setText(_translate("Dialog", "Clear"))
        self.andBtn.setText(_translate("Dialog", "AND"))
        self.orBtn.setText(_translate("Dialog", "OR"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.queryTab), _translate("Dialog", "Query Data"))
        self.primaryLbl.setText(_translate("Dialog", "Primary\n"
"Field(s)"))
        self.compareBtn.setText(_translate("Dialog", "Compare"))
        self.ignoreLbl.setText(_translate("Dialog", "Ignored\n"
"Fields"))
        self.fileWriteLbl.setText(_translate("Dialog", "Write to File"))
        self.clearBtn.setText(_translate("Dialog", "Clear All"))

        self.primaryLbl.hide()
        self.ignoreLbl.hide()
        self.ignoredFields.hide()
        self.primaryFields.hide()
        self.fileWriteBox.hide()
        self.fileWriteLbl.hide()
        self.compareBtn.hide()

        self.tabWidget.hide()
        self.clearBtn.hide()

        self.loadBtn.clicked.connect(self.load_names)
        self.compareBtn.clicked.connect(self.compare)
        self.clearBtn.clicked.connect(self.clear)
        self.filterChangesBtn.clicked.connect(self.expand_reason)
        self.addConditionBtn.clicked.connect(self.add_condition)
        self.runQueryBtn.clicked.connect(self.run_query)
        self.clearQueryBtn.clicked.connect(self.clear_query)
        self.andBtn.clicked.connect(lambda: self.add_operation("&","AND"))
        self.orBtn.clicked.connect(lambda: self.add_operation("|","OR"))

        self.auto_complete_files()
        
class PandasModel(QtCore.QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe
    """
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[col]
        return None

class App(QtWidgets.QMainWindow, Ui_Dialog):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.setupUi(self)

def main():
    app = QtWidgets.QApplication(sys.argv)
    form = App()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
