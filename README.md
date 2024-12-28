# Kubernetes Deployment Automation Tool

This script automates the deployment of Kubernetes applications, setting up Helm, installing KEDA (Kubernetes Event-driven Autoscaler), and managing the deployment lifecycle, including monitoring and exposing services.

## Features

- **Kubernetes Cluster Connection**: Automatically connects to a Kubernetes cluster using a kubeconfig file.
- **Helm Setup**: Installs Helm if not already installed.
- **KEDA Deployment**: Installs KEDA for autoscaling workloads.
- **Application Deployment**: Deploys a Kubernetes application with configurable resource requests and limits.
- **Horizontal Pod Autoscaler (HPA)**: Sets up HPA for CPU and memory-based scaling.
- **Deployment Monitoring**: Verifies the health of the deployment.
- **Service Exposure**: Exposes the application using a Kubernetes Service.

## Prerequisites

- **Python**: Version 3.6 or higher.
- **kubectl**: Installed and configured.
- **Helm**: Version 3.x installed (or installable via the script).
- **Kubernetes Cluster**: Access configured via `~/.kube/config` or a specified kubeconfig file.
- **Python Libraries**:
  - `kubernetes`

Install the required Python dependencies with:

```bash
pip install kubernetes
