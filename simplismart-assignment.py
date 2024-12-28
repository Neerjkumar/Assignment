import subprocess
import logging
import sys
import time
import argparse
from kubernetes import config

# Set up logging
logging.basicConfig(level=logging.INFO)

def connect_to_k8s_cluster(k8s_config=None):
    try:
        if k8s_config:
            config.load_kube_config(config_file=k8s_config)
        else:
            config.load_kube_config()
        logging.info("Successfully connected to Kubernetes cluster.")
    except Exception as err:
        logging.error(f"Failed to connect to cluster: {str(err)}")
        sys.exit(1)

def setup_helm():
    try:
        subprocess.check_call(['helm', 'version'])
        logging.info("Helm is already installed.")
    except FileNotFoundError:
        logging.info("Helm not found. Installing Helm...")
        try:
            subprocess.check_call(['curl', '-fsSL', 'https://get.helm.sh/helm-v3.9.0-linux-amd64.tar.gz', '-o', 'helm-v3.9.0-linux-amd64.tar.gz'])
            subprocess.check_call(['tar', '-zxvf', 'helm-v3.9.0-linux-amd64.tar.gz'])
            subprocess.check_call(['sudo', 'mv', 'linux-amd64/helm', '/usr/local/bin/helm'])
            subprocess.check_call(['rm', '-rf', 'helm-v3.9.0-linux-amd64.tar.gz', 'linux-amd64'])
            subprocess.check_call(['helm', 'version'])
            logging.info("Helm installed successfully.")
        except subprocess.CalledProcessError as err:
            logging.error(f"Error occurred during Helm installation: {str(err)}")
            sys.exit(1)

def deploy_keda():
    try:
        subprocess.check_call(['helm', 'repo', 'add', 'keda', 'https://kedacore.github.io/charts'])
        subprocess.check_call(['helm', 'repo', 'update'])
        subprocess.check_call(['helm', 'install', 'keda', 'keda/keda'])
        logging.info("KEDA installed successfully.")
    except subprocess.CalledProcessError as err:
        logging.error(f"Failed to install KEDA: {str(err)}")
        sys.exit(1)

def verify_keda_deployment():
    try:
        keda_pods_output = subprocess.check_output(['kubectl', 'get', 'pods'])
        if 'keda-operator' in str(keda_pods_output):
            logging.info("KEDA operator is running.")
        else:
            logging.error("KEDA operator is not running.")
            sys.exit(1)
    except subprocess.CalledProcessError as err:
        logging.error(f"Error verifying KEDA installation: {str(err)}")
        sys.exit(1)

def create_k8s_deployment(namespace, app_name, image, version, cpu_req, mem_req, cpu_lim, mem_lim):
    deployment_manifest = f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {app_name}
  namespace: {namespace}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {app_name}
  template:
    metadata:
      labels:
        app: {app_name}
    spec:
      containers:
      - name: {app_name}
        image: {image}:{version}
        resources:
          requests:
            memory: {mem_req}
            cpu: {cpu_req}
          limits:
            memory: {mem_lim}
            cpu: {cpu_lim}
        ports:
        - containerPort: 8080
    """
    try:
        subprocess.run(['kubectl', 'apply', '-f', '-', '--namespace', namespace],
                       input=deployment_manifest,
                       text=True,
                       check=True)
        logging.info(f"Deployment {app_name} created successfully.")
    except subprocess.CalledProcessError as err:
        logging.error(f"Failed to create deployment {app_name}: {err}")
        sys.exit(1)

def create_horizontal_pod_autoscaler(namespace, app_name, cpu_util, mem_util):
    hpa_manifest = f"""
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {app_name}-hpa
  namespace: {namespace}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {app_name}
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: {cpu_util}
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: {mem_util}
    """
    try:
        subprocess.run(['kubectl', 'apply', '-f', '-', '--namespace', namespace],
                       input=hpa_manifest,
                       text=True,
                       check=True)
        logging.info(f"HPA for {app_name} created successfully.")
    except subprocess.CalledProcessError as err:
        logging.error(f"Failed to create HPA for {app_name}: {err}")
        sys.exit(1)

def monitor_deployment(namespace, app_name):
    try:
        status = subprocess.check_output(['kubectl', 'get', 'deployment', app_name, '-n', namespace, '-o', 'jsonpath={.status.conditions[?(@.type=="Available")].status}'])
        retries = 0
        while status != b'True' and retries < 4:
            time.sleep(10)
            status = subprocess.check_output(['kubectl', 'get', 'deployment', app_name, '-n', namespace, '-o', 'jsonpath={.status.conditions[?(@.type=="Available")].status}'])
            retries += 1
            logging.info("Retrying deployment status check...")

        if status != b'True':
            logging.warning(f"Deployment {app_name} is not healthy.")
        else:
            logging.info(f"Deployment {app_name} is healthy.")
    except subprocess.CalledProcessError as err:
        logging.error(f"Error checking deployment status: {str(err)}")
        sys.exit(1)

def expose_deployment(namespace, app_name, service_kind="NodePort", svc_port=80, container_port=8080):
    service_manifest = f"""
apiVersion: v1
kind: Service
metadata:
  name: {app_name}-svc
  namespace: {namespace}
spec:
  selector:
    app: {app_name}
  type: {service_kind}
  ports:
    - protocol: TCP
      port: {svc_port}
      targetPort: {container_port}
    """
    try:
        subprocess.run(['kubectl', 'apply', '-f', '-', '--namespace', namespace],
                       input=service_manifest,
                       text=True,
                       check=True)
        logging.info(f"Service {app_name}-svc created successfully.")
    except subprocess.CalledProcessError as err:
        logging.error(f"Failed to create service for {app_name}: {err}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kubernetes deployment automation.")
    parser.add_argument('--namespace', required=True, help="Namespace for the deployment")
    parser.add_argument('--app-name', required=True, help="Name of the application")
    parser.add_argument('--image', required=True, help="Container image for the application")
    parser.add_argument('--version', required=True, help="Version of the container image")
    parser.add_argument('--cpu-req', default="100m", help="CPU requests for the application")
    parser.add_argument('--mem-req', default="128Mi", help="Memory requests for the application")
    parser.add_argument('--cpu-lim', default="500m", help="CPU limits for the application")
    parser.add_argument('--mem-lim', default="512Mi", help="Memory limits for the application")
    parser.add_argument('--cpu-util', type=int, default=80, help="Target CPU utilization for HPA")
    parser.add_argument('--mem-util', type=int, default=80, help="Target memory utilization for HPA")
    parser.add_argument('--svc-port', type=int, default=80, help="Port for the service")
    parser.add_argument('--container-port', type=int, default=8080, help="Port for the container")

    args = parser.parse_args()

    connect_to_k8s_cluster()
    setup_helm()
    deploy_keda()
    verify_keda_deployment()

    create_k8s_deployment(args.namespace, args.app_name, args.image, args.version, args.cpu_req, args.mem_req, args.cpu_lim, args.mem_lim)
    create_horizontal_pod_autoscaler(args.namespace, args.app_name, args.cpu_util, args.mem_util)
    monitor_deployment(args.namespace, args.app_name)
    expose_deployment(args.namespace, args.app_name, "NodePort", args.svc_port, args.container_port)
