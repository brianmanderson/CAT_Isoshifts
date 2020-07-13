from connect import *
import os


class Change_Patient_Class(object):
    def __init__(self):
        self.patient_db = get_current("PatientDB")
    def ChangePatient(self, MRN):
        info_all = self.patient_db.QueryPatientInfo(Filter={"PatientID": MRN}, UseIndexService=False)
        if not info_all:
            info_all = self.patient_db.QueryPatientInfo(Filter={"PatientID": MRN}, UseIndexService=True)
        for info in info_all:
            if info['PatientID'] == MRN:
                break
        patient = self.patient_db.LoadPatient(PatientInfo=info, AllowPatientUpgrade=True)
        return patient


Change_Patient = Change_Patient_Class()
path = r'\\mymdafiles\di_data1\Morfeus\Andrea\Liver projects\Exported_Shifts'
out_path = r'\\mymdafiles\di_data1\Morfeus\Andrea\Liver projects\Finished_Shifts'
for MRN in os.listdir(path):
    if os.path.exists(os.path.join(out_path, MRN, 'Finished.txt')):
        continue
    patient = Change_Patient.ChangePatient(MRN)
    for case in patient.Cases:
        xxx = 1
    # case.SetCurrent()
    imported_UIDs = [e.Series[0].ImportedDicomUID for e in case.Examinations]
    MRN_path = os.path.join(path,MRN)
    plan = case.TreatmentPlans[0]
    structure_sets = plan.GetStructureSet()
    primary = structure_sets.OnExamination.Name
    for file in os.listdir(MRN_path):
        series_instance_UID = file.split('_Shifts')[0]
        if series_instance_UID in imported_UIDs:
            exam_index = imported_UIDs.index(series_instance_UID)
            exam = case.Examinations[exam_index]
            print(exam.Name)
            fid = open(os.path.join(MRN_path,file))
            data = []
            for line in fid:
                data.append(float(line.strip('\n')))
            fid.close()
            case.SetRigidTransformation(FromExaminationName=exam.Name, ToExaminationName=primary, RigidTransformation={ 'YawDegrees': 0, 'PitchDegrees': 0, 'RollDegrees': 0, 'Translation': { 'x': data[0], 'y': -data[1], 'z': data[2] }, 'RotationCenter': { 'x': 0, 'y': 0, 'z': 0 } })
    patient.Save()
    if not os.path.exists(os.path.join(out_path,MRN)):
        os.makedirs(os.path.join(out_path,MRN))
    fid = open(os.path.join(out_path,MRN,'Finished.txt'),'w+')
    fid.close()