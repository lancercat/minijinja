import sys

from PySide6 import QtWidgets

from neko_sdk.neko_jinja.performance_monitor import handler
from neko_sdk.neko_jinja.collect_res_osocrNG import collect_resd

if __name__ == '__main__':
    # save_metas("scancfg",["project283"],"/run/media/lasercat/ssddata",DEV_METAS,VDS,METHOD_METAS,get_palette(),{});
    app = QtWidgets.QApplication(sys.argv);
    h=handler("scancfg/meta_moose.json",info_collector=collect_resd);
    h.launch();
    app.exec()

