
build:
	docker build --build-arg app=app -f Dockerfile -t $(SERVICE):$(VERSION) .

push:
	docker tag $(SERVICE):$(VERSION) registry.sphinx-repo.epu-ntua/sphinx-project/vulnerability-assessment/vaaas-docker/$(SERVICE):$(VERSION)
	docker push registry.sphinx-repo.epu-ntua/sphinx-project/vulnerability-assessment/vaaas-docker/$(SERVICE):$(VERSION)


build-push:	build	push
