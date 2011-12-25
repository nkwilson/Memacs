# -*- coding: utf-8 -*-
# Time-stamp: <2011-10-26 15:13:31 awieser>

import codecs
import sys
import time
import os
import re
import logging
from common.orgproperty import OrgProperties
from common.reader import CommonReader

INVOCATION_TIME = time.strftime(u"%Y-%m-%dT%H:%M:%S", time.gmtime())


class OrgOutputWriter(object):
    __handler = None
    __test = False

    def __init__(self, short_description, tag, file_name=None,
                test=False, append=False):
        """
        @param file_name:
        """
        self.__test = test
        self.__test_data = ""
        self.__append = append
        self.__time = time.time()
        self.__short_description = short_description
        self.__tag = tag
        self.__file_name = file_name
        self.__existing_ids = []

        if file_name:
            if append and os.path.exists(file_name):
                self.__handler = codecs.open(file_name, 'a', u"utf-8")
                self.__compute_existing_list()
            else:
                self.__handler = codecs.open(file_name, 'w', u"utf-8")
                self.__write_header()
        else:
            self.__write_header()

    def get_test_result(self):
        return self.__test_data

    def write(self, output):
        """
        Write "<output>"
        """
        if self.__handler:
            self.__handler.write(unicode(output))
        else:
            if self.__test:
                self.__test_data += output
            else:
                # don't remove the comma(otherwise there will be a \n)
                print output,

    def writeln(self, output=""):
        """
        Write "<output>\n"
        """
        self.write(unicode(output) + u"\n")

    def __write_header(self):
        """
        Writes the header of the file

        __init__() does call this function
        """
        self.write_commentln(u"-*- coding: utf-8 mode: org -*-")
        self.write_commentln(
            u"this file is generated by " + sys.argv[0] + \
                ".Any modifications will be overwritten upon next invocation!")
        self.write_commentln(
            "To add this file to your org-agenda files open the stub file " + \
                " (file.org) not this file(file.org_archive) with emacs" + \
                "and do following: M-x org-agenda-file-to-front")
        self.write_org_item(
            self.__short_description + "          :Memacs:" + self.__tag + ":")

    def __write_footer(self):
        """
        Writes the footer of the file including calling python script and time

        Don't call this function - call instead function close(),
        close() does call this function
        """
        self.writeln(u"* successfully parsed by " + \
                     sys.argv[0] + u" at " + INVOCATION_TIME \
                     + u" in " + self.__time + u".")

    def write_comment(self, output):
        """
        Write output as comment: "## <output>"
        """
        self.write(u"## " + output)

    def write_commentln(self, output):
        """
        Write output line as comment: "## <output>\n"
        """
        self.write_comment(output + u"\n")

    def write_org_item(self, output):
        """
        Writes an org item line.

        i.e: * <output>\n
        """
        self.writeln("* " + output)

    def write_org_subitem(self, output, note="", properties=OrgProperties()):
        """
        Writes an org item line.

        i.e: * <output>\n
        """
        self.writeln("** " + output)
        if note != "":
            for n in note.splitlines():
                self.writeln("   " + n)
        self.writeln(unicode(properties))

    def __compute_existing_list(self):
        assert self.__existing_ids == []

        data = CommonReader.get_data_from_file(self.__file_name)
        for found_id in re.findall(":ID:(.*)", data):
            found_id = found_id.strip()
            if found_id != "":
                self.__existing_ids.append(found_id)

        logging.debug("there are already %d entries", len(self.__existing_ids))

    def __id_exists(self, id):
        """
        @return: if id already exists in output file
        """
        return id in self.__existing_ids

    def append_org_subitem(self, output, note="", properties=OrgProperties()):
        """
        Checks if subitem exists in orgfile (:ID: <id> is same),
        if not, it will be appended
        """
        if self.__append:
            id = properties.get_id()

            if id == None:
                raise Exception("ID Property not set")

            if self.__id_exists(id):
                # do nothing, id exists ...
                logging.debug("ID exists not appending")
            else:
                # id does not exist so we can append
                logging.debug("ID not exists appending")
                self.write_org_subitem(output, note, properties)

        else:
            raise Exception("cannot use this method, when not in append mode")

    def close(self):
        """
        Writes the footer and closes the file
        @param write_footer: write the foother with time ?
        """
        self.__time = "%1fs " % (time.time() - self.__time)
        if not self.__append:
            self.__write_footer()
        if self.__handler != None:
            self.__handler.close()
