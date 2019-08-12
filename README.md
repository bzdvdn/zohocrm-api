# ZOHOCRM v2 REST API wrapper

# Installation

Install using `pip`...

    pip install zohocrm-api

Or

    git clone https://github.com/bzdvdn/zohocrm-api.git

    python3 setup.py

# Usage

```python
from zohocrm import  ZOHOClient
client = ZOHOClient("<access_token>", "<refresh_token>", "<app_client_id>", "<app_client_secret>") # init client

leads = client.leads.list() # get all leads
lead_statuses = client.leads.list(data={"fields": "Lead_Statuses"})

#update access_token
new_token = client.update_access_token() # save to db
```

# TODO
* full documentation
* examples
* async version
* tests