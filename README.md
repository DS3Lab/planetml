# Doc

### Update Status

``` python
import requests
requests.post('https://planetd.shift.ml/site_stats', json={
  "source": "stanford.edu", # ethz.ch; osg-htc.org
  "total_perfs": 0,
  "num_gpu": 0,
  "num_cpu": 0,
  "note": "string"
}
```
