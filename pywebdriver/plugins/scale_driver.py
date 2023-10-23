# SPDX-FileCopyrightText: 2022 Coop IT Easy SCRLfs
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Class API for implementing a weighing scale."""

import logging
import time
from abc import ABC, abstractmethod
from contextlib import ExitStack
from importlib import import_module
from threading import RLock, Thread

from flask import jsonify

from pywebdriver import app, config, drivers

from .base_driver import AbstractDriver

_logger = logging.getLogger(__name__)

driver = None


class ScaleError(Exception):
    """Base exception."""


class ScaleConnectionError(ScaleError):
    """Raised when the connection with the scale is not healthy when trying to
    acquire data from it.
    """


class ScaleAcquireDataError(ScaleError):
    """An error occurred during the acquiring of data that did not break the
    connection.
    """


class AbstractScaleDriver(Thread, AbstractDriver, ABC):
    VALID_WEIGHT_STATUS = "ok"

    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, daemon=True, **kwargs)

        self.active = False
        self.config = config
        self.connection = None
        self._data = {}
        self._data_lock = RLock()
        self.vendor_product = "default_scale"

    @property
    def weight(self):
        """Return the last reported weight of the scale."""
        with self._data_lock:
            return self._data.get("value", None)

    @property
    def scale_status(self):
        """Return the last reported status of the scale."""
        with self._data_lock:
            return self._data.get("status", ["error"])

    @property
    @abstractmethod
    def poll_interval(self):
        """Time between polls to the scale."""

    def get_vendor_product(self):
        product = self.vendor_product
        if not product:
            return "device_not_found"
        return product

    def get_status(self, **params):
        """Is the device connected or not?"""
        return {
            "status": "connected" if self.active else "disconnected",
            "messages": [],
        }

    @abstractmethod
    def acquire_data(self, connection):
        """Acquire data over the connection."""

    @abstractmethod
    def establish_connection(self):
        """Establish a connection. The connection must be a context manager."""

    def run(self):
        with ExitStack() as exit_stack:
            while True:
                with self._data_lock:
                    self._data = {}
                while not self.active:
                    try:
                        connection = exit_stack.enter_context(
                            self.establish_connection()
                        )
                        self.active = True
                        print("Balança Conectadada")
                    except Exception:
                        _logger.error("failed to connect to scale")
                        time.sleep(1)
                poll_time = 0
                while self.active:
                    try:
                        # Sleep until approximately exactly self.poll_interval
                        # time has passed since previous iteration.
                        current_time = time.perf_counter()
                        sleep_time = self.poll_interval - (current_time - poll_time)
                        if sleep_time > 0:
                            time.sleep(sleep_time)
                        poll_time = time.perf_counter()

                        data = self.acquire_data(connection)
                        with self._data_lock:
                            self._data = data
                    except ScaleConnectionError:
                        _logger.error("connection with scale lost")
                        exit_stack.close()
                        self.active = False
                    except Exception:
                        # While connection is still active, continue and try
                        # again.
                        _logger.exception("error during acquiring of data")


@app.before_first_request
def before_first_request():
    protocol = config.get("scale_driver", "protocol_name", fallback=None)
    if not protocol:
        raise ValueError("scale_driver.protocol_name is not defined")
    module = import_module(".scale_protocols." + protocol, __package__)
    for _, value in module.__dict__.items():
        try:
            result = issubclass(value, AbstractScaleDriver)
        except Exception:
            continue
        if result and value != AbstractScaleDriver:
            driver = value(config=config)
            driver.start()
            drivers["scale"] = driver
            break
    else:
        raise ValueError(
            "could not find scale protocol class in {}".format(module.__name__)
        )


@app.route("/hw_proxy/scale_read", methods=["POST","GET"])
def scale_read_post():
    return jsonify(
        jsonrpc="2.0",
        result={
            "weight": drivers["scale"].weight,
            "unit": "kg",
            "info": drivers["scale"].scale_status,
        },
    )