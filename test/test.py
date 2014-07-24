import sys
import os

from argparse import ArgumentParser

def test_xcode():
    import mod_pbxproj
    proj_file_path = os.path.join(os.path.dirname(__file__), "project.pbxproj")

    project = mod_pbxproj.XcodeProject.Load(proj_file_path)

    # test remove lib
    project.remove_lib("libbox2d Mac.a")
    project.remove_library_search_paths("../modules/Box2d/prebuilt/mac", target_name="cpp-tests Mac")
    project.remove_user_header_search_paths("../modules/Box2d/include", target_name="cpp-tests Mac")

    # test add lib & lib search path
    parent_group = project.get_or_create_group("mac-libs")
    project.add_file_if_doesnt_exist("../modules/Box2d/prebuilt/mac/libbox2d Mac.a", parent=parent_group, tree="<group>", target="cpp-tests Mac")
    project.add_library_search_paths("../modules/Box2d/prebuilt/mac", target_name="cpp-tests Mac", recursive=False)

    # test add header serch path
    project.add_user_header_search_paths("../modules/Box2d/include", target_name="cpp-tests Mac", recursive=False)

    if project.modified:
        project.save()

def test_vs():
    import modify_vcxproj
    proj_file_path = os.path.join(os.path.dirname(__file__), "cpp-tests.vcxproj")

    project = modify_vcxproj.VCXProject(proj_file_path)

    project.remove_lib("libCocosBuilder.lib", "..\\modules\\cocosbuilder\\prebuilt")
    project.add_lib("libCocosBuilder.lib", "xcopy /Y /Q \"$(ProjectDir)..\\..\\..\\modules\\cocosbuilder\\prebuilt\\win32\\*.*\" \"$(OutDir)\"")

    project.save()

def test_android():
    import modify_mk
    proj_file_path = os.path.join(os.path.dirname(__file__), "Android.mk")

    project = modify_mk.AndroidMK(proj_file_path)

    project.remove_lib("cocostudio_static", "modules/cocostudio/prebuilt/android")
    project.add_lib("cocostudio_static", "modules/cocostudio/prebuilt/android")

    project.save()

if __name__ == "__main__":
    tool_path = os.path.join(os.path.dirname(__file__), '..')
    sys.path.append(tool_path)

    parser = ArgumentParser(description="Generate prebuilt engine for Cocos Engine.")
    parser.add_argument('-x', dest='test_xcode', action="store_true", help='Test modify xcode project.')
    parser.add_argument('-v', dest='test_vs', action="store_true", help='Test modify VS project.')
    parser.add_argument('-a', dest='test_android', action="store_true", help='Test modify Android.mk.')
    (args, unknown) = parser.parse_known_args()

    if len(unknown) > 0:
        print("unknown arguments: %s" % unknown)

    if args.test_xcode:
        test_xcode()

    if args.test_vs:
        test_vs()

    if args.test_android:
        test_android()