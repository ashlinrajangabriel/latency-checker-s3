import time
import os
import boto3
from datetime import datetime
import statistics

def create_large_file(file_name, size_in_mb):
    with open(file_name, 'wb') as f:
        f.write(os.urandom(size_in_mb * 1024 * 1024))

def create_bucket(client, bucket, region):
    if region == 'us-east-1':
        response = client.create_bucket(Bucket=bucket)
    else:
        response = client.create_bucket(
            Bucket=bucket,
            CreateBucketConfiguration={
                'LocationConstraint': region
            }
        )
    return response

def delete_bucket(client, bucket):
    # Delete all objects in the bucket
    res = []
    for obj in client.list_objects(Bucket=bucket)['Contents']:
        res.append({'Key': obj['Key']})
    client.delete_objects(Bucket=bucket, Delete={'Objects': res})

    # Now the bucket can be deleted
    response = client.delete_bucket(Bucket=bucket)
    return response


def measure_latency(client, bucket):
    region='eu-west-1'
    start_time = datetime.now()
    _ = client.list_objects(Bucket=bucket)
    elapsed_time = datetime.now() - start_time
    return elapsed_time.total_seconds()

def upload_file(client, file_name, bucket, object_name=None):
    if object_name is None:
        object_name = file_name

    start_time = time.time()
    client.upload_file(file_name, bucket, object_name)
    return time.time() - start_time

def download_file(client, file_name, bucket, object_name=None):
    if object_name is None:
        object_name = file_name

    start_time = time.time()
    client.download_file(bucket, object_name, file_name)
    return time.time() - start_time

if __name__ == "__main__":
    client = boto3.client('s3',
                          region_name=region,
                          aws_access_key_id=access_key,
                          aws_secret_access_key=access_secret)

    
    bucket = 'ajsakillas'

    # You should replace these with your actual upload and download speeds in Mbps
    upload_bandwidth = 10.0  # in Mbps
    download_bandwidth = 50.0  # in Mbps

    # Convert bandwidth from Mbps to MB/s (1 byte = 8 bits)
    upload_bandwidth /= 8
    download_bandwidth /= 8

    # Create the bucket
    create_bucket(client, bucket,region)

    file_sizes = [5, 10, 15]
    upload_times = []
    download_times = []
    latencies = []

    for size in file_sizes:
        file_name = f'testfile_{size}MB'
        object_name = file_name

        # Create a file of size MB
        create_large_file(file_name, size)

        # Measure latency
        latency = measure_latency(client, bucket)
        latencies.append(latency)

        # Test upload speed
        upload_time = upload_file(client, file_name, bucket, object_name)
        upload_times.append(upload_time)
        
        # Estimated upload time based on bandwidth
        estimated_upload_time = size / upload_bandwidth
        upload_latency = upload_time - estimated_upload_time
        print(f"Upload Latency for {size}MB: {upload_latency} seconds")

        # Test download speed
        download_time = download_file(client, file_name, bucket, object_name)
        download_times.append(download_time)

        # Estimated download time based on bandwidth
        estimated_download_time = size / download_bandwidth
        download_latency = download_time - estimated_download_time
        print(f"Download Latency for {size}MB: {download_latency} seconds")

        # Clean up the file
        os.remove(file_name)

    # Calculate averages and speeds in MB/s
    avg_latency = statistics.mean(latencies)
    avg_upload_speed = statistics.mean([size/time for size, time in zip(file_sizes, upload_times)])
    avg_download_speed = statistics.mean([size/time for size, time in zip(file_sizes, download_times)])

    print(f"Average Latency: {avg_latency} seconds")
    print(f"Average Upload speed: {avg_upload_speed} MB/s")
    print(f"Average Download speed: {avg_download_speed} MB/s")

    # Delete the bucket
    delete_bucket(client, bucket)


