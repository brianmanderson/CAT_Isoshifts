import os
from connect import *
import time


class import_dicom_class:
    def __init__(self,path = '\\\\Client\\S$\\ro-admin\\shared\\radiation physics\\BMAnderson\\PhD\\Koay_Patients\\temp\\',round = 1):
        self.round = round
        self.exams_in_case = []
        try:
            self.patient = get_current('Patient')
            self.case = get_current('Case')
            self.patient_id = self.patient.PatientID
            for exam in self.case.Examinations:
                self.exams_in_case.append(exam.Name)
        except:
            self.patient_id = '0'
        self.patient_db = get_current("PatientDB")
        self.path = path
        self.imported_uids = []
        self.down_folder(path)

    def down_folder(self,input_path):
        try:
            time.sleep(.25)
            print('running')
            self.import_dicoms_new(input_path)
        except:
            print('had an error of sorts')
        return None
    def import_dicoms_new(self,file_path):
        if os.path.exists(file_path + 'imported.txt'):
            print('previously imported ' + str(self.round))
            return None
        print('importing dicom')
        time.sleep(1)
        pi = self.patient_db.QueryPatientsFromPath(Path=file_path, Filter={})[0]
        MRN = pi['Id']
        info = self.patient_db.QueryPatientInfo(Filter={"PatientID": MRN})[0]
        # If it isn't, see if it's in the secondary database
        if not info:
            pi = self.patient_db.QueryPatientsFromPath(Path=file_path, Filter={})[0]
            self.patient_db.ImportPatientFromPath(Path=file_path, Patient=pi, SeriesFilter={}, ImportFilters=[])
            self.patient = self.patient_db.LoadPatient(PatientInfo=pi[0], AllowPatientUpgrade=True)
            self.exams_in_case = []
            for exam in self.case.Examinations:
                self.exams_in_case.append(exam.Name)
        else:
            if self.patient_id != MRN:
                print('patient id does not match MRN')
                if self.patient_id != '0':
                    print('saving')
                    self.patient.Save()
                self.patient = self.patient_db.LoadPatient(PatientInfo=info, AllowPatientUpgrade=True)
                self.patient_id = self.patient.PatientID
                for case in self.patient.Cases:
                    self.case = case
                self.case.SetCurrent()
                self.exams_in_case = []
                for exam in self.case.Examinations:
                    self.exams_in_case.append(exam.Name)
            self.imported_uids = [e.Series[0].ImportedDicomUID for e in self.case.Examinations]
            # Check and see if the CT has already been imported
            go = True
            uid = self.patient_db.QuerySeriesFromPath(Path=path_CT,Filter={})[0]['StudyInstanceUid']
            if self.round == 1:
                if not uid in self.imported_uids and uid and go:
                    self.patient.Save()
                    self.patient.ImportDicomDataFromPath(Path=file_path, CaseName=self.case.CaseName, SeriesFilter={},
                                                         ImportFilters=[])
                    self.patient.Save()
                    exam_name = []
                    for exam in self.case.Examinations:
                        if exam.Name not in self.exams_in_case:
                            exam_name.append(exam.Name)
                            print(exam_name)
                            break
                    if exam_name:
                        new_exam_name = file_path.split('\\')[-2]
                        print(exam_name[0] + ' to ' + new_exam_name)
                        self.exams_in_case.append(exam_name[0])
                        self.case.Examinations[exam_name[0]].Name = new_exam_name
                        self.patient.Save()
                        if os.path.exists(file_path + file_path.split('\\')[-2] + '_coordinates.csv'):
                            print('path exists')
                            fid = open(file_path + file_path.split('\\')[-2] + '_coordinates.csv')
                            x = float(fid.readline()[:-1])
                            y = float(fid.readline()[:-1])
                            z = float(fid.readline()[:-1])
                            rotation = float(fid.readline()[:-1]) * 10
                            fid.close()
                        else:
                            print('No values found..')
                            return None
                        self.case.PatientModel.StructureSets[new_exam_name].OnExamination.CreateTransformedExamination(ExaminationName=new_exam_name + '_Transformed', YawRotation=0, PitchRotation=0, RollRotation=rotation,Translation={'x': x, 'y': y, 'z': z}, FrameOfReference='')
                else:
                    print('already imported')
                fid = open(file_path + 'imported.txt', 'w+')
                fid.close()
        os.remove(file_path + 'running.txt')
        return None
def main():
    xxx = 1
if __name__ == "__main__":
    #await_user_input('Select RT Paths file')
    path_base = '\\\\Client\\S$\\shared\\radiation physics\\BMAnderson\\Calli\\Test1\\Reference1\\'
    CT_file_paths = os.listdir(path_base)
    print('running')
    for i in CT_file_paths:
        path_CT = path_base + i + '\\'
        print(path_CT)
        import_dicom_class(path=path_CT)
        time.sleep(1)
