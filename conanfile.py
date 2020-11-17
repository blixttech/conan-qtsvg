from conans import ConanFile, CMake, tools, VisualStudioBuildEnvironment
from conans.tools import cpu_count, os_info, SystemPackageTool
from conans.errors import ConanException
from distutils.spawn import find_executable
import os
import re


class QtSvgConan(ConanFile):
    name = "qtsvg"
    description = "SVG module for Qt"
    topics = ("conan", "qtsvg", "svg")
    url = "https://github.com/blixttech/conan-qtsvg.git"
    homepage = "https://code.qt.io/cgit/qt/qtsvg.git"
    license = "LGPL-3.0"  # SPDX Identifiers https://spdx.org/licenses/

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = {"shared": True}

    def set_version(self):
        git = tools.Git(folder=self.recipe_folder)
        version = re.sub(".*/", "", str(git.get_branch()))
        self.version = version

    def requirements(self):
        self.requires("qt/%s@bincrafters/stable" % self.version)

    def source(self):
        self._source_folder = os.path.join(self.source_folder, self.name)
        git = tools.Git(folder=self._source_folder)
        git.clone(("https://code.qt.io/qt/%s.git" % self.name), self.version)

    def build(self):
        if self.settings.os == "Windows" and (not self.settings.compiler == "Visual Studio"):
            raise ConanException("Not yet implemented for this compiler")

        self._source_folder = os.path.join(self.source_folder, self.name)
        self._build_folder = os.path.join(self.build_folder, ("%s-build" % self.name))
        if not os.path.exists(self._build_folder):
            os.mkdir(self._build_folder)

        qmake_pro_file = os.path.join(self._source_folder, ("%s.pro" % self.name))
        qmake_command = os.path.join(self.deps_cpp_info['qt'].rootpath, "bin", "qmake")
        qmake_args = []
        if not self.options.shared:
            qmake_args.append("CONFIG+=staticlib")

        if self.settings.build_type == "Release":
            qmake_args.append("CONFIG+=release")
        elif self.settings.build_type == "Debug":
            qmake_args.append("CONFIG+=debug")
        else:
            raise ConanException("Invalid build type")

        qmake_args.append("-r %s" % qmake_pro_file)

        build_args = []
        if self.settings.os == "Windows":
            build_command = find_executable("jom.exe")
            if build_command:
                build_args.append("-j")
                build_args.append(str(cpu_count()))
            else:
                build_command = find_executable("nmake.exe")
                if not build_command:
                    raise ConanException("Cannot find nmake")
        else:
            build_command = find_executable("make")
            if build_command:
                build_args.append("-j")
                build_args.append(str(cpu_count()))
            else:
                raise ConanException("Cannot find make")

        self.output.info("Using '%s %s'" % (qmake_command, " ".join(qmake_args)))
        self.output.info("Using '%s %s' to build" % (build_command, " ".join(build_args)))

        if self.settings.compiler == "Visual Studio":
            env_build = VisualStudioBuildEnvironment(self)
            with tools.environment_append(env_build.vars):
                vcvars_cmd = tools.vcvars_command(self.settings)
                self.run("cd %s && %s && %s %s" % (self._build_folder,
                                                   vcvars_cmd,
                                                   qmake_command,
                                                   " ".join(qmake_args)))
                self.run("cd %s && %s && %s %s" % (self._build_folder,
                                                   vcvars_cmd,
                                                   build_command,
                                                   " ".join(build_args)))
        else:
            self.run("cd %s && %s %s" % (self._build_folder, qmake_command, " ".join(qmake_args)))
            self.run("cd %s && %s %s" % (self._build_folder, build_command, " ".join(build_args)))

    def package(self):
        self.copy("*", dst="bin", src=os.path.join(self._build_folder, "bin"), symlinks=True)
        self.copy("*", dst="include", src=os.path.join(self._build_folder, "include"), symlinks=True)
        self.copy("*", dst="lib", src=os.path.join(self._build_folder, "lib"), symlinks=True)
        self.copy("*", dst="mkspecs", src=os.path.join(self._build_folder, "mkspecs"), symlinks=True)
        self.copy("*", dst="plugins", src=os.path.join(self._build_folder, "plugins"), symlinks=True)

    def package_info(self):
        if os.path.exists(os.path.join(self.package_folder, "bin")):
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        if os.path.exists(os.path.join(self.package_folder, "plugins")):
            self.env_info.QT_PLUGIN_PATH.append(os.path.join(self.package_folder, "plugins"))

        self.env_info.CMAKE_PREFIX_PATH.append(self.package_folder)
