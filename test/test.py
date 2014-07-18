import sys
import os
import subprocess

def add_file_to_proj():
    import mod_pbxproj
    proj_file_path = os.path.join(os.path.dirname(__file__), "project.pbxproj")

    project = mod_pbxproj.XcodeProject.Load(proj_file_path)

    # project.add_file('cpp-tests/proj.android/jni/main.cpp')
    #
    # if project.modified:
    project.save()

if __name__ == "__main__":
    tool_path = os.path.join(os.path.dirname(__file__), '..')
    sys.path.append(tool_path)

    add_file_to_proj()
