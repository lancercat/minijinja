import os;
def copylog(host,root,name,branch):
    if(host["addr"]=="Nep"):
        return ;
    key = "~/.ssh/id_rsa";
    if("key" in host):
        key=host["key"];

    dpath=os.path.join(root,host["name"],name);
    os.makedirs(dpath,exist_ok=True)
    cmd="rsync  -az --recursive -e \'ssh -p"+ host["port"]+" -i "+key+"\' " +\
        host["username"]+"@"+host["addr"]+":/"+\
        os.path.join(host["root"],branch,name,"PLAYDAN*.log") + " "+\
        dpath;

    print(cmd);
    os.system(cmd);
def copymodel(host,root,name,branch):
    dpath=os.path.join(root,host["name"]);
    key = "~/.ssh/id_rsa";
    if ("key" in host):
        key = host["key"];
    os.makedirs(dpath,exist_ok=True)
    cmd="rsync  -avz --recursive -e \'ssh -p"+ host["port"]+" -i "+key+"\' " +\
        host["username"]+"@"+host["addr"]+":/"+\
        os.path.join(host["root"],branch,name) + " "+\
        dpath;
    print(cmd);
    os.system(cmd);
