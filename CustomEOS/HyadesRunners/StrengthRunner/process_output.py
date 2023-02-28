def read_output(index):
    from openpyxl import load_workbook
    
    wb = load_workbook(filename='hyades_input.xlsx')
    densities = wb.worksheets[3]['B2:ADU202']
    pressures = wb.worksheets[1]['B2:ADU202']
    
    return (densities, pressures)

