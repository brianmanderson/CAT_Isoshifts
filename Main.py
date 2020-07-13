__author__ = 'Brian M Anderson'
# Created on 7/13/2020

'''
Copy CAT log files to Morfeus
'''
copy_log_files = False
if copy_log_files:
    from Create_Shifts_Text.Copy_Logs import down_folder
    output = r'\\mymdafiles\di_data1\Morfeus\Andrea\Copy_Of_Logs'
    base_path = r'G:\CAT\2107\hlms'
    down_folder(base_path, output=output, base_path=base_path)

'''
Create the shift files that you will import to Raystation
'''
create_shift_text = True
if create_shift_text:
    from Create_Shifts_Text.Create_Shifts_From_Text import create_shift_plan_files
    create_shift_plan_files(log_path=r'\\mymdafiles\di_data1\Morfeus\Andrea\Liver projects\LOG files from CAT box',
                            output_path=r'\\mymdafiles\di_data1\Morfeus\Andrea\Liver projects\Exported_Shifts')

'''
From shift files, run Raystation_Code.import_shifts_to_Raystation.py

Make sure that the output_path is set to be the input_path in the import_shifts function
'''

