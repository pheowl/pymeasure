#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#


import logging

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range

from pymeasure.adapters import VISAAdapter

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class KeysightB2961A(Instrument):
    """ Represents the Keysight B2961A Power supply
    interface for interacting with the instrument.
    """
    ##########
    # Source #
    ##########
    source_mode = Instrument.control(
        ":SOUR:FUNC:MODE?", ":SOUR:FUNC:MODE %s",
        """ A string property that controls the source mode, which can
        take the values 'current' or 'voltage'. The convenience methods
        :meth:`~.KeysightB2961A.apply_current` and
        :meth:`~.KeysightB2961A.apply_voltage` can also be used. """,
        validator=strict_discrete_set,
        values={'current': 'CURR', 'voltage': 'VOLT'},
        map_values=True
    )

    source_func = Instrument.control(
        ":SOUR:FUNC?", ":SOUR:FUNC %s",
        """ A string property that controls the source function, which can
        take the values 'dc' or 'pulse'. """, 
        validator=strict_discrete_set,
        values={'pulse': 'PULS', 'dc': 'DC'},
        map_values=True
    )

    source_enabled = Insturment.measurement(
        "OUTPUT?",
        """ Reads a boolean value that is True if the source is enabled. """,
        cast=bool
    )

    ###############
    # Current (A) #
    ###############
    source_current = Instrument.control(
        ":SOUR:CURR:LEV:IMM:AMPL?", ":SOUR:CURR:LEV:IMM:AMPL %g",
        """ A floating point property that controls the immediate current
        output. """,
        validator=truncated_range,
        values=[-3, 3],
    )
    
    source_current_reading = Instrument.measurement(
        "READ:SOUR?", """ Provides a readback of the sourced current. """)

    source_current_range = Instrument.control(
        ":SOUR:CURR:RANG?", ":SOUR:CURR:RANG %g",
        """ A floating point property that controls the source current
        range. """,
        validator=truncated_range,
        values=[-3, 3],
    )

    source_current_autorange = Instrument.control(
        ":SOUR:CURR:RANG:AUTO?", ":SOUR:CURR:RANG:AUTO %s",
        """ A bool property that controls the source auto range function. """,
        validator=strict_discrete_set,
        values={True: 'ON', False: 'OFF'},
        map_values=True
    )

    ###############
    # Voltage (V) #
    ###############
    source_voltage = Instrument.control(
        ":SOUR:VOLT:LEV:IMM:AMPL?", ":SOUR:VOLT:LEV:IMM:AMPL %g",
        """ A floating point property that controls the immediate voltage
        output. """,
        validator=truncated_range,
        values=[-21, 21],  # device can in principle output 210 V
    )

    source_current_reading = Instrument.measurement(
        "READ:SOUR?", """ Provides a readback of the sourced voltage. """)

    source_voltage_range = Instrument.control(
        ":SOUR:VOLT:RANG?", ":SOUR:VOLT:RANG %g",
        """ A floating point property that controls the source voltage
        range. """,
        validator=truncated_range,
        values=[-21, 21],  # device can in principle output 210 V
    )

    source_voltage_autorange = Instrument.control(
        ":SOUR:VOLT:RANG:AUTO?", ":SOUR:VOLT:RANG:AUTO %s",
        """ A bool property that controls the source auto range function. """,
        validator=strict_discrete_set,
        values={True: 'ON', False: 'OFF'},
        map_values=True
    )

    #########
    # Sense #
    #########

    ###############
    # Current (A) #
    ###############
    current_comp = Instrument.control(
        ":SENS:CURR:PROT?", ":SENS:CURR:PROT %g",
        """ A floating point property that sets the compliance value. The
        setting is applied to both positive and negative sides. """,
        validator=truncated_range,
        values=[-3, 3]
    )

    current_comp_tipped = Instrument.measurement(
        "SENS:CURR:PROT:TRIP?",
        """ Reads the status of the compliance. """,
        cast=bool)

    current = Instrument.measurement(":READ:CURR?",
                                     """ Reads the current in Amps. """
                                     )

    current_range = Instrument.control(
        ":SENS:CURR?", ":CURR %g",
        """ A floating point property that controls the DC current range in
        Amps, which can take values from 0 to 25 A.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[-3, 3],
    )

    ###############
    # Voltage (V) #
    ###############
    voltage_comp = Instrument.control(
        ":SENS:CURR:PROT?", ":SENS:CURR:PROT %g",
        """ A floating point property that sets the compliance value. The
        setting is applied to both positive and negative sides. """,
        validator=truncated_range,
        values=[-3, 3]
    )

    voltage_comp_tipped = Instrument.measurement(
        "SENS:CURR:PROT:TRIP?",
        """ Reads the status of the compliance. """,
        cast=bool)

    voltage = Instrument.measurement(":READ:VOLT?",
                                     """ Reads the voltage in Volts. """
                                     )

    #################
    # _status (0/1) #
    #################
    _status = Instrument.measurement(":OUTP?",
                                     """ Read power supply current output status. """,
                                     )

    def enable(self):
        """ Enables the flow of current.
        """
        self.write(":OUTP 1")

    def disable(self):
        """ Disables the flow of current.
        """
        self.write(":OUTP 0")

    def is_enabled(self):
        """ Returns True if the current supply is enabled.
        """
        return bool(self._status)

    def __init__(self, adapter, name="Keysight B2961A power supply", **kwargs):
        super().__init__(
            adapter, name, **kwargs
        )
        # Set up data transfer format
        if isinstance(self.adapter, VISAAdapter):
            self.adapter.config(
                is_binary=False,
                datatype='float32',
                converter='f',
                separator=','
            )
