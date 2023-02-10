import sys
import os 
import pymel.core as pymel
import maya.cmds as cmd
from os import listdir
from os.path import isfile, join
import math
import json
from collections import OrderedDict
from path_helper import get_module_dir_path
from PySide2 import QtCore,QtGui
from PySide2.QtWidgets  import QWidget,QMessageBox,QFileDialog
from UiLoader import loadUi


#get relative path to Maya python script folder
script_dir_path = get_module_dir_path()
sys.path.append(script_dir_path)



"""
Load and over write .ui(QTdesigner) widget file
"""
class my_form(QWidget):

    #init widget
    def __init__(self):

        #inheritance from QWidget
        super(my_form,self).__init__()

        #load .ui file
        ui_path = script_dir_path + "/Anim_Importer_Exporter.ui"
        loader = QtUiTools.QUiLoader()
        loadUi(ui_path,self)

        #set input type of text field(QLineEdit)
        self.scalar_value.setValidator(QtGui.QIntValidator())
        self.end_frame_text.setValidator(QtGui.QIntValidator())
        self.start_frame_text.setValidator(QtGui.QIntValidator())

        #set click functions of button
        self.del_btn.clicked.connect(self.delete_event)
        self.search_file_btn.clicked.connect(self.find_path_event)
        self.Refresh_btn.clicked.connect(self.refresh_joint_list)
        self.Export_btn.clicked.connect(self.export_event)
        self.import_btn.clicked.connect(self.import_event)
        self.Import_Refresh_btn.clicked.connect(self.refresh_joint_list)

        #refresh Joint list and target joint
        self.refresh_target_joint()
        self.refresh_joint_list()

    #refresh target joint in the importer tab
    def refresh_target_joint(self):
        root_joint = self.find_root_joints()
        self.target_joint_text.setText(root_joint)
    
    #refresh joint list in the exporter tab
    def refresh_joint_list(self):
        self.joint_list.clear()
        all_joint_list = sorted(pymel.ls(type = "transform"))
        for joint in all_joint_list:
            self.joint_list.addItem(str(joint))
            #print(joint)

    #when user press import button on the importer tab
    def import_event(self):
        if (self.dropList.currentItem()):
            folderPath = (self.dropList.currentItem().text())
            folderPath = folderPath.replace("/","\\")

            all_frames = [f for f in listdir(folderPath) if isfile(join(folderPath, f))]

            #set default start frame and end frame if user did not type
            if (self.start_frame_text.text()):
                start_frame = int(self.start_frame_text.text())
            else:
                start_frame = 0

            if (self.end_frame_text.text()):
                end_frame = int(self.end_frame_text.text())
            else:
                end_frame = len(all_frames)
            import_frames = all_frames[start_frame:end_frame]
            scalar_value = int(self.scalar_value.text())

            #temp index
            index = 0
            #import json data into joint in Maya
            for frame in import_frames:
                poseData = json.load(open(folderPath + "\\" + frame))
                for joint_name, joint_data in poseData.iteritems():
                    for channels, each_value in joint_data.iteritems():
                        cmd.setKeyframe('{0}.{1}'.format(joint_name, channels),value = each_value, time = index/scalar_value)
                index += 1

            self.messageDialog('Info', 'Import Done!')
        else:
            self.messageDialog('Careful', 'Nothing selected')


    #when user press export button on the exporter tab
    def export_event(self):

        #open file browser
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        folderPath= QFileDialog.getExistingDirectory(
            None,
            "Open a folder",
            "/home/my_user_name/",
            QFileDialog.ShowDirsOnly
        )
        
        #set the folder name to contain json files, in this case is using Root joint's name
        root_joint = self.find_root_joints()
        root_joint_legal = root_joint
        specialChars = "!#$%^&*():" 
        for specialChar in specialChars:
            root_joint_legal = root_joint_legal.replace(specialChar, '_')

        #get the range of animated frame(first frame and last frame)
        key_times = cmd.keyframe(root_joint, attribute = ('tx','ty','tz','rx','ry','rz'),  q=True, tc=True)
        first_key = int(math.ceil(key_times[0]))
        last_key = int(math.ceil(key_times[-1]))
        
        #read data from each frame
        for frame in range(last_key):
           
            cmd.currentTime(frame)

            #type = "joint"
            #get all object need to export
            joint_list = sorted(pymel.ls(type = "transform"))


            PoseDict = OrderedDict()
            savePath = "{0}/{1}".format(folderPath,root_joint_legal,str(frame)).replace("/","\\")

            #create folder if the export path is not exist
            folder = os.path.exists(savePath)
            if not folder:
                os.makedirs(savePath)


            filePath = "{0}/{1}/frame_{2}.json".format(folderPath,root_joint_legal,str(frame)).replace("/","\\")
            
            #get date from each channel
            for joint in joint_list:
                tx = cmd.getAttr(joint + ".tx")
                ty = cmd.getAttr(joint + ".ty")
                tz = cmd.getAttr(joint + ".tz")
                rx = cmd.getAttr(joint + ".rx")
                ry = cmd.getAttr(joint + ".ry")
                rz = cmd.getAttr(joint + ".rz")
                sx = cmd.getAttr(joint + ".sx")
                sy = cmd.getAttr(joint + ".sy")
                sz = cmd.getAttr(joint + ".sz")

                PoseDict[joint.nodeName()] = {
                    "tx":tx,"rx":rx,"sx":sx,
                    "ty":ty,"ry":ry,"sy":sy,
                    "tz":tz,"rz":rz,"sz":sz
                }

            #write data into json file
            with open(filePath,'w') as p:
                json.dump(PoseDict,p,indent=4)
        
        self.messageDialog('Info', 'Export Done!')
        
    #find root joints in the scene
    def find_root_joints(self):
        joint_list = cmd.ls(type='joint', l=True)
        output = []
        exclusion = []
        for jnt in joint_list:
            # convert all hierarchy into a list
            pars = jnt.split('|')[1:]

            if not set(pars) & set(exclusion):
                for p in pars:
                    if cmd.nodeType(p) == 'joint':
                        output.append(p)
                        exclusion+=pars
                        break
        if(output):
            root_joint = output[0]
        else:
            root_joint = "Please import into scene"

        return (root_joint)

    #show message dialog
    def messageDialog(self,title,message_content):
     msg_box = QMessageBox(QMessageBox.Warning, title,message_content)
     msg_box.exec_()

    #overwrite dragEnter Event of Qwidget
    def dragEnterEvent(self,e):
        print(e)
        if e.mimeData().hasText():
            e.accept()
        else:
            e.ignore()

    #overwrite dropEvent Event of Qwidget
    def dropEvent(self,e):
        
        #impoter list support drag and drop 
        all_file_path = e.mimeData().text()
        
        filePathList = all_file_path.split('\n') 
        print((filePathList))

        message_single = False
        for filePath in filePathList:
            filePath = filePath.replace('file:///', '', 1) 
            if(filePath):
                if((os.path.isdir(filePath))):
                    if(self.dropList.findItems(filePath,QtCore.Qt.MatchExactly)):
                        #Same file, do not add on it
                        pass
                    else:
                        self.dropList.addItem(filePath)
                    
                else:
                    message_single = True
        
        #Can only choose a folder to import
        if(message_single == True):
            self.messageDialog('Careful!', 'Only works for folder')
    
    #when user press remove button on the importer tab
    def delete_event(self):
        selected_items = self.dropList.selectedItems()
        if(selected_items):
            for item in selected_items:
                self.dropList.takeItem(self.dropList.row(item))
        else:
            self.messageDialog('Oops', 'Nothing selected')
    
    #when user press open file browser button
    def find_path_event(self):
        folderPath = self.get_filename()
        if folderPath:
            
            if(self.dropList.findItems(folderPath,QtCore.Qt.MatchExactly)):
                #Same file, do not add on it
                pass
            else:
                self.dropList.addItem(folderPath)

        
    #Open file browser
    def get_filename(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        folderPath= QFileDialog.getExistingDirectory(
            None,
            "Open a folder",
            "/home/my_user_name/",
            QFileDialog.ShowDirsOnly
        )
        return (folderPath)



if __name__ == '__main__':
    #app = QApplication(sys.argv)
    main = my_form()
    main.show()
    #sys.exit(app.exec_())


