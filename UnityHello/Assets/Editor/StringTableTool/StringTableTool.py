import xlrd
import os.path
import time
import os
import sys
import codecs

SCRIPT_HEAD = "-- This file is generated by program!\n\
-- Don't change it manaully.\n\
-- Created at: %s\n\
\n\
\n\
"


def format_str(value):
    if type(value) == int or type(value) == float:
        value = str(value)

    value = value.replace('\"', '\\\"')
    value = value.replace('\'', '\\\'')
    return value


def handle_one_sheet(excel, sheet):
    sheet_name = sheet.name.replace(" ", "_")
    if not sheet_name.startswith("OUT_"):
        return
    sheet_name = sheet_name[4:]
    print(sheet_name + " sheet")
    excel["data"][sheet_name] = {}

    if sheet.ncols < 2:
        return {}, -1, "sheet[" + sheet_name + "]" + " columns must >= 2"
    row_idx = 0
    for row_idx in range(0, sheet.nrows):
        row = {}
        col_idx = 0
        for col_idx in range(0, sheet.ncols):
            value = sheet.cell_value(row_idx, col_idx)
            row[col_idx] = format_str(value)
        excel["data"][sheet_name][row[0]] = row


def make_table(filename):
    if not os.path.isfile(filename):
        sys.exit("%s is not a valid filename" % filename)
    book_xlrd = xlrd.open_workbook(filename)

    excel = {}
    excel["filename"] = filename
    excel["data"] = {}

    for sheet in book_xlrd.sheets():
        handle_one_sheet(excel, sheet)

    return excel, 0, "ok"


def get_string(value):
    if value is None:
        return ""
    return value


def write_sheet_to_lua_script(output_path, sheet_name, sheet):
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    output_filename = output_path + "/" + sheet_name + ".lua"
    outfp = codecs.open(output_filename, 'w', 'UTF-8')
    create_time = time.strftime(
        "%a %b %d %H:%M:%S %Y", time.gmtime(time.time()))
    outfp.write(SCRIPT_HEAD % (create_time))

    outfp.write("local " + sheet_name + " =")
    outfp.write("\n{")

    for (row_idx, row) in sheet.items():
        # print(row_idx)
        row_key = get_string(row[0])
        # print(row_key)
        outfp.write("\t[" + "\"" + row_key + "\"" + "] = ")
        row_value = get_string(row[1])
        # print(row_value)
        outfp.write("\"" + row_value + "\",\n")

    outfp.write("}\n")
    outfp.write("\nfunction " + sheet_name +
                ".GetText(key, ...)\n\treturn string.format(" + sheet_name + "[key], ...);\nend\n")
    outfp.write("\nfunction " + sheet_name +
                ".GetTempText(key, ...)\n\treturn string.format(key, ...);\nend\n")

    outfp.write("\nreturn " + sheet_name)

    outfp.close()


def write_to_lua_script(excel, output_path):
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    for (sheet_name, sheet) in excel["data"].items():
        global_dir = output_path + "\\" + sheet_name[12:]
        write_sheet_to_lua_script(global_dir, "StringTable", sheet)


def main():
    if len(sys.argv) < 3:
        sys.exit("usage: StringTableTool.py excel_name output_path")
    filename = sys.argv[1]
    output_path = sys.argv[2]

    if not os.path.exists(filename):
        sys.exit("error: " + filename + " is not exists.")

    data, ret, errstr = make_table(filename)

    if ret != 0:
        print(filename)
        print("error: " + errstr)
    else:
        # print(filename)
        print("res:")
        # print(t)
        print "success!!!!!!!!!!!!!!!!!!!!!!!!!!"
    write_to_lua_script(data, output_path)

if __name__ == '__main__':
    main()
