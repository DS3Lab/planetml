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
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.gateway = gateway
        self.wd = wd
        self.init = init
        self.is_connected = False
        if self.wd is not None:
            print("Working directory: ", self.wd)

    def _connect(self):
        # Todo: use a context manager to auto-connect, and close the connection
        logger.info(f"Connecting to host: {self.username}@{self.host}")

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        sock = None
        if self.gateway:
            gw_client = paramiko.SSHClient()
            gw_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            gw_client.connect(
                self.gateway, port=self.port, username=self.username, password=self.password)
            sock = gw_client.get_transport().open_channel(
                'direct-tcpip', (self.host, 22), ('', 0)
            )

        kwargs = dict(
            hostname=self.host,
            port=22,
            username=self.username,
            password=self.password,
            sock=sock,
        )

        client.connect(**kwargs)
        self.ssh_client = client
        logger.info(f"Connected to host {self.username}@{self.host}")
        self.is_connected = True

    def execute(self, command):
        parsed_command = f"cd {self.wd} && {self.init} ;{command}"
        return self.execute_raw(parsed_command)

    def execute_raw(self, command):
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        out = stdout.read().decode("utf-8").strip()
        error = stderr.read().decode("utf-8").strip()
        if error:
            logger.error(error)
        return out

    def is_successful(self, work_dir, job_id):
        file_content = self.execute_raw(
            f"cd {self.wd}/{work_dir} && cat lsf.o{job_id}")
        print(file_content)
        if 'Successfully completed.' in file_content:
            return True
        return False


if __name__ == "__main__":
    from pydantic import BaseSettings

    class Settings(BaseSettings):
        lsf_host: str
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
