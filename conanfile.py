from conan import ConanFile
from conan.tools.files import get, patch, chdir, rmdir, copy
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.build import cross_building
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=2.0"


class LinuxHeadersGenericConan(ConanFile):
    name = "linux-headers-generic"
    version = "5.15.109"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.kernel.org/"
    license = "GPL-2.0-only"
    description = "Generic Linux kernel headers"
    topics = ("linux", "headers", "generic")
    settings = "os", "arch", "build_type", "compiler"

    
    def layout(self):
        basic_layout(self, src_folder="source")
    
    def package_id(self):
        del self.info.settings.os
        del self.info.settings.build_type
        del self.info.settings.compiler

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("linux-headers-generic supports only Linux")
        if hasattr(self, "settings_build") and cross_building(self):
            raise ConanInvalidConfiguration("linux-headers-generic can not be cross-compiled")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps_tc = AutotoolsDeps(self)
        deps_tc.generate()

        tc = AutotoolsToolchain(self)
        tc.configure_args = ["--prefix=/"]
        tc.cflags.append("-std=gnu99")
        tc.generate()
        
    def build(self):
        with chdir(self, os.path.join(self.source_folder)):
            autotools = Autotools(self)
            autotools.make(target="headers")

    def package(self):
        copy(self, "COPYING", dst="licenses", src=self.source_folder)
        copy(self, "include/*.h", src=os.path.join(self.source_folder, "usr"), dst="include")
