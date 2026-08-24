# Helm.

Helm is just a package manager for Kubernetes. It is like the apt in Ubuntu. You can create the Helm chart and install and deploy and do many things with that.
!!! tip "💡"
    For this learning, I am using Minikube. You can install minikube from [here](https://minikube.sigs.k8s.io/docs/start/?arch=%2Fwindows%2Fx86-64%2Fstable%2F.exe%20download).

### How to start with the helm.
1. You need to install the Helm chat if it is not installed.
??? note "Installation steps."
    1. cmd: 
    ```javascript
    curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-4
    chmod 700 get_helm.sh
    	./get_helm.sh
    ```
    1. You can ref this [doc ](https://helm.sh/docs/intro/install/)also

1. Install first helloworld chat 
  1. `helm create helloworld` —>> it create the helm chart with the all basic details
  1. `helm install <release name> helloworld`
  

