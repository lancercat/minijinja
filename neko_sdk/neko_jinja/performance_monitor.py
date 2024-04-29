import json
import os
import pprint

import numpy as np
import torch
from PyQt5.uic.Compiler.qtproxies import QtCore
from PySide6 import QtWidgets, QtCore

from neko_sdk.visualization.result_compilers.scan_dual import draw, draw_areas
from neko_sdk.neko_jinja.spells.info_spells import info_spell_v1;
from scipy import stats


class ScrollLabel(QtWidgets.QScrollArea):

    # constructor
    def __init__(self, *args, **kwargs):
        QtWidgets.QScrollArea.__init__(self, *args, **kwargs)

        # making widget resizable
        self.setWidgetResizable(True)
        self.setMaximumWidth(320)
        # making qwidget object
        content = QtWidgets.QWidget(self)
        self.setWidget(content)

        # vertical box layout
        lay = QtWidgets.QVBoxLayout(content)

        # creating label
        self.label = QtWidgets.QLabel(content)

        # setting alignment to the text
        self.label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        # making label multi-line
        self.label.setWordWrap(True)

        # adding label to the layout
        lay.addWidget(self.label)

    # the setText method
    def setText(self, text):
        # setting text to the label
        self.label.setText(text)
def load_meta(cfgpath):
    with open(cfgpath, "r") as fp:
        meta = json.load(fp);
    return meta;

def save_meta(cfgpath,meta):
    with open(cfgpath, "w+") as fp:
        try:
            json.dump(meta,fp);
        except:
            print(cfgpath);
            print(meta);
def save_metas(cfgroot,projects,working_dir,
               devmetas,vds,method_metas,color_metas,bundles={}):
    devpath=os.path.join(cfgroot, "devices.json");
    bundlepath=os.path.join(cfgroot,"bundles.json");
    methodpath = os.path.join(cfgroot, "methods.json");
    colorpath = os.path.join(cfgroot, "colors.json");
    save_meta(devpath,devmetas);
    save_meta(bundlepath,bundles);
    save_meta(methodpath,method_metas);
    save_meta(colorpath,color_metas)
    meta = {
        "devpath":devpath,
        "bundlepath":bundlepath,
        "methodpath":methodpath,
        "colorpath": colorpath,
        "vds":vds,
        "projects": projects,
        "working_dir": working_dir
    }
    save_meta(os.path.join(cfgroot,"meta.json"),meta);


