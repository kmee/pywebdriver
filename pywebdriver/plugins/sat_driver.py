import logging
from collections import OrderedDict

from erpbrasil.driver.sat import driver
from flask import jsonify, request

from pywebdriver import app, drivers

from .base_driver import ThreadDriver

_logger = logging.getLogger(__name__)

order_transmiting = False
sended_orders = OrderedDict()


class SatDriver(ThreadDriver, driver.Sat):
    def __init__(self, *args, **kwargs):
        ThreadDriver.__init__(self)
        driver.Sat.__init__(self, *args, **kwargs)


# if config.get("sat_driver", "sat_path"):
#    driver_config["sat_path"] = config.get(
#        "sat_driver", "sat_path"
#    )

# if config.get("sat_driver", "codigo_ativacao"):
#    driver_config["codigo_ativacao"] = config.get(
#        "sat_driver", "codigo_ativacao"
#    )

# if config.get("sat_driver", "impressora"):
#    driver_config["impressora"] = config.get(
#        "sat_driver", "impressora"
#    )

# if config.get("sat_driver", "printer_params"):
#    driver_config["printer_params"] = config.get(
#        "sat_driver", "printer_params"
#    )

# if config.get("sat_driver", "fiscal_printer_type"):
#    driver_config["fiscal_printer_type"] = config.get(
#        "sat_driver", "fiscal_printer_type"
#    )

# if config.get("sat_driver", "assinatura"):
#    driver_config["assinatura"] = config.get(
#        "sat_driver", "assinatura"
#    )

# if config.get("sat_driver"):
#    sat_driver = SatDriver(**driver_config)
#    drivers["hw_fiscal"] = sat_driver
# else:


def set_transmitted_order_to_dict(order_name, order_value):
    global sended_orders
    if len(sended_orders) > 50:
        last_key = next(reversed(sended_orders))
        last_order = {last_key: sended_orders[last_key]}
        sended_orders.clear()
        sended_orders.update(last_order)

    sended_orders.update({order_name: order_value})


@app.route("/hw_proxy/init", methods=["POST", "GET", "PUT"])
def int_sat():
    res = request.json["params"]["json"]
    sat_driver = SatDriver(**res)
    drivers["hw_fiscal"] = sat_driver
    return jsonify(success=True)
    # TODO: Verificar a questão do retorno do init.
    # {"jsonrpc": "2.0", "id": 581330955, "result": true}


@app.route("/hw_proxy/enviar_cfe_sat", methods=["POST", "GET", "PUT"])
def enviar_cfe_sat():
    global order_transmiting
    res = ""
    if (
        not sended_orders.get(request.json["params"]["json"]["name"])
        and not order_transmiting
    ):
        order_transmiting = True
        for item in request.json["params"]["json"]["orderlines"]:
            item["amount_estimate_tax"] = 0
        res = drivers["hw_fiscal"].action_call_sat(
            "send", request.json["params"]["json"]
        )
        if "06000" in res:
            set_transmitted_order_to_dict(request.json["params"]["json"]["name"], res)
        order_transmiting = False
    elif sended_orders.get(request.json["params"]["json"]["name"]):
        res = sended_orders.get(request.json["params"]["json"]["name"])
    else:
        res = "SAT Ocupado!"

    return jsonify(jsonrpc="2.0", result=res)


@app.route("/hw_proxy/cancelar_cfe", methods=["POST", "GET", "PUT"])
def cancelar_cfe():
    res = drivers["hw_fiscal"].action_call_sat("cancel", request.json["params"]["json"])
    return jsonify(jsonrpc="2.0", result=res)


@app.route("/hw_proxy/reprint_cfe", methods=["POST", "GET", "PUT"])
def reprint_cfe():
    res = drivers["hw_fiscal"].action_call_sat(
        "reprint", request.json["params"]["json"]
    )
    return jsonify(jsonrpc="2.0", result=res)


@app.route("/hw_proxy/sessao_sat", methods=["POST"])
def sessao_sat():
    res = drivers["hw_fiscal"].action_call_sat("sessao")
    return jsonify(jsonrpc="2.0", result=res)


@app.route("/hw_proxy/named_printer_action", methods=["POST"])
def named_printer_action():
    action = request.json["params"]["data"].get("action")
    printer_name_ip = request.json["params"]["data"]["printer_name"]
    if action == "cashbox":
        drivers["escpos"].open_cashbox(printer_name_ip)
    elif action == "print_receipt":
        receipt = request.json["params"]["data"]["receipt"]

        drivers["escpos"].print_img(receipt, printer_name_ip)

    return jsonify(jsonrpc="2.0", result=True)
