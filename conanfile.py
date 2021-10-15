from conans import ConanFile


class QtSvgConan(ConanFile):
    name = "qtsvg"
    description = "SVG module for Qt"
    topics = ("conan", "qtsvg", "svg")
    url = "https://github.com/blixttech/conan-qtsvg.git"
    homepage = "https://code.qt.io/cgit/qt/qtsvg.git"
    license = "LGPL-3.0"  # SPDX Identifiers https://spdx.org/licenses/

    python_requires = "qtmodulepyreq/0.2.0@blixt/stable"
    python_requires_extend = "qtmodulepyreq.QtModuleConanBase"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = {"shared": True}

    module = "Svg"
