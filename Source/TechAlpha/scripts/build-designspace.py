# menuTitle: build Roboto Flex avar2 designspaces

import os, glob
from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor
from variableValues.measurements import FontMeasurements


'''

The “TechAlpha” deliverables
----------------------------

A set of sources from the original Roboto Flex parametric axes, plus spacing and the slant source.

Three designspace files including:

A. default
   parametric axes
   blended axes (avar2 data)

B. default
   parametric axes
   9 sources for 5 axes extrema*

C. default
   9 sources for 5 axes extrema*

* axes extrema:               current values:

  | axis |  min |  max |      |  min |  max |
  |------|------|------|      |------|------|
  | Opsz |    6 |  144 |  ->  |    8 |  144 |
  | Wght |  200 |  700 |  ->  |  100 | 1000 |
  | Wdth |   75 |  125 |  ->  |   25 |  151 |
  | Slnt |      |  -10 |      |      |  -10 | ✔
  | Grad |  -50 |   50 |  ->  | -200 |  150 | ✔


'''


def permille(value, unitsPerEm):
    return round(value * 1000 / unitsPerEm)


class RobotoFlexDesignSpaceBuilder:

    baseFolder       = os.path.dirname(os.getcwd())
    sourcesFolder    = os.path.join(baseFolder,    'sources')
    extremaFolder    = os.path.join(sourcesFolder, 'extrema')
    measurementsPath = os.path.join(sourcesFolder, 'measurements.json')
    defaultUFO       = os.path.join(sourcesFolder, 'RobotoFlex_wght400.ufo')
    designspacePath  = os.path.join(sourcesFolder, 'RobotoFlex.designspace')

    familyName = 'Roboto Flex'

    parametricAxes = 'XOPQ XOUC XOLC XOFI XTRA XTUC XTLC XTFI YOPQ YTAS YTDE YTUC YTLC YTFI'.split()
    parametricAxesHidden = False

    blendedAxes = 'opsz wght wdth'.split()

    def __init__(self):
        # collect parametric sources + extrema
        self.sourcesParametric = glob.glob(f'{self.sourcesFolder}/*.ufo')
        self.sourcesExtrema    = glob.glob(f'{self.extremaFolder}/*.ufo')

        # get default measurements
        f = OpenFont(self.defaultUFO, showInterface=False)
        self.unitsPerEm = f.info.unitsPerEm
        self.measurementsDefault = FontMeasurements()
        self.measurementsDefault.read(self.measurementsPath)
        self.measurementsDefault.measure(f)
        f.close()

    @property
    def defaultLocation(self):
        L = { name : permille(self.measurementsDefault.values[name], self.unitsPerEm) for name in self.parametricAxes }
        L['slnt'] = 0
        L['GRAD'] = 0
        L['SPAC'] = 0
        return L

    def addSources(self):
        # add default source
        src = SourceDescriptor()
        src.path       = self.defaultUFO
        src.familyName = self.familyName
        src.location   = self.defaultLocation.copy()
        self.designspace.addSource(src)

        # add slnt source
        L = self.defaultLocation.copy()
        L['slnt'] = -10
        src = SourceDescriptor()
        src.path       = os.path.join(self.sourcesFolder, 'RobotoFlex_slnt-10.ufo')
        src.familyName = self.familyName
        src.location   = L
        self.designspace.addSource(src)

        # add GRAD sources
        for gradeValue in [-200, 150]:
            L = self.defaultLocation.copy()
            L['GRAD'] = gradeValue
            src = SourceDescriptor()
            src.path       = os.path.join(self.sourcesFolder, f'RobotoFlex_GRAD{gradeValue}.ufo')
            src.familyName = self.familyName
            src.location   = L
            self.designspace.addSource(src)

        # add SPAC sources
        for spacingValue in [-100, 100]:
            L = self.defaultLocation.copy()
            L['SPAC'] = spacingValue
            src = SourceDescriptor()
            src.path       = os.path.join(self.sourcesFolder, f'RobotoFlex_SPAC{spacingValue}.ufo')
            src.familyName = self.familyName
            src.location   = L
            self.designspace.addSource(src)

        # add parametric sources
        for name in self.parametricAxes:
            for ufo in self.sourcesParametric:
                if name in ufo:
                    src = SourceDescriptor()
                    src.path       = ufo
                    src.familyName = self.familyName            
                    L = self.defaultLocation.copy()
                    value = int(os.path.splitext(os.path.split(ufo)[-1])[0].split('_')[-1][4:])
                    L[name] = value
                    L['slnt'] = 0
                    L['GRAD'] = 0
                    src.location = L
                    self.designspace.addSource(src)

    def addParametricAxes(self):
        '''
        slnt GRAD SPAC are added manually
        parametric axes are added automatically

        '''
        # add slant axis
        a = AxisDescriptor()
        a.name    = 'slnt'
        a.tag     = 'slnt'
        a.minimum = -10
        a.maximum = 0
        a.default = 0
        self.designspace.addAxis(a)

        # add grades axis
        a = AxisDescriptor()
        a.name    = 'GRAD'
        a.tag     = 'GRAD'
        a.minimum = -200
        a.maximum = 150
        a.default = 0
        self.designspace.addAxis(a)

        # add spacing axis
        a = AxisDescriptor()
        a.name    = 'SPAC'
        a.tag     = 'SPAC'
        a.minimum = -100
        a.maximum = 100
        a.default = 0
        self.designspace.addAxis(a)

        # add parametric axes
        for name in self.parametricAxes:
            # get min/max values
            values = []
            for ufo in self.sourcesParametric:
                if name in ufo:
                    value = int(os.path.splitext(os.path.split(ufo)[-1])[0].split('_')[-1][4:])
                    values.append(value)
            assert len(values)
            values.sort()
            # create axis
            a = AxisDescriptor()
            a.name    = name
            a.tag     = name
            a.minimum = values[0]
            a.maximum = values[1]
            a.default = permille(self.measurementsDefault.values[name], self.unitsPerEm)
            a.hidden  = self.parametricAxesHidden
            self.designspace.addAxis(a)

    def addInstances(self):

        # i = InstanceDescriptor()
        # i.name    = 'slnt'
        # i.tag     = 'slnt'
        # i.minimum = -10
        # i.maximum = 0
        # i.default = 0
        # self.designspace.addInstance(a)
        pass


    def build(self):
        self.designspace = DesignSpaceDocument()
        self.addParametricAxes()
        self.addSources()
        self.addInstances()

    def save(self):
        # save .designspace file
        self.designspace.write(self.designspacePath)


