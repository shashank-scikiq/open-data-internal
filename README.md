# Secret Key Setting

## create k8 secret

```cmd
kubectl create secret generic ondc-open-data-webapp-secret --from-literal=db_password=********
```

```cmd
kubectl create secret generic ondc-open-data-webapp-aws-secret --from-literal=AWS_ACCESS_KEY=********* -n ondc-open-data
```

```cmd
kubectl create secret generic ondc-open-data-webapp-aws-secret-key --from-literal=AWS_SECRET_KEY=****** -n ondc-open-data
```

```cmd
kubectl create secret generic app-secret-key --from-literal=APP_SECRET_KEY=********* -n ondc-open-data
```


[![Deploy on EC2 dev_4](https://github.com/shashank-scikiq/open-data-internal/actions/workflows/ec2_deploymeny.yaml/badge.svg?branch=dev_4)](https://github.com/shashank-scikiq/open-data-internal/actions/workflows/ec2_deploymeny.yaml)