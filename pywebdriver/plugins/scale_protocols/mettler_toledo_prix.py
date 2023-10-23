# SPDX-FileCopyrightText: 2022 Coop IT Easy SCRLfs
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging
import re
from curses.ascii import ENQ, ETX

import serial

from ..scale_driver import (
    AbstractScaleDriver,
    ScaleAcquireDataError,
    ScaleConnectionError,
)

ANSWER_RE = re.compile(rb"^\?(?P<status>.)|(?P<weight>\d+\.\d+)$")

_logger = logging.getLogger(__name__)


class MettlerToledo8217ScaleDriver(AbstractScaleDriver):
    """Driver for the 8217 Mettler Toledo protocol. Because of Python
    restrictions, the number doesn't come first in the class name.
    """

    def __init__(self, config, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.vendor_product = "mettler_toledo_8217"
        self._poll_interval = self.config.getfloat(
            "scale_driver", "poll_interval", fallback=0.2
        )
        self._last_weight = 0.0

    @property
    def poll_interval(self):
        return self._poll_interval

    @property
    def _port(self):
        return self.config.get("scale_driver", "port", fallback="/dev/ttyS0")

    @property
    def _baudrate(self):
        return self.config.getint("scale_driver", "baudrate", fallback=9600)

    def acquire_data(self, connection):
        """Acquire data over the connection."""
        buffer = self._read_raw_data(connection)
        buffer = buffer.decode("utf-8")
        print("BUFFER")
        print(buffer)
        buffersplit = buffer.split("\x02", 1)
        print("SPLIT BUFFER")
        print(buffersplit)
        buffersplitweight = buffersplit[1].split("\x03", 2)
        print("Buffer OK")
        print(buffersplitweight)
        print(buffer)
        peso = buffersplitweight[0]
        buffersplitweight = peso[0:2] + "." + peso[2::]
        print(buffersplitweight)
        #match = ANSWER_RE.match(buffer)
        #if match is None:
            #raise ValueError("serial readout was not valid")
        #matchdict = match.groupdict()
        #_logger.debug(matchdict)
        status = "OK"
        weight = buffersplitweight
        if weight is not None:
            self._last_weight = float(weight)
            return {
                "value": self._last_weight,
                "status": self.VALID_WEIGHT_STATUS,
            }
        status_byte = int.from_bytes(status, byteorder="big")
        weight_info = []
        if status_byte & 1:
            weight_info.append("moving")
        if status_byte & 1 << 1:
            weight_info.append("over_capacity")
        if status_byte & 1 << 2:
            weight_info.append("negative")
            weight = 0.0
        if status_byte & 1 << 3:
            weight_info.append("outside_zero_capture_range")
        if status_byte & 1 << 4:
            weight_info.append("center_of_zero")
        if status_byte & 1 << 5:
            weight_info.append("net_weight")
        if not weight_info:
            # some scales return the weight once and then only status 0 for
            # each subsequent weight command until the weight changes. in that
            # case, return the last weight.
            weight = self._last_weight
            weight_info = self.VALID_WEIGHT_STATUS
        return {"value": weight, "status": weight_info}

    def _read_raw_data(self, connection):
        buffer = b""
        stx = False
        try:
            __message = str(chr(5))
            connection.write(__message.encode('ascii'))
            print(connection)
        except serial.SerialException as e:
            raise ScaleConnectionError() from e
        while True:
            try:
                connection.flushInput() 
                c = connection.read(14)
                print("Connection")
                print(c)
                buffer += c
            except serial.SerialException as e:
                raise ScaleConnectionError() from e
            if not c:
                # timeout
                #print("Timeout")
                #raise ScaleAcquireDataError("read time-out")
                stx = True
                break
            #if c == b"\x02":
                # start of answer
                #stx = True
                #buffer = b""
            #elif c == b"\x03":
                # end of answer
                #if not stx:
                    #continue
                #break
            #else:
                #buffer += c
        return buffer

    def establish_connection(self):
        """Establish a connection. The connection must be a context manager."""
        return serial.Serial(
            port=self._port,
            baudrate=self._baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1,
        )
