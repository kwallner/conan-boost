import platform

from conans.client.run_environment import RunEnvironment
from conans.model.conan_file import ConanFile, tools
from conans import CMake
import os
import sys

lib_list = ['math', 'wave', 'container', 'contract', 'exception', 'graph', 'iostreams', 'locale', 'log',
            'program_options', 'random', 'regex', 'mpi', 'serialization',
            'coroutine', 'fiber', 'context', 'timer', 'thread', 'chrono', 'date_time',
            'atomic', 'filesystem', 'system', 'graph_parallel', 'python',
            'stacktrace', 'test', 'type_erasure']


class DefaultNameConan(ConanFile):
    name = "DefaultName"
    version = "0.1"
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake"
    options = {
        "shared": [True, False],
        "header_only": [True, False],
        "fPIC": [True, False],
        "skip_lib_rename": [True, False],
        "magic_autolink": [True, False] # enables BOOST_ALL_NO_LIB
    }
    options.update({"without_%s" % libname: [True, False] for libname in lib_list})

    default_options = {
        "shared" : False, 
        "header_only" : False, 
        "fPIC" : True,
        "skip_lib_rename" : False, 
        "magic_autolink" : False # enables BOOST_ALL_NO_LIB
    }
    default_options.update({"without_%s" % libname : libname != "python" for libname in lib_list})
    default_options.update({"bzip2:shared" : False })
    default_options.update({"zlib:shared" : False })

    def build(self):
        cmake = CMake(self)
        if self.options["boost"].header_only:
            cmake.definitions["HEADER_ONLY"] = "TRUE"
        if self.options["boost"].python:
            cmake.definitions["WITH_PYTHON"] = "TRUE"

        cmake.configure()
        cmake.build()

    def test(self):
        bt = self.settings.build_type
        re = RunEnvironment(self)
        with tools.environment_append(re.vars):
            if platform.system() == "Darwin":
                lpath = os.environ["DYLD_LIBRARY_PATH"]
                self.run('DYLD_LIBRARY_PATH=%s ctest --output-on-error -C %s' % (lpath, bt))
            else:
                self.run('ctest --output-on-error -C %s' % bt)
            if self.options["boost"].python:
                os.chdir("bin")
                sys.path.append(".")
                import hello_ext
                hello_ext.greet()
