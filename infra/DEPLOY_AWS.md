# Deploying to AWS

A condensed guide for ECS Fargate deployment.

## Prerequisites
- AWS CLI configured
- An AWS account with permissions for ECS, ECR, RDS, ElastiCache, Secrets Manager, IAM

## Steps

### 1. Create ECR repository and push image

```bash
aws ecr create-repository --repository-name aiops-agent
aws ecr get-login-password --region REGION | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com

docker build -t aiops-agent .
docker tag aiops-agent:latest ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/aiops-agent:latest
docker push ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/aiops-agent:latest
```

### 2. Create RDS Postgres

Use the AWS Console or CLI to create a `db.t4g.micro` Postgres 16 instance in a private subnet.

### 3. Create ElastiCache Redis

A single-node `cache.t4g.micro` Redis cluster suffices for dev.

### 4. Store secrets

```bash
aws secretsmanager create-secret --name aiops/openai --secret-string "sk-..."
aws secretsmanager create-secret --name aiops/slack --secret-string "https://hooks.slack.com/..."
```

### 5. Edit `ecs-task-definition.json`

Replace `ACCOUNT_ID`, `REGION`, `RDS_ENDPOINT`, `ELASTICACHE_ENDPOINT`, and secret ARNs.

### 6. Register the task and create the service

```bash
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json
aws ecs create-cluster --cluster-name aiops
aws ecs create-service \
  --cluster aiops \
  --service-name aiops-agent \
  --task-definition aiops-agent \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

### 7. Put an ALB in front

Create an Application Load Balancer pointing at the ECS service on port 8000 with a target group health check on `/health`.

### 8. CloudWatch

Logs land in `/ecs/aiops-agent`. Set up metric filters on `ERROR` and `Pipeline failed` for alerting.
