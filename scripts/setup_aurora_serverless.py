import boto3
import os
import time
import environ

# Initialize environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(os.path.dirname(__file__), '../src/.env'))

# Load environment variables
DB_NAME = env("DB_NAME", default="your_aurora_db")
DB_USER = env("DB_USER", default="username")
DB_PASSWORD = env("DB_PASSWORD", default="password")
DB_CLUSTER_IDENTIFIER = env("DB_CLUSTER_IDENTIFIER", default="aurora-cluster")
DB_INSTANCE_IDENTIFIER = env("DB_INSTANCE_IDENTIFIER", default="aurora-instance")
DB_ENGINE = env("DB_ENGINE", default="aurora-postgresql")
DB_ENGINE_VERSION = env("DB_ENGINE_VERSION", default="16.1")
DB_REGION = env("DB_REGION", default="us-east-1")

# Initialize boto3 client
rds_client = boto3.client('rds', region_name=DB_REGION)

def create_db_cluster():
    try:
        response = rds_client.create_db_cluster(
            DBClusterIdentifier=DB_CLUSTER_IDENTIFIER,
            Engine=DB_ENGINE,
            EngineVersion=DB_ENGINE_VERSION,
            MasterUsername=DB_USER,
            MasterUserPassword=DB_PASSWORD,
            DatabaseName=DB_NAME,
            ServerlessV2ScalingConfiguration={
                'MinCapacity': 0.5,
                'MaxCapacity': 8    
            },
            BackupRetentionPeriod=7,
            StorageEncrypted=True,
            EnableIAMDatabaseAuthentication=True
        )
        print(f"Creating DB Cluster: {DB_CLUSTER_IDENTIFIER}")
        return response
    except Exception as e:
        print(f"Error creating DB Cluster: {e}")

def create_db_instance():
    try:
        response = rds_client.create_db_instance(
            DBInstanceIdentifier=DB_INSTANCE_IDENTIFIER,
            DBClusterIdentifier=DB_CLUSTER_IDENTIFIER,
            Engine=DB_ENGINE,
            DBInstanceClass='db.serverless',
            PubliclyAccessible=False
        )
        print(f"Creating DB Instance: {DB_INSTANCE_IDENTIFIER}")
        return response
    except Exception as e:
        print(f"Error creating DB Instance: {e}")

def wait_for_cluster_available():
    print("Waiting for DB Cluster to become available...")
    while True:
        response = rds_client.describe_db_clusters(DBClusterIdentifier=DB_CLUSTER_IDENTIFIER)
        status = response['DBClusters'][0]['Status']
        if status == 'available':
            print("DB Cluster is available.")
            break
        time.sleep(30)

def main():
    create_db_cluster()
    wait_for_cluster_available()
    create_db_instance()

if __name__ == "__main__":
    main()
