Kubernetes Deployment Automation Tool

This script automates the deployment of Kubernetes applications, setting up Helm, installing KEDA (Kubernetes Event-driven Autoscaler), and managing the deployment lifecycle, including monitoring and exposing services.

Features

Kubernetes Cluster Connection: Automatically connects to a Kubernetes cluster using a kubeconfig file.

Helm Setup: Installs Helm if not already installed.

KEDA Deployment: Installs KEDA for autoscaling workloads.

Application Deployment: Deploys a Kubernetes application with configurable resource requests and limits.

Horizontal Pod Autoscaler (HPA): Sets up HPA for CPU and memory-based scaling.

Deployment Monitoring: Verifies the health of the deployment.

Service Exposure: Exposes the application using a Kubernetes Service.

Prerequisites

Python 3.6 or higher

kubectl installed and configured

Helm 3.x installed (or installable via script)

Kubernetes cluster with access configured via ~/.kube/config or a specified kubeconfig file

Python libraries:

kubernetes

Install the required Python dependencies with:

pip install kubernetes

Usage

Run the script with the following options:

python k8s_automation.py --namespace <namespace> --app-name <app-name> \
    --image <container-image> --version <image-version> \
    --cpu-req <cpu-requests> --mem-req <memory-requests> \
    --cpu-lim <cpu-limits> --mem-lim <memory-limits> \
    --cpu-util <cpu-utilization> --mem-util <memory-utilization> \
    --svc-port <service-port> --container-port <container-port>

Required Arguments

--namespace: Kubernetes namespace for the deployment.

--app-name: Name of the application.

--image: Container image for the application.

--version: Version of the container image.

Optional Arguments

--cpu-req: CPU requests (default: 100m).

--mem-req: Memory requests (default: 128Mi).

--cpu-lim: CPU limits (default: 500m).

--mem-lim: Memory limits (default: 512Mi).

--cpu-util: Target CPU utilization for HPA (default: 80).

--mem-util: Target memory utilization for HPA (default: 80).

--svc-port: Port for the service (default: 80).

--container-port: Port for the container (default: 8080).

Functions

connect_to_k8s_cluster(k8s_config=None)

Connects to a Kubernetes cluster using the specified kubeconfig file or the default configuration.

setup_helm()

Checks if Helm is installed. If not, installs Helm version 3.9.0.

deploy_keda()

Deploys KEDA using Helm.

verify_keda_deployment()

Verifies that the KEDA operator is running.

create_k8s_deployment(namespace, app_name, image, version, cpu_req, mem_req, cpu_lim, mem_lim)

Creates a Kubernetes Deployment for the specified application with resource constraints.

create_horizontal_pod_autoscaler(namespace, app_name, cpu_util, mem_util)

Sets up an HPA for the deployment to scale based on CPU and memory utilization.

monitor_deployment(namespace, app_name)

Monitors the deployment status and retries up to 4 times if it is not healthy.

expose_deployment(namespace, app_name, service_kind="NodePort", svc_port=80, container_port=8080)

Exposes the application using a Kubernetes Service of the specified type.

Example

python k8s_automation.py --namespace my-namespace --app-name my-app \
    --image my-image --version 1.0.0 \
    --cpu-req 200m --mem-req 256Mi \
    --cpu-lim 1 --mem-lim 1Gi \
    --cpu-util 75 --mem-util 75 \
    --svc-port 8080 --container-port 8080

Logging

The script uses Python’s logging module to provide real-time feedback:

INFO: Indicates successful operations.

ERROR: Indicates failure in critical operations.

WARNING: Highlights potential issues.

Notes

Ensure the Kubernetes cluster is accessible from your machine.

Modify the script to customize resource settings or add additional functionality as needed.

Troubleshooting

Kubernetes Cluster Connection Failure:
Ensure kubectl is configured correctly and can access the cluster.

Helm Installation Issues:
Check network connectivity and permissions for installing software.

Deployment Errors:
Review the deployment and service manifests for correctness.

HPA Configuration Issues:
Verify that the Metrics Server is installed and running in the cluster.
