cluster-create:
	k3d cluster create guardian

cluster-delete:
	k3d cluster delete guardian

cluster-info:
	kubectl cluster-info

pods:
	kubectl get pods -A
