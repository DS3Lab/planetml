import requests
import paramiko
from loguru import logger
from dstool.class_utils import singleton

@singleton
class LSFClient(object):
    def __init__(self,
                 host="",
                 port=22,
                 username="",
                 password="",
                 gateway=None,
                 wd=None,
                 init=None,
                ):
        logger.info(f"Connecting to host: {username}@{host}")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.username = username

        sock = None
        if gateway:
            gw_client = paramiko.SSHClient()
            gw_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            gw_client.connect(
                gateway, port=port, username=username, password=password)
            sock = gw_client.get_transport().open_channel(
                'direct-tcpip', (host, 22), ('', 0)
            )
        
        kwargs = dict(
            hostname=host,
            port=22,
            username=username,
            password=password,
            sock=sock,
        )

        client.connect(**kwargs)
        self.ssh_client = client
        logger.info(f"Connected to host {username}@{host}")
        self.wd = wd
        self.init = init
        if self.wd is not None:
            print("Working directory: ", self.wd)

    def execute(self, command):
        parsed_command = f"cd {self.wd} && {self.init} ;{command}"
        print(parsed_command)
        stdin, stdout, stderr = self.ssh_client.exec_command(parsed_command, environment={
            "PATH":"/cluster/home/xiayao/.local/bin/"
        })
        if stderr:
            logger.error(stderr.read().decode("utf-8"))
        return stdout.read().decode("utf-8")

    def submit_job(self, job):
        command = "bsub /cluster/home/xiayao/.local/bin/mls.py"
        return self.execute(command)

if __name__=="__main__":
    from pydantic import BaseSettings

    class Settings(BaseSettings):
        lsf_host:str
        lsf_username: str
        lsf_password: str
        lsf_wd: str
        lsf_init: str
        class Config:
            env_file = '.env'
            env_file_encoding = 'utf-8'
    settings = Settings()
    lsf_client = LSFClient(
        host=settings.lsf_host,
        username=settings.lsf_username,
        password=settings.lsf_password,
        wd=settings.lsf_wd,
        init=settings.lsf_init,
    )
    lsf_client.execute("/cluster/home/xiayao/.local/bin/mls.py")