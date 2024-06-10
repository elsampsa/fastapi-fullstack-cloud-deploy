# FastAPI Fullstack Example Cloud Deployment

- Azure deployment in [az-example-deployment/](az-example-deployment/)
- Kubernetes deployment in [kube-example-deployment/](kube-example-deployment/)
- AWS deployment **TODO**
- GCP deployment **TODO**

*What's in here?*
```
full-stack-fastapi-template/        # tiangolo's original fastapi fullstack example
az-example-deployment/              # azure deployment of the fastapi fullstack example
kube-example-deployment/            # deploying fastapi fullstack example into kubernets cluster
                                    # but in your local machine (with kind) 
azdeploy.py                         # a helper/automatization script used by az-example-deployment/
env2kube.py                         # helper script for injecting kubernets secrets from an env file
                                    # used by the example in kube-example-deployment/
```

## Author(s)

Sampsa Riikonen

## Copyright

(c) Sampsa Riikonen 2024
