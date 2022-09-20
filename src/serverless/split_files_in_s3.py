import os
import json
import boto3
from collections import defaultdict

SPLIT_THRESHOLD = 1000
SPLIT_CHUNKSIZE = 1000

# This function capitalizes all text in the original object
def lambda_handler(event, context):
    try:
        s3 = boto3.client('s3')
        event = event['body']
        with open(os.path.join("/tmp",event['file_id']), 'wb') as fp:
            s3.download_fileobj(event['bucket'], event['file_id'], fp)
        with open(os.path.join("/tmp",event['file_id']), 'r') as fp:
            contents = [json.loads(x) for x in fp.readlines()]
    
        clusters = defaultdict(list)
        for i, q in enumerate(contents):
            k = (q.get('model', None), q.get('echo', False), q.get('logprobs', 0), q.get('max_tokens', 1), q.get('n', 1), 
                q.get('temperature', 0), q.get('best_of', 1), q.get('top_p', 1),
                (tuple(sorted(q['stop'])) if q.get('stop', None) is not None else None)
                )
            clusters[k].append(q)
    
        token_chunk_size = SPLIT_CHUNKSIZE * 100
    
        chunks = []
        for k, v in clusters.items():
            n_gen = max(k[2], 100)
            chunk_size = token_chunk_size // n_gen
            # v = sorted(v, key=lambda q: -len(q['prompt'].split()))
            for i in range(len(v) // chunk_size + 1):
                qs = v[i*chunk_size: (i+1)*chunk_size]
                if len(qs) == 0:
                    continue
                chunks.append(qs)
                
        if len(chunks) > 1:
            file_names = []
            for idx, chunk in enumerate(chunks):
                chunk_string = "\n".join([json.dumps(x) for x in chunk])
                s3.put_object(Body=chunk_string, Bucket=event['bucket'], Key=event['file_id']+f"_{idx}")
                file_names.append(event['file_id']+f"_{idx}")
            return {'status_code': 200, 'original_length': len(contents), 'file_ids':file_names}
        else:
            return {'status_code': 100, 'original_length': len(contents), 'file_id':event['file_id']}
    except Exception as e:
        return {'status_code': 100, 'original_length': len(contents), 'file_id':event['file_id'], "msg": str(e)}