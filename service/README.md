## Итоговый проект

### Тестирование приложения в контейнере (все элементы будут протестированы в том же окружении, в котором будет запущен CI/CD)

1) Собираем образ

        docker build -t model_service -f Dockerfile .

2) Запускаем контейнер для локального тестирования (в качестве переменных окружения передаем секреты для S3, XXX, YYY, ZZZ заменить)

        docker run --name model_service -it --rm -p 80:80 --env aws_access_key_id=XXX --env aws_secret_access_key=YYY --env region=ZZZ model_service

3) Запустить клиент для тестирования

        python3 client.py --host 127.0.0.1 --port 80

### Отправка образа в Docker Hub

1) Залогиниться (ввести пароль или токен)

        docker login -u dmitry030309

2) Создать репозиторий на Docker Hub (project_model)

3) Сделать ссылку на необходимый образ с изменением его названия

        docker tag model_service:latest dmitry030309/project_model:latest

4) Отправить образ в репозиторий

        docker push dmitry030309/project_model:latest

5) Для автоматизированного CD не забыть добавить секреты в GitHub для доступа к DockerHub

### Проверка CI/CD

1) Делаем push в репозиторий

2) В GitHub Actions видим успешные workflows

3) В DockerHub видим обновленную версию контейнера

### Разворачиваем кластер K8S в YC с названием mykuber, создаем группу узлов с названием mynodes

1) Пользуемся инструкцией для развертывания и настройки кластера https://cloud.yandex.ru/docs/managed-kubernetes/quickstart

- необходимо установить и настроить утилиту yc (https://cloud.yandex.ru/docs/cli/quickstart#install)
- необходимо установить и настроить утилиту kubectl (https://kubernetes.io/ru/docs/tasks/tools/install-kubectl/)

- CIDR кластера 192.168.0.0/23
- CIDR сервисов 192.168.8.0/23
- Маска подсети узлов 27
- Макс. кол-во узлов 8
- Макс. кол-во подов в узле 16
  
2) Обновляем конфигурационный файл (~/.kube/config)

        yc managed-kubernetes cluster get-credentials mykuber --external --force

3) Проверяем, что утилита kubectl связалась с кластером mykuber

        kubectl config view

Если узлы не будут долго создаваться (более 15 минут), возможно, превышен лимит по ресурсам.
Надо проверять, что не превышено максимальное количество подов (задается при создании кластера путем применения маски подсети)

4) Создаем секреты, которые будут передаваться контейнерам при создании deployment (XXX, YYY, ZZZ заменить)

        kubectl create secret generic for-boto3 \
        --from-literal=aws_access_key_id=XXX \
        --from-literal=aws_secret_access_key=YYY \
        --from-literal=region=ZZZ

5) Проверяем, что секреты создались

        kubectl describe secret for-boto3

### Запускаем сервис

Если будут ошибки, иногда помогает перезапуск командной оболочки.

1) Запускаем манифесты на кластере

        cd ~/work/MLOps_plus/mlops_k8s_homework
        kubectl apply -f k8s/deployment.yml

    Доступность внутри k8s
        kubectl apply -f k8s/service.yml

    Доступность за пределами k8s
        kubectl apply -f k8s/load-balancer.yaml

2) Проверяем что все запустилось

        kubectl get deployments
        kubectl get service

3) Проверим, что секреты попали внутрь контейнеров

        kubectl get pod
        kubectl exec -it model-deployment-d67f87df6-htk4f bash
        echo $aws_access_key_id

### Проверка работоспособности через внешний IP

На основе примера https://cloud.yandex.ru/docs/managed-kubernetes/operations/create-load-balancer#lb-create

1) Находим EXTERNAL-IP для model-service-out

        kubectl get services

2) Тестируем приложение

        python3 service/client.py -host 51.250.70.250 -port 80

3) Редеплой можно сделать этой командой (но сервисы некоторое время будут недоступны)

        kubectl replace --force -f k8s/deployment.yml

### Настройка мониторинга

1) Создаем отдельное пространство имен для мониторинга и переключаемся на него
    
        kubectl create namespace monitoring
        kubectl config set-context --current --namespace=monitoring

2) Устанавливаем prometeus
   
        helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
        helm repo update
        helm install v2 prometheus-community/kube-prometheus-stack

3) Пробрасываем порт graphana на локальный помпьютер

        kubectl port-forward service/v2-grafana 8080:80

4) Подключаемся в веб-интерфейсу

    127.0.0.1:8080
    admin
    prom-operator