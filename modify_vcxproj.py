import os
import sys

from xml.dom import minidom

def os_is_win32():
    return sys.platform == 'win32'

def os_is_mac():
    return sys.platform == 'darwin'

class VCXProject(object):
    def __init__(self, proj_file_path):
        self.xmldoc = minidom.parse(proj_file_path)
        self.file_path = proj_file_path

    def save(self, new_path=None):
        if new_path is None:
            savePath = self.file_path
        else:
            if os.path.isabs(new_path):
                savePath = new_path
            else:
                savePath = os.path.abspath(new_path)

        print("Saving the vcxproj to %s" % savePath)

        if not os.path.isabs(savePath):
            savePath = os.path.abspath(savePath)

        file_obj = open(savePath, "w")
        self.xmldoc.writexml(file_obj, encoding="utf-8")
        file_obj.close()

        file_obj = open(savePath, "r")
        file_content = file_obj.read()
        file_obj.close()

        file_content = file_content.replace("&quot;", "\"")
        file_content = file_content.replace("/>", " />")

        if os_is_mac():
            file_content = file_content.replace("\n", "\r\n")

        file_content = file_content.replace("?><", "?>\r\n<")

        file_obj = open(savePath, "w")
        file_obj.write(file_content)
        file_obj.close()

        print("Saving Finished")

    def remove_lib(self, lib_name, lib_dir):
        cfg_nodes = self.xmldoc.getElementsByTagName("ItemDefinitionGroup")
        for cfg_node in cfg_nodes:
            cond_attr = cfg_node.attributes["Condition"].value
            if cond_attr.lower().find("debug") >= 0:
                cur_mode = "Debug"
            else:
                cur_mode = "Release"

            # remove the linked lib config
            link_node = cfg_node.getElementsByTagName("Link")[0]
            depends_node = link_node.getElementsByTagName("AdditionalDependencies")[0]
            link_info = depends_node.firstChild.nodeValue
            cur_libs = link_info.split(";")
            link_modified = False
            for lib in cur_libs:
                if lib == lib_name:
                    print("Remove linked library %s from \"%s\" configuration" % (lib, cur_mode))
                    cur_libs.remove(lib)
                    link_modified = True

            if link_modified:
                link_info = ";".join(cur_libs)
                depends_node.firstChild.nodeValue = link_info

            # remove the copy command in build event
            build_events = ("PreBuildEvent", "PostBuildEvent", "PreLinkEvent")
            for event in build_events:
                event_node = cfg_node.getElementsByTagName(event)[0]
                cmd_node = event_node.getElementsByTagName("Command")[0]
                cmd = cmd_node.firstChild.nodeValue
                cmd_modified = False
                if len(cmd) > 0:
                    import io
                    buf = io.StringIO(cmd)
                    newlines = []
                    for cmd_line in buf.readlines():
                        if cmd_line.find(lib_dir) < 0:
                            newlines.append(cmd_line)
                        else:
                            print("Remove command line \"%s\" from \"%s\" in \"%s\" configuration" % (cmd_line, event, cur_mode))
                            cmd_modified = True

                if cmd_modified:
                    cmd_node.firstChild.nodeValue = ("".join(newlines)).rstrip("\r\n")

    def add_lib(self, lib_name, add_copy_cmd=None, cmd_event="PreBuildEvent"):
        cfg_nodes = self.xmldoc.getElementsByTagName("ItemDefinitionGroup")
        for cfg_node in cfg_nodes:
            cond_attr = cfg_node.attributes["Condition"].value
            if cond_attr.lower().find("debug") >= 0:
                cur_mode = "Debug"
            else:
                cur_mode = "Release"

            # add the linked lib config
            link_node = cfg_node.getElementsByTagName("Link")[0]
            depends_node = link_node.getElementsByTagName("AdditionalDependencies")[0]
            link_info = depends_node.firstChild.nodeValue
            cur_libs = link_info.split(";")
            link_modified = False
            if lib_name not in cur_libs:
                print("Add linked library %s for \"%s\" configuration" % (lib_name, cur_mode))
                cur_libs.insert(0, lib_name)
                link_modified = True

            if link_modified:
                link_info = ";".join(cur_libs)
                depends_node.firstChild.nodeValue = link_info

            # add copy cmd
            if add_copy_cmd is not None:
                event_node = cfg_node.getElementsByTagName(cmd_event)[0]
                cmd_node = event_node.getElementsByTagName("Command")[0]
                cmd = cmd_node.firstChild.nodeValue
                if cmd.find(add_copy_cmd) < 0:
                    newCmd = "%s\r\n%s" % (cmd, add_copy_cmd)
                    print("Add command line \"%s\" for \"%s\" in \"%s\" configuration" % (add_copy_cmd, cmd_event, cur_mode))
                    cmd_node.firstChild.nodeValue = newCmd
