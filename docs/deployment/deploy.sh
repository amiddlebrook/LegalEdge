#!/bin/bash
# LegalEdge Infrastructure Deployment Script

set -e

ENVIRONMENT=${1:-production}
ACTION=${2:-apply}

echo "🏗️  LegalEdge Infrastructure Deployment"
echo "Environment: $ENVIRONMENT"
echo "Action: $ACTION"
echo ""

# Check prerequisites
command -v terraform >/dev/null 2>&1 || { echo "❌ Terraform is required but not installed."; exit 1; }
command -v aws >/dev/null 2>&1 || { echo "❌ AWS CLI is required but not installed."; exit 1; }

# Check if terraform.tfvars exists
if [ ! -f "terraform.tfvars" ]; then
    echo "❌ terraform.tfvars not found!"
    echo "Please copy terraform.tfvars.example to terraform.tfvars and update the values."
    exit 1
fi

# Function to check AWS credentials
check_aws_creds() {
    echo "🔍 Checking AWS credentials..."
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        echo "❌ AWS credentials not configured or invalid"
        echo "Please run: aws configure"
        exit 1
    fi
    echo "✅ AWS credentials configured"
}

# Function to initialize Terraform
init_terraform() {
    echo "🔧 Initializing Terraform..."
    terraform init
    echo "✅ Terraform initialized"
}

# Function to validate Terraform configuration
validate_config() {
    echo "🔍 Validating Terraform configuration..."
    if ! terraform validate; then
        echo "❌ Terraform validation failed"
        exit 1
    fi
    echo "✅ Terraform configuration valid"
}

# Function to plan deployment
plan_deployment() {
    echo "📋 Planning Terraform deployment..."
    terraform plan -var="environment=$ENVIRONMENT" -out=tfplan
    echo "✅ Deployment plan created"
    echo ""
    echo "📋 Deployment Plan Summary:"
    terraform show -json tfplan | jq '.planned_actions | {create: .create, update: .update, delete: .delete}'
}

# Function to apply deployment
apply_deployment() {
    echo "🚀 Applying Terraform deployment..."
    echo ""
    echo "⚠️  This will create real AWS resources and incur costs!"
    read -p "Continue with deployment? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Deployment cancelled"
        exit 0
    fi

    terraform apply -auto-approve tfplan
    echo "✅ Infrastructure deployment completed!"
}

# Function to show outputs
show_outputs() {
    echo ""
    echo "📋 Deployment Outputs:"
    terraform output
    echo ""
    echo "💾 Save these values for application deployment:"
    terraform output -json | jq -r '. | to_entries[] | "\(.key)=\(.value.value)"'
}

# Function to deploy application
deploy_application() {
    echo ""
    echo "🐳 Deploying application to ECS..."
    echo "Make sure your Docker images are built and pushed to your registry first."
    echo ""
    read -p "Continue with application deployment? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
        # Update ECS service with new image
        echo "🔄 Updating ECS service..."
        aws ecs update-service --cluster legaledge-$ENVIRONMENT-cluster \
            --service legaledge-$ENVIRONMENT-app --force-new-deployment

        echo "⏳ Waiting for deployment to complete..."
        aws ecs wait services-stable --cluster legaledge-$ENVIRONMENT-cluster \
            --service legaledge-$ENVIRONMENT-app

        echo "✅ Application deployment completed!"
    fi
}

# Main execution
cd infrastructure

echo "🔐 Step 1: Checking prerequisites..."
check_aws_creds

echo ""
echo "🏗️  Step 2: Infrastructure deployment..."
init_terraform
validate_config

if [ "$ACTION" = "plan" ]; then
    plan_deployment
    echo ""
    echo "💡 Run with './deploy.sh $ENVIRONMENT apply' to deploy"
elif [ "$ACTION" = "apply" ]; then
    plan_deployment
    apply_deployment
    show_outputs
    deploy_application
else
    echo "❌ Invalid action. Use 'plan' or 'apply'"
    exit 1
fi

echo ""
echo "🎉 LegalEdge infrastructure deployment completed!"
echo ""
echo "Next steps:"
echo "1. Verify the deployment with health checks"
echo "2. Test the application endpoints"
echo "3. Set up monitoring and alerts"
echo "4. Configure DNS (if using custom domain)"
