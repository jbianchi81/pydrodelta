from minio import Minio, S3Error

from .config import config as g_config
from io import BytesIO, StringIO
from pandas import DataFrame, read_csv, to_datetime
from .util import coalesce

default_config = g_config["minio"] if "minio" in g_config else None

class MinioClient:

    def __init__(self,config : dict = None):
        config = coalesce(config, default_config)
        if config is None:
            self.client = None
            self.bucket_name = None
        else:
            self.client = Minio(config["url"],
                access_key=config["access_key"],
                secret_key=config["secret_key"],
                secure=config["secure"]
            )
            self.bucket_name = config["bucket_name"] if "bucket_name" in config else "plan"

    def saveStringfile(
            self,
            bucket_name : str,
            content : str,
            file_name : str
        ) -> None:
        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)
        byteobj = content.encode('utf-8')
        streamobj = BytesIO(byteobj)
        self.client.put_object(
            bucket_name,
            file_name,
            streamobj,
            len(byteobj)
        )

    def loadStringFile(
            self,
            bucket_name : str,
            file_name : str
        ) -> str:
        response = self.client.get_object(
            bucket_name,
            file_name)
        return response.data.decode()

    def saveDataFrame(
            self,
            bucket_name : str,
            data : DataFrame,
            file_name : str
        ) -> None:
        self.saveStringfile(
            bucket_name,
            data.to_csv(),
            file_name
        )

    def loadDataFrame(
            self,
            bucket_name : str,
            file_name : str
        ) -> DataFrame:
        content = self.loadStringFile(
            bucket_name,
            file_name
        )
        return read_csv(StringIO(content))

    def saveSeriesData(
            self,
            bucket_name : str,
            data : DataFrame,
            file_name : str
        ) -> None:
        self.saveStringfile(
            bucket_name,
            data.reset_index().to_csv(index=False),
            file_name
        )

    def loadSeriesData(
            self,
            bucket_name : str,
            file_name : str
        ) -> DataFrame:
        try:
            result = self.client.stat_object(bucket_name, file_name)
        except S3Error as e:
            raise ValueError("Object not found in storage: %s" % str(e))
        data = self.loadDataFrame(
            bucket_name,
            file_name
        )
        data = data.set_index("timestart")
        data.index = to_datetime(data.index)
        return data

    def assertClient(self):
        if self.client is None:
            raise ValueError("Persistent storage server is not running")
