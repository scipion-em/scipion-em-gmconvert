# -*- coding: utf-8 -*-
# **************************************************************************
# *
# * Authors:     James Krieger (jmkrieger@cnb.csic.es)
# *
# * Biocomputing Unit, Centro Nacional de Biotecnologia, CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'jmkrieger@cnb.csic.es'
# *
# **************************************************************************


"""
This module will provide the conversion of a volume to a Gaussian mixture model
"""
from pyworkflow.protocol import Protocol, params
from pwem.objects import EMFile

from gmconvert import Plugin as gmconvertPlugin

class GMConvertVolume(Protocol):
    """
    This protocol will convert a volume to a Gaussian mixture model
    """
    _label = 'gmconvert volume'

    # -------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        """ Define the input parameters that will be used.
        Params:
            form: this is the form to be populated with sections and params.
        """
        # You need a params to belong to a section:
        form.addSection(label='gmconvert volume')
        form.addParam('inputVolume', params.PointerParam, label="Input volume",
                      important=True,
                      pointerClass='Volume',
                      help='The volume to be converted')
        
        form.addParam('cutoff', params.FloatParam,
                      default=0.05, label='threshold', important=True,
                      help='cutoff for thresholding the volume')        

        form.addParam('numGaussians', params.IntParam,
                      default=10, label='number of Gaussians', important=True)

        form.addParam('outFn', params.StringParam,
                      default='', label='Output filename', important=True)
        
        form.addParam('outMap', params.StringParam,
                      default='', label='Output map filename (optional)')

    # --------------------------- STEPS functions ------------------------------
    def _insertAllSteps(self):
        # Insert processing steps
        self._insertFunctionStep('convertStep')
        self._insertFunctionStep('createOutputStep')

    def convertStep(self):
        args = 'V2G -imap {0} -ogmm {1} -cutoff {2} -ng {3}'.format(self.inputVolume.get().getFileName(), 
                                                                    self._getPath(self.outFn.get()), 
                                                                    self.cutoff.get(), 
                                                                    self.numGaussians.get())
        if self.outMap.get() != '':
            args += ' -oimap {0}'.format(self.outMap.get())

        try:
            gmconvertPlugin.runGMConvert(self, args)
        except:
            # check if it actually finished correctly
            fi = open(self._getLogsPath('run.stdout'), 'r')
            lines = fi.readlines()
            fi.close()

            if not lines[-1].startswith('COMP_TIME_SEC_FINAL'):
                # gmconvert usually raises an non-zero error code regardless 
                # so we should go and read the error information from the log file
                log = open(self._getLogsPath("run.stderr"), 'r')
                if len(log.read().splitlines()) > 0:
                    for line in log.read().splitlines():
                        self.info("ERROR: %s." % line)
                        raise ChildProcessError("gmconvert has failed: %s. See error log "
                                                "for more details." % line) from None

    def createOutputStep(self):
        outFile = EMFile(filename=self._getPath(self.outFn.get()))
        self._defineOutputs(outputFile=outFile)

    # --------------------------- INFO functions -----------------------------------
    def _summary(self):
        """ Summarize what the protocol has done"""
        summary = []
        if self.isFinished():
            summary.append("This protocol has converted {0} to a GMM in {0}." % (self.inputVolume.get().getFileName(), 
                                                                                 self._getPath(self.outFn.get())))
        return summary

    def _methods(self):
        methods = []
        if self.isFinished():
            methods.append("This protocol has converted {0} to a GMM in {0}." % (self.inputVolume.get().getFileName(), 
                                                                                 self._getPath(self.outFn.get())))
        return methods
