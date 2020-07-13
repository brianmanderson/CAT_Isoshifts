import os


def down_folder(input_path,outputs=[]):
    files = None
    dirs = None
    for _, dirs, files in os.walk(input_path):
        break
    for file in files:
        if file.find('Plan') != -1:
            outputs.append(os.path.join(input_path,file))
    for dir_val in dirs:
        outputs = down_folder(os.path.join(input_path,dir_val),outputs)
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
files = down_folder(r'C:\Users\bmanderson\Desktop\Patient_0')
output_path = r'C:\Users\bmanderson\Desktop\Patient_Outputs'
for file in files:
    output = get_daily_plan_couch_positions(file)
    shifts = give_shift_outputs(output)
    split_up = file.split('\\')
    path_base = ''.join([i + '\\' for i in split_up[:-1]])
    file_name = split_up[-1]
    MRN = file_name.split('_')[1]
    MRN_folder = os.path.join(output_path,MRN)
    CT_name = 'CT ' + str(int(file_name[file_name.find('CT')+2:].split('_')[0]))
    if not os.path.exists(MRN_folder):
        os.makedirs(MRN_folder)
    fid = open(os.path.join(MRN_folder,CT_name + '_Shifts.txt'),'w+')
    for shift in shifts:
        fid.write(str(shift) + '\n')
    fid.close()