cluster-create:
	k3d cluster create guardian

cluster-delete:
	k3d cluster delete guardian

cluster-info:
	kubectl cluster-info

pods:
	kubectl get pods -A

incident:

	@./ops/collect-incident.sh
	@LATEST=$$(ls -td incidents/20* | head -1); \
	echo "Analizuję: $$LATEST"; \
	python3 ops/analyze-incident.py "$$LATEST"; \
	echo ""; \
	echo "Raport:"; \
	echo "$$LATEST/incident-report.md"
