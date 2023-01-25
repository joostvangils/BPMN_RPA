import ftplib
import pickle


# The BPMN-RPA FTP module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The BPMN-RPA FTP module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# The BPMN-RPA FTP module is based on the Python ftplib module, which is licensed under the MIT license:
# Copyright (c) 2007 Giampaolo Rodola


class FTP:
    def __init__(self, host, user, password):
        """
        Create a new FTP connection.
        :param host: The host name or IP address of the FTP server.
        :param user: The user name to connect with.
        :param password: The password to connect with.
        """
        self.user = user
        self.password = password
        self.ftp = None
        self.host = host
        self.__connect__()

    def __connect__(self):
        """
        Internal function to connect to the FTP server.
        """
        self.ftp = ftplib.FTP()
        # open FTP connection
        self.ftp.connect(self.host, 21)
        # login
        self.ftp.login(self.user, self.password)

    def __is_picklable__(self, obj: any) -> bool:
        """
        Internal function to determine if the object is pickable.
        :param obj: The object to check.
        :return: True or False
        """
        try:
            pickle.dumps(obj)
            return True
        except Exception as e:
            return False

    def __getstate__(self):
        """
        Internal function for serialization
        """
        state = self.__dict__.copy()
        for key, val in state.items():
            if not self.__is_picklable__(val):
                state[key] = str(val)
        return state

    def __setstate__(self, state):
        """
        Internal function for deserialization
        :param state: The state to set to the 'self' object of the class
        """
        self.__dict__.update(state)
        self.__connect__()

    def close_ftp(self):
        """
        Close FTP connection.
        """
        self.ftp.close()

    def download_ftp_file(self, remote_file, local_file):
        """
        Download a file from the FTP server.
        :param remote_file: The full path to the file to download.
        :param local_file:  The full path to the file to create.
        """
        # download file
        with open(local_file, 'wb') as f:
            self.ftp.retrbinary('RETR ' + remote_file, f.write)

    def upload_ftp_file(self, local_file, remote_file):
        """
        Upload a file to the FTP server.
        :param local_file: The full path to the file to upload.
        :param remote_file: The full path to the file to create.
        """
        # upload file
        self.ftp.storbinary("STOR " + remote_file, open(local_file, 'rb'))

    def list_ftp_files(self, path):
        """
        List the files in a folder on the FTP server.
        :param path: The full path to the folder to list.
        :return: A list of files in the folder.
        """
        # list files in directory
        self.ftp.cwd(path)
        return self.ftp.nlst()

    def list_ftp_files_with_wildcard(self, path, wildcard):
        """
        List the files in a folder with a specific wildcard on the FTP server.
        :param path: The full path to the folder to list.
        :param wildcard: The wildcard of the files to return.
        :return: A list of files in the folder.
        """
        files = []
        self.ftp.cwd(path)
        for file in self.ftp.nlst():
            if file.startswith(wildcard):
                files.append(file)
        return files

    def copy_ftp_file(self, source, destination):
        """
        Copy a file on the FTP server.
        :param source: The full path to the file to copy.
        :param destination: The full path to the destination.
        """
        # download file
        with open(destination, 'wb') as f:
            self.ftp.retrbinary('RETR ' + source, f.write)

    def move_ftp_file(self, source, destination):
        """
        Move a file on the FTP server.
        :param source: The full path to the file to move.
        :param destination: The full path to the destination.
        """
        # download file
        with open(destination, 'wb') as f:
            self.ftp.retrbinary('RETR ' + source, f.write)
        # delete file
        self.ftp.delete(source)

    def delete_ftp_file(self, path):
        """
        Delete a file from the FTP server.
        :param path: The full path to the file to delete.
        """
        # delete file
        self.ftp.delete(path)

    def delete_ftp_folder(self, path):
        """
        Delete a folder on the FTP server.
        :param path: The full path to the folder to delete.
        """
        # delete folder and its contents
        self.ftp.rmd(path)

    def create_ftp_folder(self, path):
        """
        Create a folder on the FTP server.
        :param path: The full path to the folder to create.
        """
        # create folder
        self.ftp.mkd(path)

    def rename_ftp_file(self, source, destination):
        """
        Rename a file on the FTP server.
        :param source: The full path to the file to rename.
        :param destination: The full path to the destination.
        """
        # rename file
        self.ftp.rename(source, destination)

    def rename_ftp_folder(self, source, destination):
        """
        Rename a folder on the FTP server.
        :param source: The full path to the folder to rename.
        :param destination: The full path to the destination.
        """
        # rename folder
        self.ftp.rename(source, destination)

    def get_ftp_file_size(self, path):
        """
        Get the size of a file on the FTP server.
        :param path: The full path to the file.
        :return: The size of the file.
        """
        # get file size
        return self.ftp.size(path)

    def get_ftp_folder_size(self, path):
        """
        Get the size of a folder on the FTP server.
        :param path: The full path to the folder.
        :return: The size of the folder.
        """
        # get folder size
        size = 0
        self.ftp.cwd(path)
        for file in self.ftp.nlst():
            size += self.ftp.size(file)
        return size

    def get_ftp_file_timestamp(self, path):
        """
        Get the timestamp of a file on the FTP server.
        :param path: The full path to the file.
        :return: The timestamp of the file.
        """
        # get file timestamp
        return self.ftp.sendcmd("MDTM " + path)

    def get_ftp_folder_timestamp(self, path):
        """
        Get the timestamp of a folder on the FTP server.
        :param path: The full path to the folder.
        :return: The timestamp of the folder.
        """
        # get folder timestamp
        return self.ftp.sendcmd("MDTM " + path)

    def get_ftp_file_permissions(self, path):
        """
        Get the permissions of a file on the FTP server.
        :param path: The full path to the file.
        :return: The permissions of the file.
        """
        # get file permissions
        return self.ftp.sendcmd("SITE CHMOD " + path)

    def get_ftp_folder_permissions(self, path):
        """
        Get the permissions of a folder on the FTP server.
        :param path: The full path to the folder.
        :return: The permissions of the folder.
        """
        # get folder permissions
        return self.ftp.sendcmd("SITE CHMOD " + path)

    def set_ftp_file_permissions(self, path, permissions):
        """
        Set the permissions of a file on the FTP server.
        :param path: The full path to the file.
        :param permissions: The permissions to set.
        """
        # set file permissions
        self.ftp.sendcmd("SITE CHMOD " + permissions + " " + path)

    def set_ftp_folder_permissions(self, path, permissions):
        """
        Set the permissions of a folder on the FTP server.
        :param path: The full path to the folder.
        :param permissions: The permissions to set.
        """
        # set folder permissions
        self.ftp.sendcmd("SITE CHMOD " + permissions + " " + path)

    def get_ftp_file_owner(self, path):
        """
        Get the owner of a file on the FTP server.
        :param path: The full path to the file.
        :return: The owner of the file.
        """
        # get file owner
        return self.ftp.sendcmd("SITE CHOWN " + path)

    def get_ftp_folder_owner(self, path):
        """
        Get the owner of a folder on the FTP server.
        :param path: The full path to the folder.
        :return: The owner of the folder.
        """
        # get folder owner
        return self.ftp.sendcmd("SITE CHOWN " + path)

    def set_ftp_file_owner(self, path, owner):
        """
        Set the owner of a file on the FTP server.
        :param path: The full path to the file.
        :param owner: The owner to set.
        """
        # set file owner
        self.ftp.sendcmd("SITE CHOWN " + owner + " " + path)

    def set_ftp_folder_owner(self, path, owner):
        """
        Set the owner of a folder on the FTP server.
        :param path: The full path to the folder.
        :param owner: The owner to set.
        """
        # set folder owner
        self.ftp.sendcmd("SITE CHOWN " + owner + " " + path)

    def get_ftp_file_group(self, path):
        """
        Get the group of a file on the FTP server.
        :param path: The full path to the file.
        :return: The group of the file.
        """
        # get file group
        return self.ftp.sendcmd("SITE CHGRP " + path)

    def get_ftp_folder_group(self, path):
        """
        Get the group of a folder on the FTP server.
        :param path: The full path to the folder.
        :return: The group of the folder.
        """
        # get folder group
        return self.ftp.sendcmd("SITE CHGRP " + path)

    def set_ftp_file_group(self, path, group):
        """
        Set the group of a file on the FTP server.
        :param path: The full path to the file.
        :param group: The group to set.
        """
        # set file group
        self.ftp.sendcmd("SITE CHGRP " + group + " " + path)

    def set_ftp_folder_group(self, path, group):
        """
        Set the group of a folder on the FTP server.
        :param path: The full path to the folder.
        :param group: The group to set.
        """
        # set folder group
        self.ftp.sendcmd("SITE CHGRP " + group + " " + path)

    def get_ftp_file_md5(self, path):
        """
        Get the MD5 hash of a file on the FTP server.
        :param path: The full path to the file.
        :return: The MD5 hash of the file.
        """
        # get file md5
        return self.ftp.sendcmd("SITE MD5 " + path)

    def get_ftp_folder_md5(self, path):
        """
        Get the MD5 hash of a folder on the FTP server.
        :param path: The full path to the folder.
        :return: The MD5 hash of the folder.
        """
        # get folder md5
        return self.ftp.sendcmd("SITE MD5 " + path)

    def change_working_directory(self, path):
        """
        Change the working directory on the FTP server.
        :param path: The full path to the folder.
        """
        # change working directory
        self.ftp.cwd(path)

    def get_working_directory(self):
        """
        Get the working directory on the FTP server.
        :return: The working directory.
        """
        # get working directory
        return self.ftp.pwd()

