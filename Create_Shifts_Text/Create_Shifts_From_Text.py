import os, pydicom


def find_plan_files(input_path,outputs=[]):
    files = None
    dirs = None
    for _, dirs, files in os.walk(input_path):
        break
    if input_path.find('Log') != -1:
        for file in files:
            if file.find('Plan') != -1 and file.find('catuser') == 0:
                outputs.append(os.path.join(input_path,file))
    for dir_val in dirs:
        outputs = find_plan_files(os.path.join(input_path,dir_val),outputs)
    return outputs


def get_daily_plan_couch_positions(file):
    values = ['Daily Isocenter', 'Plan Isocenter']
    output = {}
    fid = open(file)
    for line in fid:
        for val in values:
            if line.find(val) == 0:
                line = fid.readline()
                output[val] = line.strip('\n')
                del values[values.index(val)]
                continue
        if line.find('Couch Correction') == 0:
            fid.readline() # burn a line
            for add in ['AP','SI','RL']:
                line = fid.readline()
                output['Couch_'+add] = line.strip('\n')
            break
    fid.close()
    return output


def give_shift_outputs(output):
    new_output = {}
    directions = ['RL', 'AP', 'SI']
    for isocenter in ['Daily','Plan']:
        new_output[isocenter] = {}
        split_up = output[isocenter + ' Isocenter'].split(' ')
        for i, value in enumerate(split_up):
            for direction in directions:
                if value.find(direction) == 0:
                    actual_number = split_up[i+1]
                    actual_number = float(actual_number.split('(')[0])
                    new_output[isocenter][direction] = actual_number
                    break
    isocenter = 'Couch'
    new_output[isocenter] = {}
    for direction in directions:
        actual_number = float(output[isocenter + '_' + direction].split(':')[1])
        new_output[isocenter][direction] = float(actual_number)
    direction = 'RL'
    RL = new_output['Daily'][direction] - new_output['Couch'][direction] - new_output['Plan'][direction]
    RL = -RL # flip sign
    direction = 'AP'
    AP = new_output['Daily'][direction] + new_output['Couch'][direction] - new_output['Plan'][direction]
    direction = 'SI'
    AP = -AP # flip sign
    SI = new_output['Daily'][direction] + new_output['Couch'][direction] - new_output['Plan'][direction]
    return RL, AP, SI


def create_shift_plan_files(log_path, output_path):
    files = find_plan_files(log_path)
    for file in files:
        try:
            output = get_daily_plan_couch_positions(file)
            if output == {}:
                continue
            shifts = give_shift_outputs(output)
            split_up = file.split('\\')
            path_base = ''.join([i + '\\' for i in split_up[:-1]])
            file_name = split_up[-1]
            CT_name = 'CT ' + str(int(file_name[file_name.find('CT')+2:].split('_')[0]))
            dicom_folder = file_name.split('_')
            CT_Folder = ''.join([i + '\\' for i in split_up[:-2]])
            for i in dicom_folder:
                if i.find('CT') == 0:
                    CT_Folder = os.path.join(CT_Folder, i)
                    dicom_file = os.listdir(CT_Folder)[0]
                    ds = pydicom.read_file(os.path.join(CT_Folder, dicom_file))
                    MRN = str(ds.PatientID)
                    Series_InstanceUID = ds.SeriesInstanceUID
                    break
            MRN_folder = os.path.join(output_path, MRN)
            if not os.path.exists(MRN_folder):
                os.makedirs(MRN_folder)
            fid = open(os.path.join(MRN_folder, Series_InstanceUID + '_Shifts.txt'),'w+')
            for shift in shifts:
                fid.write(str(shift) + '\n')
            fid.close()
        except:
            continue
    return None


if __name__ == '__main__':
    pass
