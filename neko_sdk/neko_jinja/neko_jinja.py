import paramiko;
KF="~/.ssh/id_rsa"

def remote_fire_and_forget(hostname,uname,port,uroot,commands):
    pass;

def is_alive(hostname, uname, port,key=KF):
    try:
        ssh = paramiko.SSHClient();
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy());
        ssh.connect(hostname, username=uname, port=port, key_filename=key);
        return True;
    except:
        return False;

def quick_cast_isalive(devitem):
    if("key" in devitem):
        return is_alive(
            devitem["addr"],
            devitem["username"],
            devitem["port"],
            devitem["key"]
        );
    return is_alive(
        devitem["addr"],
        devitem["username"],
        devitem["port"],
        );


def remote_get_return_blocking(hostname,uname,port,uroot,commands,key=KF):
    ssh = paramiko.SSHClient();
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy());
    ssh.connect(hostname, username=uname,port=port, key_filename=key);
    commands = ["cd " + uroot] + commands;
    exec = "".join([i + ";" for i in commands]);
    stdin, stdout, stderr = ssh.exec_command(exec);
    outstr=stdout.read().decode('ascii');
    ssh.close();
    return outstr;


def quick_cast_get_return_blocking(devitem,commands):
    if ("key" in devitem):
        return remote_get_return_blocking(
            devitem["addr"],
            devitem["username"],
            devitem["port"],
            devitem["root"],
            commands,
            devitem["key"],
        );
    return remote_get_return_blocking(
        devitem["addr"],
        devitem["username"],
        devitem["port"],
        devitem["root"],
        commands,
    );

def remote_get_return_blocking_multiple(hostname,uname,port,uroot,commands_seq,key=KF):
    ssh = paramiko.SSHClient();
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy());
    ssh.connect(hostname, username=uname,port=port, key_filename=key);
    commands_seq = [["cd " + uroot] + commands for commands in commands_seq];
    execs = ["".join([i + ";" for i in commands]) for commands in commands_seq];
    outstrs=[];
    for e in execs:
        stdin, stdout, stderr = ssh.exec_command(e);
        outstr=stdout.read().decode('ascii');
        outstrs.append(outstr)
    ssh.close();
    return outstrs;




def quick_cast_get_return_blocking_multiple(devitem,command_seqs):
    if ("key" in devitem):
        return remote_get_return_blocking_multiple(
            devitem["addr"],
            devitem["username"],
            devitem["port"],
            devitem["root"],
            command_seqs,
            devitem["key"]
        );
    return remote_get_return_blocking_multiple(
        devitem["addr"],
        devitem["username"],
        devitem["port"],
        devitem["root"],
        command_seqs
    );