class RobotoFlexDesignSpaceBuilderA(RobotoFlexDesignSpaceBuilder):

    '''
    A. default
       parametric axes
       blended axes (avar2 data)

    '''

    designspacePath = os.path.join(RobotoFlexDesignSpaceBuilder.sourcesFolder, 'RobotoFlexA.designspace')

    def injectBlendedAxes(self):
        '''
        <axes>          
          <axis tag="wght" name="Weight" minimum="100" maximum="900" default="400"></axis>
          <mappings>
              <mapping>
                  <input>
                      <dimension name="Weight" xvalue="900" />
                  </input>
                  <output>
                      <dimension name="XOPQ" xvalue="260" />
                      <dimension name="XTRA" xvalue="370" />
                      <dimension name="YOPQ" xvalue="132" />
                  </output>
              </mapping>
          </mappings>
        </axes>

        see http://github.com/harfbuzz/boring-expansion-spec/blob/main/avar2-in-designspace.md#parametric-use-case

        '''

        # load measurements for later
        M = FontMeasurements()
        M.read(self.measurementsPath)

        # blended axes data
        axesDefaults = {
            'opsz'  : 14,
            'wght'  : 400,
            'wdth'  : 100,
        }
        axesNames = {
            'opsz'  : 'Optical size',
            'wght'  : 'Weight',
            'wdth'  : 'Width',            
        }

        # assemble XML for blended axes
        axes = ''
        for name in self.blendedAxes:
            # get min/max values
            values = []
            for ufo in self.sourcesExtrema:
                if name in ufo:
                    value = int(os.path.splitext(os.path.split(ufo)[-1])[0].split('_')[-1][4:])
                    values.append(value)
            assert len(values)
            values.sort()
            axes += f'    <axis tag="{axesNames[name]}" name="{name}" minimum="{values[0]}" maximum="{values[1]}" default="{axesDefaults[name]}"></axis>\n'

        # assemble XML for blend mappings
        mappings = '    <mappings>\n'
        for name in self.blendedAxes:
            for ufo in self.sourcesExtrema:
                if name in ufo:
                    # get measurements
                    f = OpenFont(ufo, showInterface=False)
                    M.measure(f)
                    mappings += '      <mapping>\n'
                    mappings += '        <input>\n'
                    value = int(os.path.splitext(os.path.split(ufo)[-1])[0].split('_')[-1][4:])
                    mappings += f'          <dimension name="{axesNames[name]}" xvalue="{value}" />\n'
                    mappings += '        </input>\n'
                    mappings += '        <output>\n'
                    for measurementName in self.parametricAxes:
                        mappings += f'          <dimension name="{measurementName}" xvalue="{int(M.values[measurementName])}" />\n'
                    mappings += '        </output>\n'
                    mappings += '      </mapping>\n'
        mappings += '    </mappings>\n'

        # inject assembled xml into designspace
        xml = ''
        with open(self.designspacePath, mode='r') as f:
            for L in f.readlines():
                if L.strip().startswith('<axes>'):
                    xml += L
                    xml += axes
                elif L.strip().startswith('</axes>'):
                    xml += mappings
                    xml += L
                else:
                    xml += L

        # save the final patched designspace xml
        with open(self.designspacePath, mode='w') as f:
            f.write(xml)

    def build(self):
        self.designspace = DesignSpaceDocument()
        self.addParametricAxes()
        self.addSources()
        

class RobotoFlexDesignSpaceBuilderB(RobotoFlexDesignSpaceBuilder):

    designspacePath = os.path.join(RobotoFlexDesignSpaceBuilder.sourcesFolder, 'RobotoFlexB.designspace')


class RobotoFlexDesignSpaceBuilderC(RobotoFlexDesignSpaceBuilder):

    designspacePath = os.path.join(RobotoFlexDesignSpaceBuilder.sourcesFolder, 'RobotoFlexC.designspace')
    parametricAxesHidden = True


# -----
# build
# -----

if __name__ == '__main__':
    
    # D = RobotoFlexDesignSpaceBuilder()
    # D.build()
    # D.save()
    
    D1 = RobotoFlexDesignSpaceBuilderA()
    D1.build()
    D1.save()
    D1.injectBlendedAxes()

    # D2 = RobotoFlexDesignSpaceBuilderB()
    # print(D2.designspacePath)
    # D2.build()
    # D2.save()

    # D3 = RobotoFlexDesignSpaceBuilderC()
    # print(D3.designspacePath)
    # D3.build()
    # D3.save()