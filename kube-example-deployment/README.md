# Install into kubernetes cluster running on your laptop

*Also your crash course to kubernetes*

## kind

Kind stands for "Kubernetes IN Docker", how to install, ask google.

So you can run a kubernetes cluster on your local laptop - how cool is that!?

*cheatsheet*

```bash
kind
    get clusters # list all clusters
    kind create cluster --name fastapi # create a kind cluster named "fastapi" 
    kind delete cluster --name fastapi # delete kind cluster named "fastapi"
```
kind delete & create commands modify the `~/.kube/config` file (see below). 

Do this:
```bash
kind create cluster --name fastapi
```

Now you have a kubernetes *node* named `fastapi-control-plane` running some *pods* (see below).

## kubectl

`kubectl` talks to the API of your kubernetes cluster.  How to install it, google is your friend.

To which kubernets cluster in particular, is defined by your current kubernetes context.

Context(s) can be found in `~/.kube/config`.  There can be many contexts/clusters defined in there.
Alternatively, you can override the current context, by putting the path of your alternative config file 
into `KUBECONFIG` environmental variable.

*cheatsheet*

```bash
kubectl 
    config get-contexts # list all contexts found in ~/.kube/config
    kubectl config use-context fastapi # uses context of cluster named "fastapi"
    get nodes # get physical (virtual) machines running pods
    get pod -A # get all pods
    logs name --follow
    describe pod name -n default
    delete pod name -n namespace
    get ingress -A
    delete ingress nginx-ingress -n default
    kubectl create secret generic secret-name --from-literal=KEY=VALUE -n default 
```

Do this:
```bash
kubectl config use-context fastapi
```

## load docker images to kubernetes

Kubernetes cluster runs its own docker image server.  Let's upload the images there.

First of all, you need the docker images in your localhost, so do the step "4. Run fastapi locally" as explained
in [here](../az-example-deployment/README.md).

After that, do this:
```bash
kind load docker-image fapi-azure-frontend:latest --name fastapi
kind load docker-image fapi-azure-backend:latest --name fastapi
```

## create secrets

Passwords, tokens and such are deployed as kubernetes secrets.  Kubernetes exposes the secrets as environment variables
for the services running in the cluster.

Do this:
```bash
./envs.bash
```

## create ingress service

Do this:
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
kubectl label nodes fastapi-control-plane ingress-ready=true
```
Here is a link to that last [mystical spell](https://github.com/kubernetes-sigs/kind/issues/3226)

## install your microservices to kubernetes

```bash
kubectl apply \
    -f db-deployment.yaml \
    -f backend-deployment.yaml \
    -f frontend-deployment.yaml \
    -f ingress.yaml
```

## expose port

First, do
```bash
kubectl get pods --namespace=ingress-nginx | grep controller
```
Take the pod name and get the `uuid` from there and use it with this command:
```
kubectl port-forward ingress-nginx-controller-uuid 8080:80 --namespace=ingress-nginx
```
Now the web-frontend should be visible at [http://localhost:8080](http://localhost:8080).

## about ingress

Here's a general overview of how ingress works in Kubernetes:

- 1. Ingress Resource: You define an Ingress resource in a YAML file, specifying the routing rules, i.e., which paths should be routed to which services.

- 2. Ingress Controller: An Ingress Controller is deployed in the cluster, typically as a DaemonSet or Deployment. It watches the Kubernetes API for Ingress resource changes and updates the load balancing configuration accordingly.

- 3. Load Balancing: The Ingress Controller typically configures an external load balancer (like NGINX, HAProxy, or a cloud provider's load balancer) or sets up a reverse proxy within the cluster to route traffic based on the Ingress rules.

- 4. Service Endpoints: The Ingress Controller routes traffic to the appropriate Service endpoints based on the configured rules.

Frontend at your localhost will be at [http://localhost:8080](http://localhost:8080).  The backend address is the frontend calls
must also include the correct port, so use port also in [local.env](local.env).

Some docs in [here](https://kind.sigs.k8s.io/docs/user/ingress/).

How to make trafik ingress to work, I have no idea..!


## more topics

Here are some topics you should chat with your favorite AI assistant:

- kubernetes yaml files
- kubernetes namespaces
- kubernets nodes, the control plane node and pods
- kubernetes operators
- kubernets CRDs (custom resource definitions)
- kustomization.yaml file
- helm charts
- kubernetes secrets and external secrets

Run some of the kubernets yaml files through your favorite AI assistant to get a neat explanation.

Advanced topics:

- ArgoCD
- Crossplane
- Talos linux
- Omni kubernetes clusters
