import os
import json
import boto3

SPLIT_THRESHOLD = 100
SPLIT_CHUNKSIZE = 25

# This function capitalizes all text in the original object
def lambda_handler(event, context):
    s3 = boto3.client('s3')
    event = json.loads(event['body'])
    with open(os.path.join("/tmp",event['file_id']), 'wb') as fp:
        s3.download_fileobj(event['bucket'], event['file_id'], fp)
    with open(os.path.join("/tmp",event['file_id']), 'r') as fp:
        contents = [json.loads(x) for x in fp.readlines()]
    
    if len(contents) > SPLIT_THRESHOLD:
        # here we start to split files into chunks, chunk size = 10
        # we assume it has a either a 'prompt' or an 'input' keyword
        # now sort them
        if 'prompt' in contents[0]:
            contents = sorted(contents, key=lambda d: len(d['prompt']))
        elif 'input' in contents[0]:
            contents = sorted(contents, key=lambda d: len(d['input']))
        chunks = [contents[x:x+SPLIT_CHUNKSIZE] for x in range(0, len(contents), SPLIT_CHUNKSIZE)]
        file_names = []
        for idx, chunk in enumerate(chunks):
            chunk_string = "\n".join([json.dumps(x) for x in chunk])
            s3.put_object(Body=chunk_string, Bucket=event['bucket'], Key=event['file_id']+f"_{idx}")
            file_names.append(event['file_id']+f"_{idx}")
        return {'status_code': 200, 'original_length': len(contents), 'file_ids':file_names}
    else:
        return {'status_code': 100, 'original_length': len(contents), 'file_id':event['file_id']}
    
    return {'status_code': 200, 'original_length': len(contents)}