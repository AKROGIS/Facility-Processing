__author__ = 'RESarwas'
import sys
import os

# dependency pyodbc
# C:\Python27\ArcGIS10.3\Scripts\pip.exe install pyodbc

try:
    import pyodbc
except ImportError:
    pyodbc = None
    print 'pyodbc module not found, make sure it is installed with'
    print 'C:\Python27\ArcGIS10.3\Scripts\pip.exe install pyodbc'
    sys.exit()


def get_connection_or_die():
    conn_string = ("DRIVER={{SQL Server Native Client 10.0}};"
                   "SERVER={0};DATABASE={1};Trusted_Connection=Yes;")
    conn_string = conn_string.format('inpakrovmais', 'akr_facility')
    try:
        connection = pyodbc.connect(conn_string)
    except pyodbc.Error as e:
        print("Rats!!  Unable to connect to the database.")
        print("Make sure your AD account has the proper DB permissions.")
        print("Contact Regan (regan_sarwas@nps.gov) for assistance.")
        print("  Connection: " + conn_string)
        print("  Error: " + e[1])
        sys.exit()
    return connection


def make_table(connection):
    sql = ("IF NOT (EXISTS (SELECT * "
           "FROM INFORMATION_SCHEMA.TABLES "
           "WHERE TABLE_NAME = 'Photos_in_filesystem'))"
           "BEGIN"
           "  CREATE TABLE [Photos_in_filesystem] "
           "  (folder nvarchar(max), [file] nvarchar(max), lat float, lon float, bytes int, "
           "  gpsdate datetime2, exifdate datetime2, filedate datetime2)"
           "END")
    return execute_sql(connection, sql)


def clear_table(connection):
    sql = "DELETE FROM [Photos_in_filesystem] "
    return execute_sql(connection, sql)


def execute_sql(connection, sql):
    wcursor = connection.cursor()
    wcursor.execute(sql)
    try:
        wcursor.commit()
    except pyodbc.Error as de:
        return "Database error: " + sql + '\n' + str(connection) + '\n' + str(de)
    return None


def write_photos(connection, photos):
    wcursor = connection.cursor()
    if photos and len(photos[0]) == 2:
        for photo in photos:
            if len(photo) == 2:
                # (folder,file) tuple
                sql = "INSERT [Photos_in_filesystem] ([folder], [file]) values ('{0}','{1}')"
                sql = sql.format(*photo)
            else:
                # dictionary of values for each photo
                sql = ("INSERT [Photos_in_filesystem] "
                       "([folder], [file], lat, lon, bytes, gpsdate, exifdate, filedate) values "
                       "('{folder}','{file}', {lat}, {lon}, {bytes}, '{gpsdate}', '{exifdate}', '{filedate}')")
                sql = sql.format(**photo)
            # print(sql)
            wcursor.execute(sql)
    try:
        wcursor.commit()
    except pyodbc.Error as de:
        return "Database error inserting into 'Photos_in_filesystem'\n" + str(connection) + '\n' + str(de)
    return None


def files_for_folders(root):
    """
    Get the files in the folders below root
    :param root: The full path of the folder to search
    :return: A dictionary of the folders in root with a list of files for each folder.  All paths are relative to root.
    """
    files = {}
    for folder in [f for f in os.listdir(root) if os.path.isdir(os.path.join(root, f))]:
        path = os.path.join(root, folder)
        files[folder] = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    return files


def folder_file_tuples(root):
    """
    Get the (folder,file) info below root
    :param root: The full path of the folder to search
    :return: A list of (folder,file) pairs for each file in each folder below root.
    folder and file are names, not paths.
    """
    pairs = []
    folders = files_for_folders(root)
    for folder in folders:
        for name in folders[folder]:
            pairs.append((folder, name))
    return pairs


def is_image(name):
    ext = os.path.splitext(name)[1].lower()
    return ext in ['.jpg', '.jpeg', '.png', '.gif']


def is_jpeg(name):
    ext = os.path.splitext(name)[1].lower()
    return ext in ['.jpg', '.jpeg']


if __name__ == '__main__':
    photo_dir = r"T:\PROJECTS\AKR\FMSS\PHOTOS\ORIGINAL"
    conn = get_connection_or_die()
    make_table(conn)
    clear_table(conn)
    photo_list = [t for t in folder_file_tuples(photo_dir) if is_jpeg(t[1])]
    write_photos(conn, photo_list)
