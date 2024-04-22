import pprint

import xmltodict

from neko_sdk.neko_jinja.neko_jinja import quick_cast_isalive, quick_cast_get_return_blocking_multiple


def cmd_nvidia_smi():
    return ["nvidia-smi -x -q"];
def nv2number(term):
    return float(term.split(" ",1)[0]);
def handle_nvidia_smi(xml):
    infodict=xmltodict.parse(xml);
    gpus=infodict["nvidia_smi_log"]["gpu"];
    rdict={

    }
    if(type(gpus)!=list):
        gpus=[gpus];

    for g in range(len(gpus)):
        rdict[g]={"temp":nv2number(gpus[g]["temperature"]["gpu_temp"]),
                  "used":nv2number(gpus[g]["fb_memory_usage"]["used"]),
                  "free":nv2number(gpus[g]["fb_memory_usage"]["free"]),
                  "total":nv2number(gpus[g]["fb_memory_usage"]["total"])
                  };
        rdict[g]["is_free"]=(rdict[g]["used"]/rdict[g]["total"])<0.01;
    return rdict;

def cmd_screen():
    return ["screen -ls"]
def handle_screens(slist):
    slist=[l.split("\t")[1:] for l in slist.split("\n")[1:-2]]
    rslist=[];
    for s in slist:
        if(s[0].find("GID")!=-1):
            rslist.append({
                "pid":int(s[0].split(".",1)[0]),
                "mname":s[0].split(".",1)[1].split("GID")[0],
                "gpuid": int(s[0].split(".", 1)[1].split("GID")[1])
            })
    return rslist;

def cmd_disk_space():
    return ["df -Ph . | tail -1 | awk \'{print $4}\'"];
def handle_disk_space(path):
    if(path.find("G")==-1):
        return 0;
    else:
        return int(float(path.split("G")[0]));

def cmd_available_ram_in_kb():
    return ["cat /proc/meminfo | grep MemAvailable | awk \'{ print $2 }\'"];
def handle_available_ram_by_kb(raw):
    return int(raw)/1024/1024;

def cast_info_spells(dev,cmds,handlers,names):
    rdict={};
    cout=quick_cast_get_return_blocking_multiple(dev,cmds);
    for c,h,n in zip(cout,handlers,names):
        rdict[n]=h(c);
    return rdict;

def info_spell_v1(devs):
    cmds = [cmd_nvidia_smi(),cmd_screen(),cmd_disk_space(),cmd_available_ram_in_kb()];
    handlers=[handle_nvidia_smi,handle_screens,handle_disk_space,handle_available_ram_by_kb];
    names = ["GPUs","OsocrTasks","DISK","RAM"];
    rdict={};
    for dname in devs:
        if(quick_cast_isalive(devs[dname])):
            rdict[dname]=cast_info_spells(devs[dname],cmds,handlers,names);
            rdict[dname]["status"]="Online";
        else:
            rdict[dname]={};
            rdict[dname]["status"] = "Lost";
            print(dname,"is lost!");
    return rdict;


if __name__ == '__main__':
    from neko_sdk.environment.hosts_fx import get_dev_meta
    devs = get_dev_meta("");
    rdict=info_spell_v1(devs);
    pprint.pprint(rdict);


