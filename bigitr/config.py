#
# Copyright 2012 SAS Institute
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import os
import string
import ConfigParser

class Config(ConfigParser.SafeConfigParser):
    def __init__(self, configFile, defaults={}):
        ConfigParser.SafeConfigParser.__init__(self, defaults)
        if isinstance(configFile, str):
            self.readConfig(self.openConfig(configFile))
        else:
            self.readConfig(configFile)
        self.requireAbsolutePaths()

    optionxform = str # case sensitive

    def requireAbsolutePaths(self, *sections):
        sections = set(sections)
        for section in self.sections():
            for option in self.options(section):
                if option in sections or option.endswith('dir'):
                    value = self.get(section, option)
                    if not value.startswith('/'):
                        raise ValueError('"[%s] %s = %s":'
                            ' Value must resolve to absolute path starting with /'
                            %(section, option, value))

    def get(self, *args, **kwargs):
        # cannot use the "var" argument because the environment overrides
        # content in the file.  Using ${} instead of %()s syntax for that
        # reason.
        v = ConfigParser.SafeConfigParser.get(self, *args, **kwargs)
        t = string.Template(v)
        return t.substitute(os.environ)

    def getGlobalFallback(self, section, key, error=True, defaultValue=None):
        'used only for config file types with a GLOBAL default section'
        if self.has_option(section, key):
            return self.get(section, key)
        if self.has_option('GLOBAL', key):
            return self.get('GLOBAL', key)
        if not error:
            return defaultValue
        # raise contextually meaningful NoOptionError using self.get
        self.get(section, key)

    def getDefault(self, section, key, defaultValue):
        if self.has_option(section, key):
            return self.get(section, key)
        return defaultValue

    def getGlobalDefault(self, section, key, defaultValue):
        return self.getGlobalFallback(section, key, error=False, defaultValue=defaultValue)

    def getOptional(self, section, key):
        return self.getDefault(section, key, None)

    def items(self, *args, **kwargs):
        # cannot use the "var" argument because it adds a keyword for
        # each environment variable, so we have to restrict it to the
        # keywords actually present and then interpolate
        i = ConfigParser.SafeConfigParser.items(self, *args, **kwargs)
        return [(x[0], self.get(args[0], x[0])) for x in i]

    def openConfig(self, configFileName):
        return open(configFileName)

    def readConfig(self, configFile):
        self.readfp(configFile)
