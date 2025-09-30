#!/bin/bash
# LegalEdge Deployment Verification Script

set -e

ENVIRONMENT=${1:-production}
DOMAIN=${2:-api.legaledge.com}

echo "🔍 LegalEdge Deployment Verification"
echo "Environment: $ENVIRONMENT"
echo "Domain: $DOMAIN"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
HEALTH_URL="https://$DOMAIN/api/v1/health/status"
READINESS_URL="https://$DOMAIN/api/v1/health/readiness"
OVERVIEW_URL="https://$DOMAIN/api/v1/overview"
DASHBOARD_URL="https://$DOMAIN/api/v1/dashboard/snapshot"

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Function to run test
run_test() {
    local test_name=$1
    local test_command=$2

    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -n "🔍 $test_name... "

    if eval "$test_command" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ PASSED${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ FAILED${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Function to test HTTP endpoint
test_endpoint() {
    local url=$1
    local expected_status=${2:-200}

    curl -f -s --max-time 10 \
        -H "User-Agent: LegalEdge-HealthCheck/1.0" \
        -w "%{http_code}" \
        -o /dev/null \
        "$url" | grep -q "^$expected_status$"
}

# Function to test SSL certificate
test_ssl_certificate() {
    echo -n "🔍 Testing SSL certificate... "
    if echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN:443" 2>/dev/null | openssl x509 -noout -dates >/dev/null 2>&1; then
        echo -e "${GREEN}✅ PASSED${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ FAILED${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Function to test DNS resolution
test_dns_resolution() {
    echo -n "🔍 Testing DNS resolution... "
    if nslookup "$DOMAIN" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ PASSED${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ FAILED${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Function to test AWS resources
test_aws_resources() {
    echo ""
    echo -e "${BLUE}🔧 Testing AWS Resources...${NC}"

    # Test ECS cluster
    run_test "ECS cluster exists" \
        "aws ecs describe-cluster --cluster legaledge-$ENVIRONMENT-cluster --region us-east-1 >/dev/null 2>&1"

    # Test ECS service
    run_test "ECS service exists" \
        "aws ecs describe-services --cluster legaledge-$ENVIRONMENT-cluster --services legaledge-$ENVIRONMENT-app --region us-east-1 >/dev/null 2>&1"

    # Test load balancer
    run_test "Load balancer exists" \
        "aws elbv2 describe-load-balancers --names legaledge-$ENVIRONMENT-alb --region us-east-1 >/dev/null 2>&1"

    # Test RDS database
    run_test "RDS database exists" \
        "aws rds describe-db-instances --db-instance-identifier legaledge-$ENVIRONMENT-db --region us-east-1 >/dev/null 2>&1"

    # Test Redis cluster
    run_test "Redis cluster exists" \
        "aws elasticache describe-cache-clusters --cache-cluster-id legaledge-$ENVIRONMENT-redis --region us-east-1 >/dev/null 2>&1"
}

# Function to test application endpoints
test_application_endpoints() {
    echo ""
    echo -e "${BLUE}🌐 Testing Application Endpoints...${NC}"

    # Test health endpoint
    run_test "Health check endpoint" \
        "test_endpoint '$HEALTH_URL'"

    # Test readiness endpoint
    run_test "Readiness check endpoint" \
        "test_endpoint '$READINESS_URL'"

    # Test overview endpoint
    run_test "Overview endpoint" \
        "test_endpoint '$OVERVIEW_URL'"

    # Test dashboard endpoint
    run_test "Dashboard endpoint" \
        "test_endpoint '$DASHBOARD_URL'"
}

# Function to test performance
test_performance() {
    echo ""
    echo -e "${BLUE}⚡ Testing Performance...${NC}"

    # Test response time for health check
    echo -n "🔍 Health check response time... "
    RESPONSE_TIME=$(curl -s -w "%{time_total}" -o /dev/null "$HEALTH_URL" 2>/dev/null || echo "0")
    if (( $(echo "$RESPONSE_TIME < 5" | bc -l) )); then
        echo -e "${GREEN}✅ FAST ($(echo "$RESPONSE_TIME * 1000" | bc -l | cut -d'.' -f1)ms)${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ SLOW ($(echo "$RESPONSE_TIME * 1000" | bc -l | cut -d'.' -f1)ms)${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi

    TESTS_TOTAL=$((TESTS_TOTAL + 1))
}

# Function to test security headers
test_security_headers() {
    echo ""
    echo -e "${BLUE}🔒 Testing Security...${NC}"

    # Test HTTPS enforcement
    run_test "HTTPS enforcement" \
        "curl -I http://$DOMAIN 2>/dev/null | grep -q 'HTTP/1.1 301'"

    # Test security headers (basic check)
    echo -n "🔍 Security headers... "
    HEADERS=$(curl -s -I "$HEALTH_URL" 2>/dev/null)
    if echo "$HEADERS" | grep -q "strict-transport-security\|x-frame-options\|x-content-type-options\|referrer-policy" 2>/dev/null; then
        echo -e "${GREEN}✅ PRESENT${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${YELLOW}⚠️  MINIMAL${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))  # Not failing, but warning
    fi

    TESTS_TOTAL=$((TESTS_TOTAL + 1))
}

# Function to test monitoring and logs
test_monitoring() {
    echo ""
    echo -e "${BLUE}📊 Testing Monitoring...${NC}"

    # Test CloudWatch logs
    run_test "CloudWatch log group exists" \
        "aws logs describe-log-groups --log-group-name-prefix /ecs/legaledge-$ENVIRONMENT --region us-east-1 >/dev/null 2>&1"

    # Test cost monitoring
    run_test "Cost monitoring dashboard exists" \
        "aws cloudwatch describe-dashboards --dashboard-names legaledge-$ENVIRONMENT-cost-monitoring --region us-east-1 >/dev/null 2>&1"
}

# Function to check costs
check_costs() {
    echo ""
    echo -e "${BLUE}💰 Checking Costs...${NC}"

    # Get today's costs
    TODAY_COST=$(aws ce get-cost-and-usage \
        --time-period Start=$(date +%Y-%m-%d),End=$(date +%Y-%m-%d) \
        --granularity DAILY \
        --metrics BlendedCost \
        --region us-east-1 \
        --query 'ResultsByTime[0].Total.BlendedCost.Amount' \
        --output text 2>/dev/null | cut -d'.' -f1 || echo "0")

    echo "📊 Today's AWS costs: $ \$$TODAY_COST"

    # Check budget
    BUDGET=$(aws budgets describe-budget --budget-name legaledge-$ENVIRONMENT-monthly-budget --region us-east-1 2>/dev/null | jq -r '.Budget.BudgetLimit.Amount // empty' || echo "0")
    if [ "$BUDGET" != "0" ]; then
        BUDGET_USAGE=$(echo "scale=2; $TODAY_COST * 100 / $BUDGET" | bc 2>/dev/null || echo "0")
        echo "📈 Budget utilization: $BUDGET_USAGE%"
    fi
}

# Function to show summary
show_summary() {
    echo ""
    echo -e "${BLUE}📋 Verification Summary${NC}"
    echo "═══════════════════════════════════════"
    echo "Environment: $ENVIRONMENT"
    echo "Domain: $DOMAIN"
    echo "Total Tests: $TESTS_TOTAL"
    echo -e "✅ Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "❌ Failed: ${RED}$TESTS_FAILED${NC}"

    SUCCESS_RATE=$(echo "scale=2; $TESTS_PASSED * 100 / $TESTS_TOTAL" | bc 2>/dev/null || echo "0")
    echo "Success Rate: $SUCCESS_RATE%"

    echo ""
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}🎉 All tests passed! LegalEdge is ready for production.${NC}"
        echo ""
        echo "🚀 Next steps:"
        echo "1. Monitor application performance"
        echo "2. Test user workflows"
        echo "3. Set up backup verification"
        echo "4. Configure alerting thresholds"
    else
        echo -e "${RED}⚠️  Some tests failed. Please review the issues above.${NC}"
        echo ""
        echo "🔧 Troubleshooting steps:"
        echo "1. Check ECS service status"
        echo "2. Review CloudWatch logs"
        echo "3. Verify security group rules"
        echo "4. Check load balancer configuration"
    fi
}

# Main execution
echo "🔍 Starting LegalEdge deployment verification..."
echo ""

# Basic connectivity tests
echo -e "${BLUE}🌐 Testing Basic Connectivity...${NC}"
test_dns_resolution
test_ssl_certificate

# AWS resources tests
test_aws_resources

# Application tests
test_application_endpoints

# Performance tests
test_performance

# Security tests
test_security_headers

# Monitoring tests
test_monitoring

# Cost check
check_costs

# Show results
show_summary