class handler(QtWidgets.QMainWindow):
    def remote_execute(this):
        pass;
    def compile_color(this,meta,color_metas):
        if ("color" in meta):
            return meta["color"];
        elif ("color_section" in meta):
            return color_metas[meta["color_section"]][meta["color_id"]];
        else:
            print("No color");
            return "#ff0000";
    def compile_method(this,method_metas, color_metas):
        cmm = {};
        for m in method_metas:
            try:
                cmm[m] = method_metas[m];
                cmm[m]["color"] = this.compile_color(cmm[m],color_metas);
            except:
                print("something wrong with", m);
        return cmm;
    def load_metas(this,metametapath):
        metameta = load_meta(metametapath);
        devices = load_meta(metameta["devpath"]);
        bundles = load_meta(metameta["bundlepath"]);
        color_metas = load_meta(metameta["colorpath"]);
        methods_raw = load_meta(metameta["methodpath"]);
        methods = this.compile_method(methods_raw, color_metas);
        return devices, bundles, methods,color_metas, metameta;

    def info_collect(this):
        devices, bundles, methods, color_metas, metameta=this.load_metas(this.metametapath);
        resd = this.info_collector(devices, methods, bundles,
                                   metameta["vds"], metameta["working_dir"],
                                   metameta["projects"]
                                   );

        return resd,devices, bundles, methods,color_metas, metameta;
    def extract_kv(this,resd,bench_name,mname,dname,idx=0):
        ks=resd[bench_name][mname][dname].keys();
        vs={}
        for k in ks:
            if(idx is None):
                vs[k]=resd[bench_name][mname][dname][k];
            else:
                vs[k]=resd[bench_name][mname][dname][k][idx];
        return vs;

    def paried_cmp(this,resd,bench_name,dname,mname_A,mname_B,cmpfn,skey,idx):
        da=this.extract_kv(resd,bench_name,mname_A,dname,idx);
        db=this.extract_kv(resd,bench_name,mname_B,dname,idx);
        pva=[];
        pvb=[];
        for k in da:
            if(k not in db or k in skey):
                continue;
            else:
                pva.append(da[k]);
                pvb.append(db[k]);
        return cmpfn(pva,pvb);
    def single_stat(this,resd,bench_name,dname,mname_A,statfn,skey,idx):
        da = this.extract_kv(resd, bench_name, mname_A, dname, idx);
        pva=[];
        for k in da:
            if(k in skey):
                continue;
            else:
                pva.append(da[k]);
        return statfn(pva);
    def do_statisitic(this,resd):
        rdic={};
        bi_fdic={"ttest":{
            "fn":stats.ttest_rel,
            "skip": set(range(0,80001,20000))
            }
        };
        fdic={
            "avg":{
            "fn":np.mean,
            "skip": set(range(0,80001,20000))
            }
        }
        for dev in this.devices:
            rdic[dev]={};
            for bench in resd:
                rdic[dev][bench] = {};
                for base in resd[bench]:
                    if (dev not in resd[bench][base]):
                        continue;
                    rdic[dev][bench][base] = {"mono":{},"bi":{}};


                    for fn in fdic:
                        try:
                            rdic[dev][bench][base]["mono"][fn] = \
                            this.single_stat(resd, bench, dev, base, fdic[fn]["fn"], fdic[fn]["skip"], 0);
                        except:
                            pass;
                    for fn in bi_fdic:
                        if (base not in rdic[dev][bench]):
                            continue;
                        rdic[dev][bench][base]["bi"][fn] = {};
                        for method in resd[bench]:
                            if (method == base):
                                continue;
                            try:
                                rdic[dev][bench][base]["bi"][fn][method] = \
                                    this.paried_cmp(resd, bench, dev, base, method, bi_fdic[fn]["fn"], bi_fdic[fn]["skip"],
                                                    0);
                            except:
                                pass;
        return rdic;


    def render_on_widget(this,resd,devices, bundles, methods,metameta):
        mw = draw(resd, os.path.join(metameta["working_dir"],metameta["projects"][0],"raw","t.png"), methods, devices);
        return mw;
    def renderrange(this,resd,devices, bundles, methods,color_metas):
        bundle=bundles["methods"];
        bs=resd.keys();
        ids={};
        for b in bs:
            dps={};
            for k in bundle:
                dp = {"color":this.compile_color(bundle[k],color_metas)};
                xss=[];
                yss=[];
                for i in range(0,len(bundle[k]["runs"]),2):
                    dname=bundle[k]["runs"][i];
                    mname=bundle[k]["runs"][i+1];
                    xss.append(resd[b][mname][dname].keys());
                    yss.append([resd[b][mname][dname][iid][0] for iid in resd[b][mname][dname]])
                # todo: check sanity of xss;
                dp["x"]=list(xss[0]);
                dp["y"]=yss;
                dps[k]=dp;
            ids[b]=draw_areas(dps);
        return ids;

    # def collect_and_test(this,resd):
    #     pass;
    # def test_all(this,resd,devices,metameta):
    #     for bench_name in resd:
    #         for devname in resd[mname]:
    #             milestones=sorted(list(
    #                 set(metameta["test_keys"]).intersection(
    #                     set(resd[mname][devname].keys())
    #                 )));
    #             if(len(milestones)):
    #                 launch_if_not_likely_done(
    #                     devices[metameta["tester_name"]],devices[devname],mname,
    #                     metameta["working_dir"],"_E"+str(milestones[-1]//200000-1),
    #                     metameta["projects"],metameta["tester_gpu"]);
    #     pass;
    #
    # def test_all_(this):
    #     return this.test_all(this.resd,this.devices,this.metameta);

    def refresh(this):
        print("start collection");
        resd, devices, bundles, methods,color_metas, metameta= this.info_collect();
        info=info_spell_v1(devices);
        this.infopanel.setText(pprint.pformat(info));
        nmw=this.render_on_widget(resd,devices, bundles, methods,metameta);
        # img=this.renderrange(resd,devices,bundles,methods,color_metas);
        this.devices=devices;
        torch.save(resd,os.path.join(metameta["working_dir"],"resd.pt"));
        stat=this.do_statisitic(resd);
        torch.save(stat, os.path.join(metameta["working_dir"], "stat.pt"));
        for dev in stat:
            print(dev);
            for test in stat[dev]:
                print(test);
                for method in stat[dev][test]:
                    print(method,stat[dev][test][method]["mono"]);
        print("saving to",metameta["working_dir"]);
        if(this.mw is not None):
            this.clayout.removeWidget(this.mw);
            this.mw.setParent(None);
            this.mw.hide();
            this.mw.deleteLater();
            this.mw=None;
        this.clayout.addWidget(nmw);
        # this.post_hooks(resd,devices,metameta);
        this.mw=nmw;
        this.resd=resd;
        this.metameta=metameta;



    def arm_test_selector(this):
        this.mlist = QtWidgets.QListWidget();
        this.keylist = QtWidgets.QListWidget();
        this.keylist.addItem("_E0");
        this.keylist.addItem("_E1");
        this.keylist.addItem("latest");
    def arm_test_all(this):
        this.test_untested_btn = QtWidgets.QPushButton();
        this.test_untested_btn.setText("test untested");
        # this.test_untested_btn.clicked.connect(this.test_all_);
        this.toolbar.addWidget(this.test_untested_btn);


    def arm_refresh(this):
        this.refres_btn = QtWidgets.QPushButton();
        this.refres_btn.setText("force refresh");
        this.refres_btn.clicked.connect(this.refresh);
        this.toolbar.addWidget(this.refres_btn);

    def __init__(this,metametapath,refresheach=3600,info_collector=None):
        super(handler, this).__init__()
        this.timer=QtCore.QTimer();
        this.info_collector=info_collector;
        this.toolbar=QtWidgets.QToolBar();
        this.arm_refresh();
        this.arm_test_all();
        this.arm_test_selector();
        this.addToolBar(this.toolbar);
        this.centH=QtWidgets.QWidget();
        this.clayout=QtWidgets.QHBoxLayout();
        this.centH.setLayout(this.clayout);
        this.setCentralWidget(this.centH);
        this.infopanel=ScrollLabel();
        this.clayout.addWidget(this.infopanel);
        this.metametapath=metametapath;
        this.timer.timeout.connect(this.refresh);
        this.mw=None;
        this.show();
        this.refresh();
        this.refresh_each=refresheach;

    def launch(this):
        this.timer.start(this.refresh_each*1000)
