__author__ = 'RESarwas'
import sys
import os

try:
    import pyodbc
except ImportError:
    pyodbc = None
    pydir = os.path.dirname(sys.executable)
    print 'pyodbc module not found, make sure it is installed with'
    print pydir + r'\Scripts\pip.exe install pyodbc'
    print 'Don''t have pip?'
    print 'Download <https://bootstrap.pypa.io/get-pip.py> to ' + pydir + r'\Scripts\get-pip.py'
    print 'Then run'
    print sys.executable + ' ' + pydir + r'\Scripts\get-pip.py'
    sys.exit()


def get_connection_or_die():
    conn_string = ("DRIVER={{SQL Server Native Client 11.0}};"
                   "SERVER={0};DATABASE={1};Trusted_Connection=Yes;")
    conn_string = conn_string.format('inpakrovmais', 'akr_facility')
    try:
        connection = pyodbc.connect(conn_string)
        return connection
    except pyodbc.Error:
        # Try to alternative connection string for 2008
        conn_string2 = conn_string.replace('SQL Server Native Client 11.0', 'SQL Server Native Client 10.0')
    try:
        connection = pyodbc.connect(conn_string)
        return connection
    except pyodbc.Error as e:
        # Additional alternatives are 'SQL Native Client' (2005) and 'SQL Server' (2000)
        print("Rats!!  Unable to connect to the database.")
        print("Make sure you have the SQL Server Client installed and")
        print("your AD account has the proper DB permissions.")
        print("Contact regan_sarwas@nps.gov for assistance.")
        print("  Connection: " + conn_string)
        print("         and: " + conn_string2)
        print("  Error: " + e[1])
        sys.exit()


def make_table(connection):
    sql = ("IF NOT (EXISTS (SELECT * "
           "FROM INFORMATION_SCHEMA.TABLES "
           "WHERE TABLE_NAME = 'Photos_In_Filesystem'))"
           "BEGIN"
           "  CREATE TABLE [Photos_In_Filesystem] "
           "  (Folder nvarchar(max), Filename nvarchar(max), Lat float, Lon float, Bytes int, "
           "  Gpsdate datetime2, Exifdate datetime2, Filedate datetime2)"
           "END")
    return execute_sql(connection, sql)


def clear_table(connection):
    sql = "DELETE FROM [Photos_In_Filesystem] "
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
                sql = "INSERT [Photos_In_Filesystem] (Folder, Filename) values ('{0}','{1}')"
                sql = sql.format(*photo)
            else:
                # dictionary of values for each photo
                sql = ("INSERT [Photos_In_Filesystem] "
                       "(Folder, Filename, Lat, Lon, Bytes, Gpsdate, Exifdate, Filedate) values "
                       "('{folder}','{file}', {lat}, {lon}, {bytes}, '{gpsdate}', '{exifdate}', '{filedate}')")
                sql = sql.format(**photo)
            # print(sql)
            wcursor.execute(sql)
    try:
        wcursor.commit()
    except pyodbc.Error as de:
        return "Database error inserting into 'Photos_In_Filesystem'\n" + str(connection) + '\n' + str(de)
    return None


def files_for_folders(root):
    """
    Get the files in the folders below root
    :param root: The full path of the folder to search
    :return: A dictionary of the folders in root with a list of files for each folder.  All paths are relative to root.
    """
    files = {}
    for folder in [f for f in os.listdir(root) if os.path.isdir(os.path.join(root, f))]:
        print folder,
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
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Assumes script is in the Processing folder which is sub to the photos base folder.
    base_dir = os.path.dirname(script_dir)
    photo_dir = os.path.join(base_dir, "ORIGINAL")
    conn = get_connection_or_die()
    make_table(conn)
    clear_table(conn)
    photo_list = [t for t in folder_file_tuples(photo_dir) if is_jpeg(t[1])]
    write_photos(conn, photo_list)
